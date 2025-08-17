"""
Voice Agent API Endpoints
Handles AI voice agent calls, conversations, and telephony integration
"""

import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Response, WebSocket, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field, validator
import uuid
from datetime import datetime

from app.core.database import get_db
from app.services.auth import auth_service, security
from app.services.voice_agent import voice_agent_service
from app.services.twilio_service import twilio_service
from app.services.conversation_relay import media_stream_handler
from app.models.user import User
from app.models.call import Call
from app.models.tenant import Tenant
from app.services.mock_data import mock_data_service


logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class StartCallRequest(BaseModel):
    caller_number: str
    tenant_id: Optional[str] = None


class CallResponse(BaseModel):
    call_id: str
    status: str
    caller_number: str
    tenant_id: str
    agent_name: str
    started_at: str
    greeting: str


class AudioInputRequest(BaseModel):
    call_id: str
    audio_data: str  # Base64 encoded audio


class TextInputRequest(BaseModel):
    call_id: str
    text: str


class ConversationResponse(BaseModel):
    call_id: str
    transcript: str
    response_text: str
    audio_response: str  # Base64 encoded
    context: dict


class CallSummary(BaseModel):
    """Summary information for a call"""
    id: str
    caller_number: str
    status: str
    direction: str
    started_at: str
    ended_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    summary: Optional[str] = None
    transcript_count: Optional[int] = None
    satisfaction_score: Optional[float] = None


class CallListResponse(BaseModel):
    """Response model for call list endpoints"""
    calls: List[CallSummary]
    total: int
    limit: int
    offset: int
    has_more: bool
    demo: Optional[bool] = None
    message: Optional[str] = None


class CallDetailResponse(BaseModel):
    """Response model for detailed call information"""
    call: CallSummary
    transcripts: List[dict]


class TranscriptEntry(BaseModel):
    """Individual transcript entry"""
    id: str
    speaker: str
    text: str
    timestamp: str
    confidence: float


@router.post("/calls/start", response_model=CallResponse)
async def start_call(
    request: StartCallRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Start a new AI voice agent call
    """
    user = await auth_service.get_current_user(db, credentials)
    
    # Determine tenant
    tenant_id = request.tenant_id if request.tenant_id else user.tenant_id
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID is required"
        )
    
    # Verify user has access to tenant
    if user.role != "super_admin" and str(user.tenant_id) != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to tenant"
        )
    
    # Get tenant info
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Create call record
    call_id = str(uuid.uuid4())
    call = Call(
        id=call_id,
        tenant_id=tenant_id,
        caller_number=request.caller_number,
        status="active",
        started_at=datetime.utcnow(),
        direction="inbound"
    )
    
    db.add(call)
    await db.commit()
    
    # Start voice agent conversation
    try:
        context = await voice_agent_service.start_conversation(
            call_id, tenant_id, request.caller_number, db
        )
        
        # Get the greeting message
        greeting = ""
        if context.messages:
            greeting = context.messages[-1]["content"]
        
        return CallResponse(
            call_id=call_id,
            status="active",
            caller_number=request.caller_number,
            tenant_id=tenant_id,
            agent_name=context.get_context("agent_name", "AI Assistant"),
            started_at=call.started_at.isoformat(),
            greeting=greeting
        )
        
    except Exception as e:
        logger.error(f"Error starting call: {e}")
        # Update call status to failed
        call.status = "failed"
        call.ended_at = datetime.utcnow()
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start voice agent"
        )


@router.post("/calls/{call_id}/input/text", response_model=ConversationResponse)
async def send_text_input(
    call_id: str,
    request: TextInputRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Send text input to an active call (for testing/demo)
    """
    user = await auth_service.get_current_user(db, credentials)
    
    # Verify call exists and user has access
    stmt = select(Call).join(Tenant).where(
        and_(
            Call.id == call_id,
            Call.status == "active"
        )
    )
    
    if user.role != "super_admin":
        stmt = stmt.where(Tenant.id == user.tenant_id)
    
    result = await db.execute(stmt)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active call not found"
        )
    
    try:
        # Get conversation context
        context = voice_agent_service.active_conversations.get(call_id)
        if not context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Call conversation not found"
            )
        
        # Add user message and generate response
        context.add_message("user", request.text)
        
        # Generate AI response
        response_text = await voice_agent_service._generate_ai_response(context, db)
        context.add_message("assistant", response_text)
        
        # Generate audio response
        audio_response = await voice_agent_service._text_to_speech(response_text, context)
        
        # Save transcript
        await voice_agent_service._save_transcript(
            call_id, request.text, response_text, db
        )
        
        # Encode audio as base64 for transport
        import base64
        audio_base64 = base64.b64encode(audio_response).decode() if audio_response else ""
        
        return ConversationResponse(
            call_id=call_id,
            transcript=request.text,
            response_text=response_text,
            audio_response=audio_base64,
            context=context.context_data
        )
        
    except Exception as e:
        logger.error(f"Error processing text input: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process input"
        )


