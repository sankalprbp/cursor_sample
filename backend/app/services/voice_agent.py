"""
AI Voice Agent Service
Core service for handling real-time AI phone conversations
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import openai
from elevenlabs import generate, stream, set_api_key
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.call import Call, CallTranscript
from app.models.tenant import Tenant
from app.models.knowledge_base import KnowledgeBase, KnowledgeDocument
from app.services.knowledge import knowledge_service


# Configure APIs
openai.api_key = settings.OPENAI_API_KEY
set_api_key(settings.ELEVENLABS_API_KEY)

logger = logging.getLogger(__name__)


class ConversationContext:
    """Manages conversation context and state"""
    
    def __init__(self, call_id: str, tenant_id: str):
        self.call_id = call_id
        self.tenant_id = tenant_id
        self.messages: List[Dict] = []
        self.context_data: Dict = {}
        self.session_data: Dict = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.messages[-limit:] if self.messages else []
    
    def set_context(self, key: str, value: Any):
        """Set context data"""
        self.context_data[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self.context_data.get(key, default)


class VoiceAgentService:
    """Main voice agent service for handling AI phone conversations"""
    
    def __init__(self):
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def start_conversation(
        self, 
        call_id: str, 
        tenant_id: str,
        caller_number: str,
        db: AsyncSession
    ) -> ConversationContext:
        """Start a new voice conversation"""
        
        # Get tenant configuration
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")
        
        # Create conversation context
        context = ConversationContext(call_id, tenant_id)
        context.set_context("tenant", tenant)
        context.set_context("caller_number", caller_number)
        context.set_context("agent_name", tenant.agent_name)
        context.set_context("agent_personality", tenant.agent_personality)
        
        # Store active conversation
        self.active_conversations[call_id] = context
        
        # Generate initial greeting
        greeting = await self._generate_initial_greeting(context, db)
        context.add_message("assistant", greeting)
        
        logger.info(f"Started conversation for call {call_id}")
        return context
    
    async def process_speech_input(
        self, 
        call_id: str, 
        audio_data: bytes,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Process incoming speech and generate response"""
        
        context = self.active_conversations.get(call_id)
        if not context:
            raise ValueError(f"No active conversation for call {call_id}")
        
        try:
            # Speech to text
            transcript = await self._speech_to_text(audio_data)
            context.add_message("user", transcript)
            
            # Generate AI response
            response_text = await self._generate_ai_response(context, db)
            context.add_message("assistant", response_text)
            
            # Text to speech
            audio_response = await self._text_to_speech(response_text, context)
            
            # Save transcript to database
            await self._save_transcript(call_id, transcript, response_text, db)
            
            return {
                "transcript": transcript,
                "response_text": response_text,
                "audio_response": audio_response,
                "context": context.context_data
            }
            
        except Exception as e:
            logger.error(f"Error processing speech input: {e}")
            raise
    
    async def end_conversation(self, call_id: str, db: AsyncSession):
        """End conversation and cleanup"""
        context = self.active_conversations.get(call_id)
        if context:
            # Generate call summary
            summary = await self._generate_call_summary(context)
            
            # Update call record
            stmt = select(Call).where(Call.id == call_id)
            result = await db.execute(stmt)
            call = result.scalar_one_or_none()
            
            if call:
                call.summary = summary
                call.ended_at = datetime.utcnow()
                call.status = "completed"
                await db.commit()
            
            # Remove from active conversations
            del self.active_conversations[call_id]
            
            logger.info(f"Ended conversation for call {call_id}")
    
    async def _speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text using OpenAI Whisper"""
        try:
            # Create a temporary file-like object
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            response = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Speech to text error: {e}")
            return "Sorry, I couldn't understand that."
    
    async def _generate_ai_response(
        self, 
        context: ConversationContext, 
        db: AsyncSession
    ) -> str:
        """Generate AI response using OpenAI"""
        
        try:
            # Get tenant configuration
            tenant = context.get_context("tenant")
            
            # Build system prompt
            system_prompt = await self._build_system_prompt(context, db)
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in context.get_conversation_history():
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Generate response
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
                functions=self._get_available_functions(),
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.function_call:
                function_response = await self._handle_function_call(
                    message.function_call, context, db
                )
                return function_response
            
            return message.content.strip()
            
        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return "I apologize, but I'm having trouble processing your request right now."
    
    async def _text_to_speech(
        self, 
        text: str, 
        context: ConversationContext
    ) -> bytes:
        """Convert text to speech using ElevenLabs"""
        try:
            # Get tenant's preferred voice settings
            voice_id = settings.ELEVENLABS_VOICE_ID
            
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2",
                stability=settings.ELEVENLABS_STABILITY,
                similarity_boost=settings.ELEVENLABS_SIMILARITY_BOOST
            )
            
            return audio
            
        except Exception as e:
            logger.error(f"Text to speech error: {e}")
            # Return empty audio on error
            return b""
    
    async def _build_system_prompt(
        self, 
        context: ConversationContext, 
        db: AsyncSession
    ) -> str:
        """Build system prompt with context and knowledge"""
        
        tenant = context.get_context("tenant")
        agent_name = context.get_context("agent_name", "AI Assistant")
        personality = context.get_context("agent_personality", "")
        
        # Get relevant knowledge base content
        last_user_message = ""
        if context.messages:
            for msg in reversed(context.messages):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break
        
        knowledge_context = ""
        if last_user_message:
            knowledge = await knowledge_service.search_knowledge(
                tenant.id, last_user_message, db, limit=3
            )
            if knowledge:
                knowledge_context = "\n\nRelevant knowledge:\n" + "\n".join([
                    f"- {item['content'][:200]}..." for item in knowledge
                ])
        
        system_prompt = f"""You are {agent_name}, an AI assistant for {tenant.name}.

