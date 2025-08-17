# AI Voice Agent MVP - Design Document

## Overview

This design document outlines the architecture and implementation approach for a working AI voice agent MVP that can receive calls and handle conversations using Twilio ConversationRelay, OpenAI GPT, ElevenLabs voice synthesis, and existing infrastructure. The design focuses on simplicity, reliability, and demonstrable functionality while building on the existing codebase.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    A[Caller] -->|Voice Call| B[Twilio Phone Number]
    B --> C[Twilio ConversationRelay]
    C -->|Webhook| D[FastAPI Voice Endpoint]
    D --> E[Conversation Manager]
    E --> F[OpenAI GPT Service]
    E --> G[Knowledge Base Service]
    E --> H[ElevenLabs TTS Service]
    E --> I[Call Logger]
    F --> J[PostgreSQL Database]
    G --> J
    I --> J
    E -->|Audio Response| C
    C -->|Audio| A
```

### System Components

#### 1. Twilio ConversationRelay Integration
- **Purpose**: Handle real-time voice conversations with automatic speech recognition and text-to-speech
- **Implementation**: WebSocket connection to Twilio's ConversationRelay API
- **Key Features**:
  - Automatic speech-to-text transcription
  - Real-time audio streaming
  - Interruption handling
  - Connection management and reconnection

#### 2. Conversation Manager
- **Purpose**: Orchestrate the conversation flow and manage state
- **Implementation**: Python service class with async methods
- **Key Features**:
  - Conversation context management
  - Turn-taking logic
  - Error handling and fallbacks
  - Performance monitoring

#### 3. Enhanced Voice Service
- **Purpose**: Process voice interactions and generate responses
- **Implementation**: Extension of existing voice_agent.py service
- **Key Features**:
  - OpenAI GPT integration for conversation
  - Knowledge base query integration
  - Response optimization for voice
  - Context-aware responses

#### 4. Knowledge Base Integration
- **Purpose**: Provide relevant information to enhance AI responses
- **Implementation**: Extension of existing knowledge.py service
- **Key Features**:
  - Document search and retrieval
  - Context-aware information extraction
  - Fallback handling for missing information

## Components and Interfaces

### 1. ConversationRelay Handler

```python
class ConversationRelayHandler:
    """Handles Twilio ConversationRelay WebSocket connections"""
    
    async def handle_connection(self, websocket: WebSocket, call_id: str)
    async def process_speech_input(self, transcript: str, call_id: str)
    async def send_audio_response(self, audio_data: bytes, call_id: str)
    async def handle_interruption(self, call_id: str)
    async def cleanup_connection(self, call_id: str)
```

### 2. Enhanced Conversation Manager

```python
class ConversationManager:
    """Manages conversation state and flow"""
    
    async def start_conversation(self, call_id: str, caller_info: dict)
    async def process_user_input(self, call_id: str, transcript: str)
    async def generate_response(self, call_id: str, context: dict)
    async def end_conversation(self, call_id: str)
    async def get_conversation_context(self, call_id: str)
```

### 3. Voice Response Generator

```python
class VoiceResponseGenerator:
    """Generates voice responses using OpenAI and ElevenLabs"""
    
    async def generate_text_response(self, prompt: str, context: dict)
    async def synthesize_speech(self, text: str, voice_settings: dict)
    async def optimize_for_voice(self, text: str)
    async def handle_interruption_response(self)
```

### 4. Knowledge Base Query Engine

```python
class KnowledgeQueryEngine:
    """Queries knowledge base for relevant information"""
    
    async def search_knowledge(self, query: str, tenant_id: str = None)
    async def extract_relevant_context(self, documents: list, query: str)
    async def format_for_conversation(self, knowledge: dict)
```

## Data Models

### 1. Call Session Model

```python
class CallSession(Base):
    __tablename__ = "call_sessions"
    
    id: str = Column(String, primary_key=True)  # Twilio Call SID
    phone_number: str = Column(String, nullable=False)
    start_time: datetime = Column(DateTime, default=datetime.utcnow)
    end_time: datetime = Column(DateTime, nullable=True)
    status: str = Column(String, default="active")  # active, completed, failed
    conversation_data: dict = Column(JSON, default=dict)
    total_duration: int = Column(Integer, nullable=True)  # seconds
    ai_response_count: int = Column(Integer, default=0)
    user_input_count: int = Column(Integer, default=0)
    knowledge_queries: int = Column(Integer, default=0)
    error_count: int = Column(Integer, default=0)
```

### 2. Conversation Turn Model

```python
class ConversationTurn(Base):
    __tablename__ = "conversation_turns"
    
    id: str = Column(String, primary_key=True)
    call_session_id: str = Column(String, ForeignKey("call_sessions.id"))
    turn_number: int = Column(Integer, nullable=False)
    timestamp: datetime = Column(DateTime, default=datetime.utcnow)
    user_input: str = Column(Text, nullable=True)
    ai_response: str = Column(Text, nullable=True)
    knowledge_used: dict = Column(JSON, nullable=True)
    response_time_ms: int = Column(Integer, nullable=True)
    audio_duration_ms: int = Column(Integer, nullable=True)