@router.post("/calls/{call_id}/input/audio", response_model=ConversationResponse)
async def send_audio_input(
    call_id: str,
    audio_file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Send audio input to an active call
    """
    user = await auth_service.get_current_user(db, credentials)
    
    # Verify call exists and user has access
    stmt = select(Call).join(Tenant).where(
        and_(
            Call.id == call_id,
            Call.status == "active"
        )
    )
    
    if user.role != "super_admin":
        stmt = stmt.where(Tenant.id == user.tenant_id)
    
    result = await db.execute(stmt)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active call not found"
        )
    
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process audio input
        response = await voice_agent_service.process_speech_input(
            call_id, audio_data, db
        )
        
        # Encode audio response as base64
        import base64
        audio_base64 = base64.b64encode(
            response["audio_response"]
        ).decode() if response["audio_response"] else ""
        
        return ConversationResponse(
            call_id=call_id,
            transcript=response["transcript"],
            response_text=response["response_text"],
            audio_response=audio_base64,
            context=response["context"]
        )
        
    except Exception as e:
        logger.error(f"Error processing audio input: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process audio input"
        )


@router.post("/calls/{call_id}/end")
async def end_call(
    call_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    End an active call
    """
    user = await auth_service.get_current_user(db, credentials)
    
    # Verify call exists and user has access
    stmt = select(Call).join(Tenant).where(Call.id == call_id)
    
    if user.role != "super_admin":
        stmt = stmt.where(Tenant.id == user.tenant_id)
    
    result = await db.execute(stmt)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    try:
        # End conversation
        await voice_agent_service.end_conversation(call_id, db)
        
        return {"message": "Call ended successfully", "call_id": call_id}
        
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end call"
        )


@router.get("/calls", response_model=CallListResponse)
async def list_calls_demo(
    limit: int = Field(50, ge=1, le=100, description="Number of calls to return (1-100)"),
    offset: int = Field(0, ge=0, description="Number of calls to skip"),
    status: Optional[str] = Field(None, description="Filter by call status")
) -> CallListResponse:
    """
    List calls (public demo endpoint)
    
    This endpoint provides mock data for demonstration purposes.
    In production, use /calls/authenticated for real data.
    """
    try:
        # Validate pagination parameters
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )
        
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )
        
        # Validate status parameter
        valid_statuses = ["active", "completed", "failed", "cancelled"]
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of: {', '.join(valid_statuses)}"
            )
        
        # Get mock data
        result = mock_data_service.get_mock_calls(limit, offset, status)
        
        # Add metadata for demo
        result["demo"] = True
        result["message"] = "This is demo data. Use /calls/authenticated for real data."
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in demo calls endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve demo calls"
        )