{personality}

Instructions:
- Be helpful, professional, and friendly
- Keep responses conversational and concise
- If you don't know something, admit it and offer to help find the information
- Use the knowledge base information when relevant
- Stay in character as a representative of {tenant.name}

Company Information:
- Company: {tenant.name}
- Phone: {tenant.phone or 'Not specified'}
- Email: {tenant.email or 'Not specified'}

{knowledge_context}

Current conversation context:
- Caller: {context.get_context('caller_number', 'Unknown')}
- Call started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

Respond naturally and helpfully to the caller's needs."""

        return system_prompt
    
    async def _generate_initial_greeting(
        self, 
        context: ConversationContext, 
        db: AsyncSession
    ) -> str:
        """Generate initial greeting for the call"""
        
        tenant = context.get_context("tenant")
        agent_name = context.get_context("agent_name", "AI Assistant")
        
        greeting = f"Hello! This is {agent_name} from {tenant.name}. How can I help you today?"
        
        return greeting
    
    async def _save_transcript(
        self, 
        call_id: str, 
        user_input: str, 
        ai_response: str, 
        db: AsyncSession
    ):
        """Save conversation transcript to database"""
        try:
            transcript = CallTranscript(
                call_id=call_id,
                speaker="user",
                text=user_input,
                timestamp=datetime.utcnow()
            )
            db.add(transcript)
            
            response_transcript = CallTranscript(
                call_id=call_id,
                speaker="assistant",
                text=ai_response,
                timestamp=datetime.utcnow()
            )
            db.add(response_transcript)
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error saving transcript: {e}")
    
    async def _generate_call_summary(self, context: ConversationContext) -> str:
        """Generate call summary using AI"""
        try:
            if not context.messages:
                return "No conversation recorded."
            
            # Prepare conversation for summarization
            conversation = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in context.messages
            ])
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Summarize this customer service call in 2-3 sentences. Include the main topic, any actions taken, and the outcome."
                    },
                    {"role": "user", "content": conversation}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating call summary: {e}")
            return "Call summary generation failed."
    
    def _get_available_functions(self) -> List[Dict]:
        """Get available functions for OpenAI function calling"""
        return [
            {
                "name": "transfer_to_human",
                "description": "Transfer call to a human agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Reason for transfer"
                        }
                    },
                    "required": ["reason"]
                }
            },
            {
                "name": "schedule_callback",
                "description": "Schedule a callback for the customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "Customer phone number"
                        },
                        "preferred_time": {
                            "type": "string",
                            "description": "Preferred callback time"
                        }
                    },
                    "required": ["phone_number", "preferred_time"]
                }
            }
        ]
    
    async def _handle_function_call(
        self, 
        function_call, 
        context: ConversationContext, 
        db: AsyncSession
    ) -> str:
        """Handle OpenAI function calls"""
        function_name = function_call.name
        arguments = json.loads(function_call.arguments)
        
        if function_name == "transfer_to_human":
            reason = arguments.get("reason", "Customer request")
            context.set_context("transfer_requested", True)
            context.set_context("transfer_reason", reason)
            return f"I'll transfer you to a human agent now. Reason: {reason}"
        
        elif function_name == "schedule_callback":
            phone = arguments.get("phone_number")
            time = arguments.get("preferred_time")
            # Here you would integrate with a scheduling system
            return f"I've scheduled a callback to {phone} at {time}. You'll receive a confirmation shortly."
        
        return "I'm sorry, I couldn't process that request."


# Global voice agent service instance
voice_agent_service = VoiceAgentService()