```

### 3. System Metrics Model

```python
class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id: str = Column(String, primary_key=True)
    timestamp: datetime = Column(DateTime, default=datetime.utcnow)
    metric_type: str = Column(String, nullable=False)  # api_response_time, error_rate, etc.
    metric_value: float = Column(Float, nullable=False)
    service_name: str = Column(String, nullable=False)  # openai, elevenlabs, twilio
    additional_data: dict = Column(JSON, nullable=True)
```

## Error Handling

### 1. Service Failure Handling

```python
class ServiceFailureHandler:
    """Handles failures of external services"""
    
    async def handle_openai_failure(self, call_id: str, error: Exception)
    async def handle_elevenlabs_failure(self, call_id: str, error: Exception)
    async def handle_twilio_failure(self, call_id: str, error: Exception)
    async def provide_fallback_response(self, call_id: str, context: str)
```

### 2. Fallback Mechanisms

- **OpenAI Failure**: Use pre-defined response templates based on common queries
- **ElevenLabs Failure**: Use system TTS or pre-recorded audio files
- **Database Failure**: Continue conversation but log errors for later processing
- **Network Issues**: Implement retry logic with exponential backoff

### 3. Graceful Degradation

- Maintain conversation flow even with service failures
- Provide clear communication to caller about any limitations
- Log all errors for post-call analysis and improvement

## Testing Strategy

### 1. Unit Testing

- **Conversation Manager**: Test conversation flow logic and state management
- **Voice Services**: Test OpenAI and ElevenLabs integration with mocked responses
- **Knowledge Base**: Test search and retrieval functionality
- **Error Handlers**: Test all failure scenarios and fallback mechanisms

### 2. Integration Testing

- **End-to-End Call Flow**: Test complete call from Twilio to response
- **Service Integration**: Test all external API integrations
- **Database Operations**: Test all database read/write operations
- **WebSocket Handling**: Test ConversationRelay connection management

### 3. Load Testing

- **Concurrent Calls**: Test system with multiple simultaneous calls
- **API Rate Limits**: Test behavior under API rate limiting
- **Memory Usage**: Monitor memory consumption during extended calls
- **Response Times**: Ensure response times meet requirements under load

### 4. Manual Testing

- **Call Quality**: Test actual phone calls for audio quality and responsiveness
- **Conversation Flow**: Test natural conversation patterns and interruptions
- **Knowledge Base**: Test accuracy of knowledge-based responses
- **Error Scenarios**: Manually trigger error conditions to test handling

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
1. Set up ConversationRelay webhook endpoints
2. Implement basic WebSocket handling for ConversationRelay
3. Create conversation session management
4. Set up database models and migrations
5. Implement basic call logging

### Phase 2: AI Integration (Week 2)
1. Integrate OpenAI GPT for conversation generation
2. Implement ElevenLabs text-to-speech integration
3. Create conversation context management
4. Implement basic knowledge base querying
5. Add error handling and fallbacks

### Phase 3: Optimization and Testing (Week 3)
1. Optimize response times and audio quality
2. Implement comprehensive error handling
3. Add performance monitoring and metrics
4. Conduct thorough testing (unit, integration, manual)
5. Create deployment documentation

### Phase 4: Demo Preparation (Week 4)
1. Set up demo environment with sample knowledge base
2. Create monitoring dashboard for demo
3. Prepare demo scripts and scenarios
4. Conduct final testing and bug fixes
5. Document demo setup and usage

## Configuration Requirements

### Environment Variables

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=150

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=default_voice_id
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.75

# System Configuration
BASE_URL=https://your-domain.com
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

### Twilio ConversationRelay Setup

```python
# Webhook configuration for ConversationRelay
CONVERSATION_RELAY_CONFIG = {
    "webhook_url": f"{BASE_URL}/api/v1/voice/conversation-relay",
    "voice_settings": {
        "language": "en-US",
        "speech_timeout": 3,
        "max_speech_duration": 30
    },
    "ai_settings": {
        "response_timeout": 5,
        "max_response_length": 200
    }
}
```

## Performance Targets

- **Call Answer Time**: < 2 seconds
- **AI Response Generation**: < 3 seconds
- **Text-to-Speech Conversion**: < 2 seconds
- **Total Response Time**: < 5 seconds
- **Concurrent Calls**: Support 5+ simultaneous calls
- **Uptime**: 99%+ availability during demo periods
- **Error Rate**: < 5% of interactions

## Security Considerations

### 1. API Security
- Validate all Twilio webhook signatures
- Use HTTPS for all external communications
- Implement rate limiting on webhook endpoints
- Secure storage of API keys in environment variables

### 2. Data Privacy
- Log only necessary conversation data
- Implement data retention policies
- Ensure compliance with privacy regulations
- Secure database connections and access

### 3. System Security
- Regular security updates for all dependencies
- Monitor for unusual call patterns or abuse
- Implement basic DDoS protection
- Secure webhook endpoints against unauthorized access

## Monitoring and Observability

### 1. Key Metrics
- Call volume and success rates
- Average response times for each service
- Error rates by service and error type
- System resource usage (CPU, memory, network)

### 2. Logging Strategy
- Structured logging with correlation IDs
- Different log levels for different environments
- Centralized log aggregation
- Real-time error alerting

### 3. Health Checks
- Service health endpoints for all components
- Database connectivity checks
- External API availability checks
- System resource monitoring

This design provides a solid foundation for building a working AI voice agent MVP that demonstrates the core functionality while being maintainable and scalable for future enhancements.