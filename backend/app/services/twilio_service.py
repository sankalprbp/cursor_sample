"""
Twilio Service
Handles phone call integration with Twilio for AI voice agent
"""

import logging
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime
import json

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.call import Call
from app.services.voice_agent import voice_agent_service


logger = logging.getLogger(__name__)


class TwilioService:
    """Service for handling Twilio phone call integration"""
    
    def __init__(self):
        self.client = None
        self.is_configured = False
        
        # Initialize Twilio client if credentials are available
        if (settings.TWILIO_ACCOUNT_SID and 
            settings.TWILIO_AUTH_TOKEN and 
            settings.TWILIO_PHONE_NUMBER):
            try:
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                self.is_configured = True
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.is_configured = False
    
    async def make_outbound_call(
        self, 
        to_number: str, 
        tenant_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Make an outbound call using Twilio"""
        
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
        """Handle incoming call and return TwiML response"""
        
        try:
            # Create call record
            call_id = await self._create_call_record(from_number, tenant_id, "inbound", db)
            
            # Start AI conversation
            context = await voice_agent_service.start_conversation(
                call_id, tenant_id, from_number, db
            )
            
            # Generate TwiML response
            response = VoiceResponse()
            
            # Add initial greeting
            if context.messages:
                greeting = context.messages[-1]["content"]
                response.say(greeting, voice='alice')
            
            # Set up streaming for real-time conversation
            connect = response.connect()
            connect.stream(url=f"{settings.BASE_URL}/api/v1/voice/twilio/stream/{call_id}")
            
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
            # Update call status in database
            stmt = f"""
                UPDATE calls 
                SET status = '{status}', 
                    updated_at = NOW()
                WHERE id = '{call_id}'
            """
            await db.execute(stmt)
            await db.commit()
            
            # If call ended, end the conversation
            if status in ['completed', 'failed', 'busy', 'no-answer']:
                await voice_agent_service.end_conversation(call_id, db)
                
                # Generate call summary
                await self._generate_call_summary(call_id, db)
            
            logger.info(f"Call {call_id} status updated to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update call status: {e}")
    
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
            
            # Update call record with summary
            stmt = f"""
                UPDATE calls 
                SET summary = '{summary}', 
                    ended_at = NOW()
                WHERE id = '{call_id}'
            """
            await db.execute(stmt)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to generate call summary: {e}")
    
    def is_available(self) -> bool:
        """Check if Twilio service is available"""
        return self.is_configured


# Global instance
twilio_service = TwilioService()