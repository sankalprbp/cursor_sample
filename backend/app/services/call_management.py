"""
Call Management Service
Handles call-related business logic and operations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
import uuid

from app.models.call import Call, CallTranscript
from app.models.tenant import Tenant
from app.models.user import User
from app.services.voice_agent import voice_agent_service
from app.services.mock_data import mock_data_service


logger = logging.getLogger(__name__)


class CallManagementService:
    """Service for managing call operations and data"""
    
    async def create_call_session(
        self,
        caller_number: str,
        tenant_id: str,
        direction: str = "inbound",
        db: AsyncSession = None
    ) -> str:
        """Create a new call session record"""
        
        call_id = str(uuid.uuid4())
        
        call = Call(
            id=call_id,
            tenant_id=tenant_id,
            caller_number=caller_number,
            status="active",
            started_at=datetime.utcnow(),
            direction=direction
        )
        
        db.add(call)
        await db.commit()
        
        logger.info(f"Created call session {call_id} for {caller_number}")
        return call_id
    
    async def get_calls_for_user(
        self,
        user: User,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Get calls accessible to a user with pagination"""
        
        # Build query based on user permissions
        stmt = select(Call).join(Tenant)
        
        if user.role != "super_admin":
            stmt = stmt.where(Tenant.id == user.tenant_id)
        
        if status:
            stmt = stmt.where(Call.status == status)
        
        stmt = stmt.order_by(Call.started_at.desc()).offset(offset).limit(limit)
        
        # Get total count for pagination
        count_stmt = select(Call).join(Tenant)
        if user.role != "super_admin":
            count_stmt = count_stmt.where(Tenant.id == user.tenant_id)
        if status:
            count_stmt = count_stmt.where(Call.status == status)
        
        result = await db.execute(stmt)
        calls = result.scalars().all()
        
        count_result = await db.execute(count_stmt)
        total_calls = len(count_result.scalars().all())
        
        # Convert to response format
        call_summaries = []
        for call in calls:
            call_summaries.append({
                "id": call.id,
                "caller_number": call.caller_number,
                "status": call.status,
                "direction": call.direction or "inbound",
                "started_at": call.started_at.isoformat() if call.started_at else "",
                "ended_at": call.ended_at.isoformat() if call.ended_at else None,
                "duration_seconds": call.duration_seconds,
                "summary": call.summary
            })
        
        return {
            "calls": call_summaries,
            "total": total_calls,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_calls
        }
    
    async def get_call_details(
        self,
        call_id: str,
        user: User,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get detailed call information including transcripts"""
        
        # Get call record
        stmt = select(Call).where(Call.id == call_id)
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()
        
        if not call:
            return None
        
        # Check access permissions
        if user.role != "super_admin" and str(call.tenant_id) != str(user.tenant_id):
            return None
        
        # Get call transcripts
        transcript_stmt = select(CallTranscript).where(
            CallTranscript.call_id == call_id
        ).order_by(CallTranscript.timestamp.asc())
        
        transcript_result = await db.execute(transcript_stmt)
        transcripts = transcript_result.scalars().all()
        
        return {
            "call": {
                "id": call.id,
                "tenant_id": str(call.tenant_id),
                "caller_number": call.caller_number,
                "status": call.status,
                "direction": call.direction,
                "started_at": call.started_at.isoformat() if call.started_at else None,
                "ended_at": call.ended_at.isoformat() if call.ended_at else None,
                "duration_seconds": call.duration_seconds,
                "summary": call.summary
            },
            "transcripts": [
                {
                    "id": str(transcript.id),
                    "speaker": transcript.speaker,
                    "text": transcript.text,
                    "timestamp": transcript.timestamp.isoformat(),
                    "confidence": transcript.confidence
                }
                for transcript in transcripts
            ]
        }
    
    async def update_call_status(
        self,
        call_id: str,
        status: str,
        db: AsyncSession
    ) -> bool:
        """Update call status and handle end-of-call processing"""
        
        try:
            # Update call status
            stmt = update(Call).where(Call.id == call_id).values(
                status=status,
                updated_at=datetime.utcnow()
            )
            result = await db.execute(stmt)
            
            if result.rowcount == 0:
                logger.warning(f"No call found with ID {call_id} for status update")
                return False
            
            # If call ended, perform end-of-call processing
            if status in ['completed', 'failed', 'busy', 'no-answer']:
                await self._handle_call_completion(call_id, db)
            
            await db.commit()
            logger.info(f"Call {call_id} status updated to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update call status: {e}")
            await db.rollback()
            return False
    
    async def _handle_call_completion(self, call_id: str, db: AsyncSession):
        """Handle call completion processing"""
        
        try:
            # Get call record
            call_stmt = select(Call).where(Call.id == call_id)
            call_result = await db.execute(call_stmt)
            call = call_result.scalar_one_or_none()
            
            if call and call.started_at:
                # Calculate duration
                duration_seconds = int((datetime.utcnow() - call.started_at).total_seconds())
                
                # Update end time and duration
                end_stmt = update(Call).where(Call.id == call_id).values(
                    ended_at=datetime.utcnow(),
                    duration_seconds=duration_seconds
                )
                await db.execute(end_stmt)
            
            # End the conversation in voice agent service
            await voice_agent_service.end_conversation(call_id, db)
            
            # Generate call summary (async, don't wait)
            # In production, this might be queued as a background task
            try:
                await self._generate_call_summary(call_id, db)
            except Exception as e:
                logger.warning(f"Failed to generate call summary for {call_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in call completion handling: {e}")
    
    async def _generate_call_summary(self, call_id: str, db: AsyncSession):
        """Generate AI summary of the completed call"""
        
        try:
            # Get call transcripts
            stmt = select(CallTranscript).where(
                CallTranscript.call_id == call_id
            ).order_by(CallTranscript.timestamp.asc())
            
            result = await db.execute(stmt)
            transcripts = result.scalars().all()
            
            if not transcripts:
                return
            
            # Create conversation text
            conversation_text = " ".join([
                f"{t.speaker}: {t.text}" for t in transcripts
            ])
            
            # Generate summary using voice agent service
            summary = await voice_agent_service._generate_call_summary_from_text(
                conversation_text
            )
            
            # Update call record with summary
            stmt = update(Call).where(Call.id == call_id).values(
                summary=summary
            )
            await db.execute(stmt)
            await db.commit()
            
            logger.info(f"Generated summary for call {call_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate call summary: {e}")
    
    async def get_demo_calls(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get demo call data for public endpoints"""
        
        result = mock_data_service.get_mock_calls(limit, offset, status)
        result["demo"] = True
        result["message"] = "This is demo data. Use /calls/authenticated for real data."
        
        return result
    
    async def get_demo_call_detail(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get demo call detail data"""
        
        call = mock_data_service.get_mock_call_by_id(call_id)
        if not call:
            return None
        
        transcripts = mock_data_service.get_mock_transcripts(call_id)
        
        return {
            "call": call,
            "transcripts": transcripts
        }


# Global instance
call_management_service = CallManagementService()