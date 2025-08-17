"""
Twilio Service
Handles phone call integration with Twilio for AI voice agent
"""

import logging
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime
import json
from functools import wraps
import time

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse

from app.core.config import settings
from app.models.call import Call
from app.services.voice_agent import voice_agent_service


logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry failed operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


class TwilioService:
    """Service for handling Twilio phone call integration"""
    
    def __init__(self):
        self.client = None
        self.is_configured = False
        self._config_errors = []
        
        # Validate configuration
        self._validate_configuration()
        
        # Initialize Twilio client if credentials are available
        if self.is_configured:
            try:
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("Twilio client initialized successfully")
                
                # Test the client with a simple API call
                self._test_client_connection()
                
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.is_configured = False
                self._config_errors.append(f"Client initialization failed: {e}")
    
    def _validate_configuration(self):
        """Validate Twilio configuration and collect errors"""
        missing_configs = []
        
        if not settings.TWILIO_ACCOUNT_SID:
            missing_configs.append("TWILIO_ACCOUNT_SID")
        elif not settings.TWILIO_ACCOUNT_SID.startswith('AC'):
            self._config_errors.append("TWILIO_ACCOUNT_SID should start with 'AC'")
            
        if not settings.TWILIO_AUTH_TOKEN:
            missing_configs.append("TWILIO_AUTH_TOKEN")
            
        if not settings.TWILIO_PHONE_NUMBER:
            missing_configs.append("TWILIO_PHONE_NUMBER")
        elif not settings.TWILIO_PHONE_NUMBER.startswith('+'):
            self._config_errors.append("TWILIO_PHONE_NUMBER should start with '+'")
        
        if missing_configs:
            self._config_errors.append(f"Missing required configuration: {', '.join(missing_configs)}")
            logger.warning(f"Twilio configuration incomplete: {', '.join(missing_configs)}")
        else:
            self.is_configured = True
    
    def _test_client_connection(self):
        """Test Twilio client connection"""
        try:
            # Simple API call to verify credentials
            account = self.client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
            logger.info(f"Twilio client connected successfully. Account: {account.friendly_name}")
        except Exception as e:
            logger.warning(f"Twilio client connection test failed: {e}")
            # Don't mark as unconfigured since credentials might be valid but API temporarily unavailable
    
    @retry_on_failure(max_retries=2, delay=1.0)
    async def make_outbound_call(
        self, 
        to_number: str, 
        tenant_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Make an outbound call using Twilio"""
        
        # Validate inputs
        if not to_number or not tenant_id:
            raise ValueError("to_number and tenant_id are required")
        
        # Validate phone number format
        if not to_number.startswith('+') or len(to_number) < 10:
            raise ValueError("Invalid phone number format. Must start with '+' and be at least 10 digits")
        
        if not self.is_configured:
            raise HTTPException(
                status_code=500,
                detail="Twilio is not configured. Please check your environment variables."
            )
        
        try:
            # Create call record
            call_id = await self._create_call_record(to_number, tenant_id, "outbound", db)
            
            # Make the call via Twilio
            call = self.client.calls.create(
                to=to_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                url=f"{settings.BASE_URL}/api/v1/voice/twilio/webhook/{call_id}",
                status_callback=f"{settings.BASE_URL}/api/v1/voice/twilio/status/{call_id}",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )
            
            logger.info(f"Outbound call initiated: {call.sid} to {to_number}")
            
            return {
                "call_id": call_id,
                "twilio_sid": call.sid,
                "status": "initiated",
                "to_number": to_number,
                "from_number": settings.TWILIO_PHONE_NUMBER
            }
            
        except Exception as e:
            logger.error(f"Failed to make outbound call: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initiate call: {str(e)}"
            )
    
    async def handle_incoming_call(
        self, 
        from_number: str,
        to_number: str,
        tenant_id: str,
        db: AsyncSession
    ) -> str:
        """Handle incoming call and return TwiML response with ConversationRelay"""
        
        # Validate inputs
        if not from_number or not tenant_id:
            raise ValueError("from_number and tenant_id are required")
        
        if not self.is_configured:
            logger.error("Twilio service not configured for incoming call")
            response = VoiceResponse()
            response.say("Service temporarily unavailable. Please try again later.")
            return str(response)
        
        try:
            # Create call record
            call_id = await self._create_call_record(from_number, tenant_id, "inbound", db)
            
            # Start AI conversation
            context = await voice_agent_service.start_conversation(
                call_id, tenant_id, from_number, db
            )
            
            # Generate TwiML response for ConversationRelay
            response = VoiceResponse()
            
            # Set up Twilio ConversationRelay for real-time AI voice conversations
            connect = response.connect()
            
            # Build WebSocket URL properly
            parsed_url = urlparse(settings.BASE_URL)
            ws_scheme = "wss" if parsed_url.scheme == "https" else "ws"
            ws_url = f"{ws_scheme}://{parsed_url.netloc}/api/v1/voice/conversation-relay/{call_id}"
            
            conversation_relay = connect.conversation_relay(
                url=ws_url,
                voice="Polly.Joanna-Neural"  # Use neural voice for better quality
            )
            
            # Configure ConversationRelay parameters for optimal AI conversation
            conversation_relay.parameter(name="language", value="en-US")
            conversation_relay.parameter(name="speech_timeout", value="3")
            conversation_relay.parameter(name="max_speech_duration", value="30")
            
            logger.info(f"Twilio ConversationRelay configured for call {call_id}")
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Failed to handle incoming call: {e}")
            response = VoiceResponse()
            response.say("I'm sorry, there was an error processing your call. Please try again later.")
            return str(response)
    
    async def handle_call_status_update(
        self, 
        call_id: str, 
        status: str, 
        db: AsyncSession
    ):
        """Handle call status updates from Twilio"""
        
        try:
            # Update call status in database using SQLAlchemy
            from sqlalchemy import select, update
            
            # Update call status
            stmt = update(Call).where(Call.id == call_id).values(
                status=status,
                updated_at=datetime.utcnow()
            )
            result = await db.execute(stmt)
            
            if result.rowcount == 0:
                logger.warning(f"No call found with ID {call_id} for status update")
                return
            
            await db.commit()
            
            # If call ended, end the conversation and calculate duration
            if status in ['completed', 'failed', 'busy', 'no-answer']:
                # Update end time and calculate duration
                call_stmt = select(Call).where(Call.id == call_id)
                call_result = await db.execute(call_stmt)
                call = call_result.scalar_one_or_none()
                
                if call and call.started_at:
                    duration_seconds = int((datetime.utcnow() - call.started_at).total_seconds())
                    
                    end_stmt = update(Call).where(Call.id == call_id).values(
                        ended_at=datetime.utcnow(),
                        duration_seconds=duration_seconds
                    )
                    await db.execute(end_stmt)
                    await db.commit()
                
                # End the conversation
                await voice_agent_service.end_conversation(call_id, db)
                
                # Generate call summary
                await self._generate_call_summary(call_id, db)
            
            logger.info(f"Call {call_id} status updated to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update call status: {e}")
            await db.rollback()
    
    async def _create_call_record(
        self, 
        phone_number: str, 
        tenant_id: str, 
        direction: str,
        db: AsyncSession
    ) -> str:
        """Create a call record in the database"""
        
        import uuid
        call_id = str(uuid.uuid4())
        
        call = Call(
            id=call_id,
            tenant_id=tenant_id,
            caller_number=phone_number,
            status="initiated",
            started_at=datetime.utcnow(),
            direction=direction
        )
        
        db.add(call)
        await db.commit()
        
        return call_id
    
    async def _generate_call_summary(self, call_id: str, db: AsyncSession):
        """Generate a summary of the completed call"""
        
        try:
            # Get call transcripts
            from app.models.call import CallTranscript
            from sqlalchemy import select
            
            stmt = select(CallTranscript).where(
                CallTranscript.call_id == call_id
            ).order_by(CallTranscript.timestamp.asc())
            
            result = await db.execute(stmt)
            transcripts = result.scalars().all()
            
            if not transcripts:
                return
            
            # Create summary from conversation
            conversation_text = " ".join([
                f"{t.speaker}: {t.text}" for t in transcripts
            ])
            
            # Use OpenAI to generate summary
            summary = await voice_agent_service._generate_call_summary_from_text(
                conversation_text
            )
            
            # Update call record with summary using SQLAlchemy
            from sqlalchemy import update
            
            stmt = update(Call).where(Call.id == call_id).values(
                summary=summary
            )
            await db.execute(stmt)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to generate call summary: {e}")
    
    def is_available(self) -> bool:
        """Check if Twilio service is available"""
        return self.is_configured
    
    def get_configuration_status(self) -> dict:
        """Get detailed configuration status for debugging"""
        return {
            "is_configured": self.is_configured,
            "has_client": self.client is not None,
            "config_errors": self._config_errors,
            "phone_number": settings.TWILIO_PHONE_NUMBER if self.is_configured else None,
            "account_sid": settings.TWILIO_ACCOUNT_SID[:8] + "..." if settings.TWILIO_ACCOUNT_SID else None
        }


# Global instance
twilio_service = TwilioService()