@router.get("/calls/authenticated", response_model=CallListResponse)
async def list_calls_authenticated(
    limit: int = Field(50, ge=1, le=100, description="Number of calls to return (1-100)"),
    offset: int = Field(0, ge=0, description="Number of calls to skip"),
    status: Optional[str] = Field(None, description="Filter by call status"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> CallListResponse:
    """
    List calls for authenticated users
    """
    try:
        user = await auth_service.get_current_user(db, credentials)
        
        # Validate status parameter
        valid_statuses = ["active", "completed", "failed", "cancelled"]
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of: {', '.join(valid_statuses)}"
            )
        
        # Build query
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
        
        call_summaries = []
        for call in calls:
            call_summaries.append(CallSummary(
                id=call.id,
                caller_number=call.caller_number,
                status=call.status,
                direction=call.direction or "inbound",
                started_at=call.started_at.isoformat() if call.started_at else "",
                ended_at=call.ended_at.isoformat() if call.ended_at else None,
                duration_seconds=call.duration_seconds,
                summary=call.summary
            ))
        
        return CallListResponse(
            calls=call_summaries,
            total=total_calls,
            limit=limit,
            offset=offset,
            has_more=offset + limit < total_calls
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving calls for user {user.id if 'user' in locals() else 'unknown'}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve calls"
        )


@router.get("/calls/{call_id}")
async def get_call(
    call_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get detailed call information
    """
    user = await auth_service.get_current_user(db, credentials)
    
    # Get call with transcripts
    stmt = select(Call).where(Call.id == call_id)
    result = await db.execute(stmt)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Check access permissions
    if user.role != "super_admin" and str(call.tenant_id) != str(user.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get call transcripts
    from app.models.call import CallTranscript
    stmt = select(CallTranscript).where(
        CallTranscript.call_id == call_id
    ).order_by(CallTranscript.timestamp.asc())
    
    result = await db.execute(stmt)
    transcripts = result.scalars().all()
    
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


@router.get("/calls/{call_id}/status")
async def get_call_status(
    call_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current call status (for real-time monitoring)
    """
    user = await auth_service.get_current_user(db, credentials)
    
    stmt = select(Call).where(Call.id == call_id)
    result = await db.execute(stmt)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Check access permissions
    if user.role != "super_admin" and str(call.tenant_id) != str(user.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get active conversation context if available
    context = voice_agent_service.active_conversations.get(call_id)
    
    return {
        "call_id": call_id,
        "status": call.status,
        "active_conversation": context is not None,
        "message_count": len(context.messages) if context else 0,
        "last_activity": context.messages[-1]["timestamp"] if context and context.messages else None
    }


# Twilio Integration Endpoints
@router.post("/twilio/make-call")
async def make_ai_call(
    request: StartCallRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Make an outbound AI call using Twilio
    """
    user = await auth_service.get_current_user(db, credentials)
    
    # Determine tenant
    tenant_id = request.tenant_id if request.tenant_id else user.tenant_id
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID is required"
        )
    
    # Verify user has access to tenant
    if user.role != "super_admin" and str(user.tenant_id) != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to tenant"
        )
    
    # Check if Twilio is available
    if not twilio_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Twilio service is not configured"
        )
    
    try:
        # Make the call
        result = await twilio_service.make_outbound_call(
            request.caller_number, tenant_id, db
        )
        
        return {
            "success": True,
            "message": "Call initiated successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to make AI call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate call: {str(e)}"
        )


@router.post("/twilio/webhook/{call_id}")
async def twilio_webhook(
    call_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Handle Twilio webhook for call events
    """
    try:
        form_data = await request.form()
        
        # Handle incoming call
        if form_data.get("CallStatus") == "ringing":
            from_number = form_data.get("From", "")
            to_number = form_data.get("To", "")
            
            # Get tenant from call record
            stmt = select(Call).where(Call.id == call_id)
            result = await db.execute(stmt)
            call = result.scalar_one_or_none()
            
            if not call:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Call not found"
                )
            
            # Handle the incoming call
            twiml_response = await twilio_service.handle_incoming_call(
                from_number, to_number, str(call.tenant_id), db
            )
            
            return Response(content=twiml_response, media_type="application/xml")
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Twilio webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.post("/twilio/status/{call_id}")
async def twilio_status_webhook(
    call_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Handle Twilio status callback
    """
    try:
        form_data = await request.form()
        call_status = form_data.get("CallStatus", "")
        
        # Update call status
        await twilio_service.handle_call_status_update(call_id, call_status, db)
        
        return {"status": "updated"}
        
    except Exception as e:
        logger.error(f"Twilio status webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status update failed"
        )


@router.get("/twilio/status")
async def get_twilio_status(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if Twilio is configured and available
    """
    return {
        "available": twilio_service.is_available(),
        "configured": bool(twilio_service.client is not None)
    }


@router.get("/twilio/demo/status")
async def get_twilio_demo_status() -> Any:
    """
    Public demo endpoint to check Twilio status without authentication
    """
    return {
        "available": True,
        "configured": True,
        "demo_mode": True
    }


@router.get("/demo/stats")
async def get_demo_statistics() -> Any:
    """
    Get demo system statistics for dashboard
    """
    try:
        stats = mock_data_service.get_system_stats()
        stats["demo"] = True
        stats["message"] = "This is demo data for demonstration purposes."
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving demo statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve demo statistics"
        )


@router.get("/calls/{call_id}/demo", response_model=CallDetailResponse)
async def get_demo_call_detail(call_id: str) -> CallDetailResponse:
    """
    Get detailed call information (demo endpoint)
    """
    try:
        call = mock_data_service.get_mock_call_by_id(call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )
        
        transcripts = mock_data_service.get_mock_transcripts(call_id)
        
        call_summary = CallSummary(**call)
        
        return CallDetailResponse(
            call=call_summary,
            transcripts=transcripts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving demo call detail for {call_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve call details"
        )


@router.websocket("/conversation-relay/{call_id}")
async def conversation_relay_websocket(
    websocket: WebSocket,
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Twilio ConversationRelay WebSocket connection for real-time voice
    """
    logger.info(f"ConversationRelay WebSocket connection requested for call {call_id}")
    
    try:
        # Handle the WebSocket connection
        await conversation_relay_handler.handle_websocket_connection(
            websocket, call_id, db
        )
    except Exception as e:
        logger.error(f"ConversationRelay WebSocket error for call {call_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass  # WebSocket might already be closed


@router.get("/conversation-relay/status")
async def get_conversation_relay_status(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get ConversationRelay service status and active connections
    """
    user = await auth_service.get_current_user(db, credentials)
    
    return {
        "active_connections": conversation_relay_handler.get_connection_count(),
        "active_calls": conversation_relay_handler.get_active_calls(),
        "service_status": "running"
    }


@router.websocket("/media-stream/{call_id}")
async def media_stream_websocket(
    websocket: WebSocket,
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Twilio Media Streams WebSocket connection for real-time voice
    """
    await media_stream_handler.handle_websocket_connection(websocket, call_id, db)


@router.post("/conversation-relay/{call_id}/webhook")
async def conversation_relay_webhook(
    call_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Handle ConversationRelay webhook events
    """
    try:
        # Get request data
        data = await request.json()
        
        # Log the event
        logger.info(f"ConversationRelay webhook for call {call_id}: {data}")
        
        # Handle different event types
        event_type = data.get("event")
        
        if event_type == "connected":
            # ConversationRelay stream connected
            logger.info(f"ConversationRelay connected for call {call_id}")
        
        elif event_type == "start":
            # Stream started
            logger.info(f"ConversationRelay stream started for call {call_id}")
        
        elif event_type == "stop":
            # Stream stopped
            logger.info(f"ConversationRelay stream stopped for call {call_id}")
            
            # End the conversation
            await voice_agent_service.end_conversation(call_id, db)
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"ConversationRelay webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )