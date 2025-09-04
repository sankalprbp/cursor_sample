"""
Twilio Media Streams Handler
Manages real-time voice conversations using Twilio's Media Streams API
"""

import asyncio
import json
import logging
import base64
import time
from typing import Dict, Optional, Any, Union, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.voice_agent import voice_agent_service
from app.services.audio_processor import audio_processor


def load_conversation_config() -> ConversationFlowConfig:
    """Load conversation configuration from settings or environment"""
    return ConversationFlowConfig(
        silence_threshold_seconds=getattr(settings, 'CONVERSATION_SILENCE_THRESHOLD', 3.0),
        max_conversation_minutes=getattr(settings, 'CONVERSATION_MAX_MINUTES', 30),
        max_errors=getattr(settings, 'CONVERSATION_MAX_ERRORS', 5),
        turn_taking_enabled=getattr(settings, 'CONVERSATION_TURN_TAKING_ENABLED', True),
        interruption_cooldown_seconds=getattr(settings, 'CONVERSATION_INTERRUPTION_COOLDOWN', 1.0)
    )


logger = logging.getLogger(__name__)


@dataclass
class ConversationFlowConfig:
    """Configuration for conversation flow management"""
    silence_threshold_seconds: float = 3.0
    max_conversation_minutes: int = 30
    max_errors: int = 5
    turn_taking_enabled: bool = True
    interruption_cooldown_seconds: float = 1.0


@dataclass
class ConversationMetrics:
    """Metrics tracking for conversation quality"""
    turn_count: int = 0
    total_duration_seconds: float = 0
    interruption_count: int = 0
    error_count: int = 0
    last_speech_time: Optional[datetime] = None
    silence_start_time: Optional[datetime] = None


@dataclass
class ConversationState:
    """Current state of the conversation"""
    is_ai_speaking: bool = False
    caller_interrupted: bool = False
    is_caller_speaking: bool = False
    
    def reset_interruption(self):
        """Reset interruption state"""
        self.caller_interrupted = False
    
    def handle_interruption(self):
        """Handle caller interruption"""
        self.caller_interrupted = True
        self.is_ai_speaking = False


class ConnectionState:
    """Represents the state of a Media Streams connection with enhanced conversation management"""
    
    def __init__(
        self, 
        call_id: str, 
        websocket: WebSocket,
        flow_config: Optional[ConversationFlowConfig] = None
    ):
        # Core connection attributes
        self.call_id = call_id
        self.websocket = websocket
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        
        # Media stream attributes
        self.stream_sid: Optional[str] = None
        self.media_format: Dict[str, Any] = {}
        self.audio_buffer: List[bytes] = []
        
        # Conversation management
        self.flow_config = flow_config or ConversationFlowConfig()
        self.metrics = ConversationMetrics()
        self.conversation_state = ConversationState()
        
        # Legacy compatibility (deprecated - use conversation_state instead)
        self.is_speaking = False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def increment_error(self) -> bool:
        """Increment error count and return True if max errors exceeded"""
        self.metrics.error_count += 1
        return self.metrics.error_count >= self.flow_config.max_errors
    
    def is_stale(self, timeout_minutes: int = 30) -> bool:
        """Check if connection is stale based on last activity"""
        return datetime.utcnow() - self.last_activity > timedelta(minutes=timeout_minutes)
    
    def update_speech_activity(self, is_speaking: bool):
        """Update speech activity tracking"""
        current_time = datetime.utcnow()
        
        if is_speaking:
            self.metrics.last_speech_time = current_time
            self.metrics.silence_start_time = None
            self.conversation_state.is_caller_speaking = True
        else:
            self.conversation_state.is_caller_speaking = False
            if self.metrics.silence_start_time is None:
                self.metrics.silence_start_time = current_time
    
    def get_silence_duration(self) -> float:
        """Get current silence duration in seconds"""
        if self.metrics.silence_start_time is None:
            return 0.0
        return (datetime.utcnow() - self.metrics.silence_start_time).total_seconds()
    
    def is_silence_threshold_exceeded(self) -> bool:
        """Check if silence threshold has been exceeded"""
        return self.get_silence_duration() >= self.flow_config.silence_threshold_seconds
    
    def get_conversation_duration(self) -> float:
        """Get total conversation duration in minutes"""
        return (datetime.utcnow() - self.connected_at).total_seconds() / 60
    
    def is_conversation_too_long(self) -> bool:
        """Check if conversation has exceeded maximum duration"""
        return self.get_conversation_duration() > self.flow_config.max_conversation_minutes
    
    def increment_turn_count(self):
        """Increment conversation turn count"""
        self.metrics.turn_count += 1
    
    def handle_interruption(self):
        """Handle caller interruption with proper state management"""
        self.conversation_state.handle_interruption()
        self.metrics.interruption_count += 1
        logger.info(f"Interruption handled for call {self.call_id} (total: {self.metrics.interruption_count})")
    
    def reset_interruption_state(self):
        """Reset interruption state after handling"""
        self.conversation_state.reset_interruption()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of conversation metrics"""
        return {
            "call_id": self.call_id,
            "duration_minutes": round(self.get_conversation_duration(), 2),
            "turn_count": self.metrics.turn_count,
            "interruption_count": self.metrics.interruption_count,
            "error_count": self.metrics.error_count,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "is_ai_speaking": self.conversation_state.is_ai_speaking,
            "is_caller_speaking": self.conversation_state.is_caller_speaking
        }


class MediaStreamHandler:
    """Handles Twilio Media Streams WebSocket connections for real-time voice"""
    
    def __init__(self, default_flow_config: Optional[ConversationFlowConfig] = None):
        self.active_connections: Dict[str, ConnectionState] = {}
        self.default_flow_config = default_flow_config or ConversationFlowConfig()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def create_connection_state(
        self, 
        call_id: str, 
        websocket: WebSocket,
        flow_config: Optional[ConversationFlowConfig] = None
    ) -> ConnectionState:
        """Factory method for creating ConnectionState with proper configuration"""
        config = flow_config or self.default_flow_config
        return ConnectionState(call_id, websocket, config)
    
    def _start_cleanup_task(self):
        """Start background task for connection cleanup"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def _periodic_cleanup(self):
        """Periodically clean up stale connections"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def _cleanup_stale_connections(self):
        """Clean up stale connections"""
        stale_calls = [
            call_id for call_id, state in self.active_connections.items()
            if state.is_stale()
        ]
        
        for call_id in stale_calls:
            logger.warning(f"Cleaning up stale connection for call {call_id}")
            await self._cleanup_connection(call_id, None)
    
    async def handle_websocket_connection(
        self, 
        websocket: WebSocket, 
        call_id: str,
        db: AsyncSession
    ):
        """Handle incoming ConversationRelay WebSocket connection"""
        
        connection_state = None
        
        try:
            await websocket.accept()
            
            # Create connection state
            connection_state = self.create_connection_state(call_id, websocket)
            self.active_connections[call_id] = connection_state
            
            logger.info(f"ConversationRelay connected for call {call_id}")
            
            # Send initial greeting
            await self._send_initial_greeting(call_id, db)
            
            # Handle incoming messages
            async for message in self._message_handler(websocket, call_id):
                try:
                    await self._process_relay_message(call_id, message, db)
                    connection_state.update_activity()
                    
                except Exception as e:
                    logger.error(f"Error processing ConversationRelay message: {e}")
                    if connection_state.increment_error():
                        logger.error(f"Max errors exceeded for call {call_id}, closing connection")
                        break
        
        except WebSocketDisconnect:
            logger.info(f"ConversationRelay disconnected for call {call_id}")
        except Exception as e:
            logger.error(f"ConversationRelay connection error for call {call_id}: {e}")
        
        finally:
            # Cleanup connection
            await self._cleanup_connection(call_id, db)
    
    async def _message_handler(self, websocket: WebSocket, call_id: str):
        """Async generator for handling WebSocket messages with proper error handling"""
        try:
            while True:
                try:
                    message = await asyncio.wait_for(
                        websocket.receive_text(), 
                        timeout=30.0  # 30 second timeout
                    )
                    yield message
                except asyncio.TimeoutError:
                    logger.warning(f"WebSocket timeout for call {call_id}")
                    # Send ping to check if connection is still alive
                    try:
                        await websocket.ping()
                    except Exception:
                        logger.error(f"WebSocket ping failed for call {call_id}")
                        break
                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for call {call_id}")
                    break
        except Exception as e:
            logger.error(f"Message handler error for call {call_id}: {e}")
            raise
    
    async def _process_relay_message(self, call_id: str, message: str, db):
        """Process incoming message from ConversationRelay"""
        
        try:
            data = json.loads(message)
            event_type = data.get("event")
            
            if event_type == "connected":
                await self._handle_connected_event(call_id, data, db)
            
            elif event_type == "start":
                await self._handle_start_event(call_id, data, db)
            
            elif event_type == "media":
                await self._handle_media_event(call_id, data, db)
            
            elif event_type == "stop":
                await self._handle_stop_event(call_id, data, db)
            
            else:
                logger.warning(f"Unknown ConversationRelay event: {event_type}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from ConversationRelay: {message}")
        except Exception as e:
            logger.error(f"Error processing ConversationRelay message: {e}")
    
    async def _handle_connected_event(self, call_id: str, data: Dict, db: AsyncSession):
        """Handle ConversationRelay connected event"""
        logger.info(f"ConversationRelay stream connected for call {call_id}")
        
        connection_state = self.active_connections.get(call_id)
        if connection_state:
            connection_state.update_activity()
            logger.debug(f"Updated activity for connected call {call_id}")
    
    async def _handle_start_event(self, call_id: str, data: Dict, db: AsyncSession):
        """Handle ConversationRelay start event"""
        logger.info(f"ConversationRelay stream started for call {call_id}")
        
        connection_state = self.active_connections.get(call_id)
        if not connection_state:
            logger.error(f"No connection state found for call {call_id}")
            return
        
        # Extract and validate stream configuration
        stream_sid = data.get("streamSid")
        if not stream_sid:
            logger.error(f"No streamSid in start event for call {call_id}")
            return
        
        media_format = data.get("mediaFormat", {})
        
        # Update connection state
        connection_state.stream_sid = stream_sid
        connection_state.media_format = media_format
        
        logger.info(f"Stream configured for call {call_id}: {stream_sid}")
    
    async def _handle_media_event(self, call_id: str, data: Dict, db):
        """Handle incoming audio media from ConversationRelay with enhanced flow control"""
        
        try:
            connection_state = self.active_connections.get(call_id)
            if not connection_state:
                logger.error(f"No connection state for call {call_id}")
                return
            
            # Extract audio data
            media = data.get("media", {})
            payload = media.get("payload")
            
            if not payload:
                # Handle silence detection
                connection_state.update_speech_activity(False)
                await self._handle_silence_detection(call_id, connection_state)
                return
            
            # Update speech activity
            connection_state.update_speech_activity(True)
            
            # Check for interruption during AI speech
            if connection_state.conversation_state.is_ai_speaking:
                logger.info(f"Caller interrupted AI for call {call_id}")
                connection_state.handle_interruption()
                await self._handle_interruption(call_id)
            
            # Decode base64 audio
            audio_data = base64.b64decode(payload)
            
            # Process audio through speech-to-text
            transcript = await self._process_speech_to_text(audio_data, call_id)
            
            if transcript and transcript.strip():
                # Check conversation length limits
                if await self._check_conversation_limits(call_id, connection_state):
                    return
                
                # Generate AI response with turn-taking logic
                start_time = time.time()
                await self._generate_and_send_response(call_id, transcript, db)
                response_time_ms = (time.time() - start_time) * 1000
                
                # Record conversation turn metrics
                try:
                    from app.services.metrics import metrics_collector
                    await metrics_collector.record_conversation_turn(
                        call_id, 
                        response_time_ms,
                        len(transcript),  # User input length
                        0,  # AI response length (will be updated later)
                        connection_state.conversation_state.caller_interrupted
                    )
                except ImportError:
                    logger.warning("Metrics collector not available")
                
                connection_state.increment_turn_count()
            
            # Update activity - caller finished speaking
            connection_state.update_speech_activity(False)
        
        except Exception as e:
            logger.error(f"Error handling media event: {e}")
    
    async def _handle_stop_event(self, call_id: str, data: Dict, db: AsyncSession):
        """Handle ConversationRelay stop event"""
        logger.info(f"ConversationRelay stream stopped for call {call_id}")
        
        connection_state = self.active_connections.get(call_id)
        if connection_state:
            connection_state.stream_sid = None
        
        # End the conversation
        try:
            await voice_agent_service.end_conversation(call_id, db)
        except Exception as e:
            logger.error(f"Error ending conversation for call {call_id}: {e}")
    
    async def _send_initial_greeting(self, call_id: str, db):
        """Send initial greeting to caller"""
        
        try:
            # Get conversation context
            context = voice_agent_service.active_conversations.get(call_id)
            
            if context and context.messages:
                greeting_text = context.messages[-1]["content"]
                
                # Convert to audio and send
                await self._send_audio_response(call_id, greeting_text)
        
        except Exception as e:
            logger.error(f"Error sending initial greeting: {e}")
    
    async def _process_speech_to_text(self, audio_data: bytes, call_id: str) -> Optional[str]:
        """Convert speech to text using OpenAI Whisper"""
        
        try:
            # Convert audio format if needed
            processed_audio = await audio_processor.convert_for_whisper(audio_data)
            
            # Use voice agent service for speech-to-text
            transcript = await voice_agent_service._speech_to_text(processed_audio)
            
            logger.info(f"Speech-to-text for call {call_id}: {transcript}")
            return transcript
        
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return None
    
    async def _generate_and_send_response(self, call_id: str, transcript: str, db):
        """Generate AI response and send audio back to caller with enhanced flow control"""
        
        try:
            connection_state = self.active_connections.get(call_id)
            if not connection_state:
                logger.error(f"No connection state for call {call_id}")
                return
            
            # Get conversation context
            context = voice_agent_service.active_conversations.get(call_id)
            
            if not context:
                logger.error(f"No conversation context for call {call_id}")
                return
            
            # Implement turn-taking logic
            await self._implement_turn_taking_logic(call_id, connection_state)
            
            # Add user message to context
            context.add_message("user", transcript)
            
            # Generate AI response
            response_text = await voice_agent_service._generate_ai_response(context, db)
            context.add_message("assistant", response_text)
            
            # Check if caller interrupted during generation
            if connection_state.conversation_state.caller_interrupted:
                logger.info(f"Skipping response due to interruption for call {call_id}")
                connection_state.reset_interruption_state()
                return
            
            # Mark AI as speaking before sending audio
            connection_state.conversation_state.is_ai_speaking = True
            
            # Convert to audio and send
            await self._send_audio_response(call_id, response_text)
            
            # Save transcript
            await voice_agent_service._save_transcript(call_id, transcript, response_text, db)
            
            # Mark AI as finished speaking
            connection_state.conversation_state.is_ai_speaking = False
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Ensure AI speaking state is reset on error
            if call_id in self.active_connections:
                self.active_connections[call_id].conversation_state.is_ai_speaking = False
    
    async def _send_audio_response(self, call_id: str, text: str):
        """Convert text to speech and send to ConversationRelay"""
        
        connection_state = self.active_connections.get(call_id)
        if not connection_state:
            logger.error(f"No connection state for call {call_id}")
            return
        
        if not connection_state.stream_sid:
            logger.error(f"No stream SID available for call {call_id}")
            return
        
        try:
            # Get conversation context for voice settings
            context = voice_agent_service.active_conversations.get(call_id)
            
            # Generate audio using ElevenLabs with timeout
            audio_data = await asyncio.wait_for(
                voice_agent_service._text_to_speech(text, context),
                timeout=10.0  # 10 second timeout for TTS
            )
            
            if not audio_data:
                logger.error(f"No audio data generated for call {call_id}")
                await self._send_fallback_response(call_id, text)
                return
            
            # Convert audio format for ConversationRelay
            processed_audio = await audio_processor.convert_for_twilio(audio_data)
            
            # Encode as base64
            audio_base64 = base64.b64encode(processed_audio).decode()
            
            # Send audio to ConversationRelay
            media_message = {
                "event": "media",
                "streamSid": connection_state.stream_sid,
                "media": {
                    "payload": audio_base64
                }
            }
            
            await connection_state.websocket.send_text(json.dumps(media_message))
            logger.info(f"Sent audio response for call {call_id} ({len(text)} chars)")
        
        except asyncio.TimeoutError:
            logger.error(f"TTS timeout for call {call_id}")
            await self._send_fallback_response(call_id, text)
        except Exception as e:
            logger.error(f"Error sending audio response for call {call_id}: {e}")
            await self._send_fallback_response(call_id, text)
    
    async def _send_fallback_response(self, call_id: str, original_text: str):
        """Send a fallback text response when audio fails"""
        try:
            connection_state = self.active_connections.get(call_id)
            if not connection_state:
                return
            
            fallback_message = {
                "event": "mark",
                "streamSid": connection_state.stream_sid,
                "mark": {
                    "name": f"fallback_response_{datetime.utcnow().timestamp()}"
                }
            }
            
            await connection_state.websocket.send_text(json.dumps(fallback_message))
            logger.info(f"Sent fallback response for call {call_id}")
            
        except Exception as e:
            logger.error(f"Error sending fallback response for call {call_id}: {e}")
    
    async def _handle_silence_detection(self, call_id: str, connection_state: ConnectionState):
        """Handle silence detection and prompting"""
        
        try:
            # Check if silence threshold exceeded
            if connection_state.is_silence_threshold_exceeded():
                silence_duration = connection_state.get_silence_duration()
                logger.info(f"Silence detected for {silence_duration:.1f}s on call {call_id}")
                
                # Send prompting message
                prompts = [
                    "I'm here to help. Is there anything else you'd like to know?",
                    "Are you still there? How can I assist you further?",
                    "I'm listening. Please let me know if you have any questions.",
                    "Is there anything specific I can help you with today?"
                ]
                
                # Select prompt based on conversation turn count
                prompt_index = min(connection_state.metrics.turn_count // 3, len(prompts) - 1)
                prompt_text = prompts[prompt_index]
                
                await self._send_audio_response(call_id, prompt_text)
                
                # Reset silence timer and increment turn count
                connection_state.metrics.silence_start_time = None
                connection_state.increment_turn_count()
        
        except Exception as e:
            logger.error(f"Error handling silence detection: {e}")
    
    async def _handle_interruption(self, call_id: str):
        """Handle caller interruption during AI speech"""
        
        try:
            connection_state = self.active_connections.get(call_id)
            if not connection_state:
                return
            
            # Send clear message to stop current audio
            clear_message = {
                "event": "clear",
                "streamSid": connection_state.stream_sid
            }
            
            await connection_state.websocket.send_text(json.dumps(clear_message))
            logger.info(f"Handled interruption for call {call_id}")
            
            # Handle interruption state
            connection_state.handle_interruption()
        
        except Exception as e:
            logger.error(f"Error handling interruption: {e}")
    
    async def _check_conversation_limits(self, call_id: str, connection_state: ConnectionState) -> bool:
        """Check conversation length limits and warn if necessary"""
        
        try:
            # Check if conversation is getting long
            if connection_state.is_conversation_too_long():
                conversation_duration = connection_state.get_conversation_duration()
                logger.warning(f"Conversation exceeded {connection_state.flow_config.max_conversation_minutes} minutes for call {call_id}")
                
                # Send warning message
                warning_text = "I notice we've been talking for quite a while. Is there anything specific I can help you wrap up today?"
                await self._send_audio_response(call_id, warning_text)
                
                # Update limits to avoid repeated warnings
                connection_state.flow_config.max_conversation_minutes += 15
                return True
            
            # Check turn count for natural conversation flow
            if connection_state.metrics.turn_count > 50:
                logger.info(f"High turn count ({connection_state.metrics.turn_count}) for call {call_id}")
                
                # Suggest wrapping up
                if connection_state.metrics.turn_count % 25 == 0:
                    wrap_up_text = "We've covered a lot today. Is there anything else I can help you with before we finish?"
                    await self._send_audio_response(call_id, wrap_up_text)
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking conversation limits: {e}")
            return False
    
    async def _implement_turn_taking_logic(self, call_id: str, connection_state: ConnectionState):
        """Implement natural turn-taking logic"""
        
        try:
            if not connection_state.flow_config.turn_taking_enabled:
                return
            
            # Wait for natural pause before responding
            if connection_state.metrics.last_speech_time:
                time_since_speech = (datetime.utcnow() - connection_state.metrics.last_speech_time).total_seconds()
                
                # Ensure minimum pause for natural conversation
                min_pause = 0.5  # 500ms minimum pause
                if time_since_speech < min_pause:
                    await asyncio.sleep(min_pause - time_since_speech)
            
            # Reset interruption state and prepare for AI response
            connection_state.reset_interruption_state()
        
        except Exception as e:
            logger.error(f"Error in turn-taking logic: {e}")
    
    async def _cleanup_connection(self, call_id: str, db: Optional[AsyncSession]):
        """Clean up connection and resources"""
        
        try:
            # Get connection state before removal
            connection_state = self.active_connections.get(call_id)
            
            # Remove from active connections
            if call_id in self.active_connections:
                del self.active_connections[call_id]
            
            # End conversation if still active and db is available
            if db and call_id in voice_agent_service.active_conversations:
                try:
                    await voice_agent_service.end_conversation(call_id, db)
                except Exception as e:
                    logger.error(f"Error ending conversation for call {call_id}: {e}")
            
            # Close WebSocket if still open
            if connection_state and connection_state.websocket:
                try:
                    await connection_state.websocket.close()
                except Exception as e:
                    logger.debug(f"WebSocket already closed for call {call_id}: {e}")
            
            logger.info(f"Cleaned up ConversationRelay connection for call {call_id}")
        
        except Exception as e:
            logger.error(f"Error cleaning up connection for call {call_id}: {e}")
    
    async def shutdown(self):
        """Shutdown handler and cleanup all connections"""
        logger.info("Shutting down ConversationRelay handler")
        
        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup all active connections
        call_ids = list(self.active_connections.keys())
        for call_id in call_ids:
            await self._cleanup_connection(call_id, None)
        
        logger.info("ConversationRelay handler shutdown complete")
    
    async def handle_interruption(self, call_id: str):
        """Handle caller interruption (stop current audio)"""
        
        try:
            websocket = self.active_connections.get(call_id)
            if not websocket:
                return
            
            # Send clear message to stop current audio
            clear_message = {
                "event": "clear",
                "streamSid": self.call_contexts.get(call_id, {}).get("stream_sid")
            }
            
            await websocket.send_text(json.dumps(clear_message))
            logger.info(f"Sent interruption clear for call {call_id}")
        
        except Exception as e:
            logger.error(f"Error handling interruption: {e}")
    
    def is_connected(self, call_id: str) -> bool:
        """Check if ConversationRelay is connected for a call"""
        return call_id in self.active_connections
    
    def get_connection_info(self, call_id: str) -> Optional[Dict]:
        """Get connection information for a call"""
        connection_state = self.active_connections.get(call_id)
        if not connection_state:
            return None
        
        base_info = {
            "call_id": connection_state.call_id,
            "connected_at": connection_state.connected_at.isoformat(),
            "stream_sid": connection_state.stream_sid,
            "media_format": connection_state.media_format,
            "last_activity": connection_state.last_activity.isoformat(),
            "buffer_size": len(connection_state.audio_buffer)
        }
        
        # Add conversation summary
        conversation_summary = connection_state.get_conversation_summary()
        return {**base_info, **conversation_summary}
    
    def get_active_calls(self) -> List[str]:
        """Get list of active call IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global instance with configuration
media_stream_handler = MediaStreamHandler(load_conversation_config())