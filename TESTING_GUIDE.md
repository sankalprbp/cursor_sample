# AI Voice Agent MVP - Testing Guide

## 🧪 Testing Strategy

This guide covers how to test your AI Voice Agent MVP to ensure it's working correctly before going live.

## 📋 Pre-Testing Checklist

### 1. Environment Setup
- [ ] All API keys configured in `.env`
- [ ] Docker services running
- [ ] Health check passes
- [ ] Database initialized
- [ ] Redis connected

### 2. Service Validation
```bash
# Check all services are running
docker-compose ps

# Verify health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

### 3. API Key Validation
```bash
# Test OpenAI connection
curl -X POST "http://localhost:8000/api/v1/voice/test/openai" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}'

# Test ElevenLabs connection
curl -X POST "http://localhost:8000/api/v1/voice/test/elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}'

# Test Twilio connection
curl http://localhost:8000/api/v1/voice/twilio/status
```

## 🎯 Testing Phases

### Phase 1: Component Testing

#### 1.1 Test Voice Agent Service
```bash
# Start a test conversation
curl -X POST "http://localhost:8000/api/v1/voice/calls/start" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "caller_number": "+1234567890",
    "tenant_id": "your-tenant-id"
  }'

# Send text input (simulates speech-to-text)
curl -X POST "http://localhost:8000/api/v1/voice/calls/{call_id}/input/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "call_id": "your-call-id",
    "text": "Hello, how are you today?"
  }'
```

#### 1.2 Test Audio Processing
```bash
# Upload audio file for testing
curl -X POST "http://localhost:8000/api/v1/voice/calls/{call_id}/input/audio" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "audio_file=@test_audio.wav"
```

#### 1.3 Test Knowledge Base Integration
```bash
# Upload test knowledge document
curl -X POST "http://localhost:8000/api/v1/knowledge/documents" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@company_info.pdf"

# Test knowledge query
curl -X POST "http://localhost:8000/api/v1/voice/calls/{call_id}/input/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "call_id": "your-call-id",
    "text": "What are your business hours?"
  }'
```

### Phase 2: Integration Testing

#### 2.1 Test Twilio Webhook Integration

1. **Set up ngrok for local testing**:
```bash
# Install ngrok (if not already installed)
# Download from: https://ngrok.com/download

# Expose local port 8000
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

2. **Update Twilio webhook configuration**:
   - Go to [Twilio Console](https://console.twilio.com/)
   - Navigate to Phone Numbers > Manage > Active numbers
   - Click your phone number
   - Set webhook URL: `https://your-ngrok-url.ngrok.io/api/v1/voice/twilio/webhook/{call_id}`

3. **Test webhook reception**:
```bash
# Monitor webhook logs
docker-compose logs -f backend | grep "webhook"

# Make a test call to your Twilio number
# Check logs for webhook reception
```

#### 2.2 Test ConversationRelay WebSocket

1. **Test WebSocket connection**:
```bash
# Use wscat to test WebSocket (install with: npm install -g wscat)
wscat -c "ws://localhost:8000/api/v1/voice/conversation-relay/test-call-id"

# Send test message
{"event": "connected", "protocol": "Call", "version": "1.0.0"}
```

2. **Test audio streaming**:
```bash
# Send media event with base64 audio
{
  "event": "media",
  "sequenceNumber": "1",
  "media": {
    "track": "inbound",
    "chunk": "1",
    "timestamp": "1234567890",
    "payload": "base64-encoded-audio-data"
  },
  "streamSid": "test-stream-id"
}
```

### Phase 3: End-to-End Testing

#### 3.1 Complete Call Flow Test

1. **Prepare test environment**:
```bash
# Ensure all services are running
docker-compose up -d

# Check system status
curl http://localhost:8000/health
```

2. **Make test call**:
   - Call your Twilio phone number
   - Verify AI answers with greeting
   - Have a conversation
   - Check call is logged properly

3. **Verify call data**:
```bash
# Get call list
curl -X GET "http://localhost:8000/api/v1/voice/calls" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get specific call details
curl -X GET "http://localhost:8000/api/v1/voice/calls/{call_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3.2 Performance Testing

1. **Response time testing**:
```bash
# Time API responses
time curl -X POST "http://localhost:8000/api/v1/voice/calls/{call_id}/input/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"call_id": "test", "text": "What time is it?"}'
```

2. **Concurrent call testing**:
```bash
# Simulate multiple calls (requires multiple Twilio numbers or test framework)
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/voice/calls/start" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -d "{\"caller_number\": \"+123456789$i\"}" &
done
wait
```

## 🔍 Debugging Common Issues

### Issue 1: "OpenAI API Error"
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check OpenAI account credits
# Visit: https://platform.openai.com/account/usage
```

### Issue 2: "ElevenLabs API Error"
```bash
# Check API key
echo $ELEVENLABS_API_KEY

# Test API key directly
curl -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"

# Check ElevenLabs usage
# Visit: https://elevenlabs.io/app/speech-synthesis
```

### Issue 3: "Twilio Webhook Not Received"
```bash
# Check ngrok is running
curl http://127.0.0.1:4040/api/tunnels

# Verify webhook URL in Twilio console
# Check firewall settings
# Verify BASE_URL in .env matches ngrok URL
```

### Issue 4: "ConversationRelay Connection Failed"
```bash
# Check WebSocket endpoint
wscat -c "ws://localhost:8000/api/v1/voice/conversation-relay/test"

# Check logs for WebSocket errors
docker-compose logs backend | grep -i websocket

# Verify Twilio stream configuration
```

### Issue 5: "Audio Quality Issues"
```bash
# Check audio processing logs
docker-compose logs backend | grep -i audio

# Test audio conversion
# Upload test audio file and check output quality

# Verify ElevenLabs voice settings
# Try different voice IDs and stability settings
```

## 📊 Performance Benchmarks

### Target Performance Metrics
- **Call Answer Time**: < 3 seconds
- **AI Response Generation**: < 5 seconds
- **Audio Processing**: < 2 seconds
- **Total Response Time**: < 8 seconds
- **Concurrent Calls**: 5+ simultaneous

### Monitoring Commands
```bash
# Monitor system resources
docker stats

# Check response times
docker-compose logs backend | grep "response_time"

# Monitor API usage
curl http://localhost:8000/api/v1/admin/metrics

# Check error rates
docker-compose logs backend | grep -i error | wc -l
```

## 🧪 Test Scenarios

### Scenario 1: Basic Greeting
1. Call Twilio number
2. **Expected**: AI answers with personalized greeting
3. **Verify**: Greeting mentions company name and agent name

### Scenario 2: Simple Question
1. Ask: "What are your business hours?"
2. **Expected**: AI provides business hours from knowledge base
3. **Verify**: Response is accurate and natural

### Scenario 3: Complex Query
1. Ask: "Can you help me with pricing for your premium service?"
2. **Expected**: AI provides relevant pricing information
3. **Verify**: Information is from knowledge base, not hallucinated

### Scenario 4: Interruption Handling
1. Start asking a question
2. Interrupt AI while it's responding
3. **Expected**: AI stops talking and listens
4. **Verify**: No audio overlap or confusion

### Scenario 5: Unknown Information
1. Ask: "What's the weather like today?"
2. **Expected**: AI politely says it doesn't have that information
3. **Verify**: No hallucinated weather data

### Scenario 6: Long Conversation
1. Have a 5+ minute conversation
2. **Expected**: AI maintains context throughout
3. **Verify**: Responses remain relevant and coherent

## ✅ Test Completion Checklist

### Basic Functionality
- [ ] System starts without errors
- [ ] Health check passes
- [ ] API documentation accessible
- [ ] All services connected

### Voice Agent Core
- [ ] AI responds to text input
- [ ] Responses are relevant and coherent
- [ ] Knowledge base integration works
- [ ] Call logging functions properly

### Twilio Integration
- [ ] Webhooks received successfully
- [ ] ConversationRelay connects
- [ ] Audio streaming works
- [ ] Call status updates properly

### Audio Quality
- [ ] Voice sounds natural and clear
- [ ] No audio artifacts or distortion
- [ ] Appropriate response timing
- [ ] Interruption handling works

### Performance
- [ ] Response times meet targets
- [ ] System handles concurrent calls
- [ ] Memory usage is reasonable
- [ ] No memory leaks detected

### Error Handling
- [ ] Graceful handling of API failures
- [ ] Appropriate fallback responses
- [ ] Error logging is comprehensive
- [ ] System recovers from failures

## 🚀 Production Readiness

### Final Validation
1. **24-hour stability test**: Run system for 24 hours without issues
2. **Load testing**: Handle expected call volume
3. **Security review**: Verify API keys and access controls
4. **Backup verification**: Ensure data backup and recovery works
5. **Monitoring setup**: Alerts and dashboards configured

### Go-Live Checklist
- [ ] Production environment configured
- [ ] SSL certificates installed
- [ ] Domain name configured
- [ ] Twilio webhooks updated to production URLs
- [ ] Monitoring and alerting active
- [ ] Support procedures documented
- [ ] Rollback plan prepared

## 📞 Support and Troubleshooting

### Log Analysis
```bash
# View all logs
docker-compose logs -f

# Filter for errors
docker-compose logs backend | grep -i error

# Search for specific call
docker-compose logs backend | grep "call_id_here"

# Monitor real-time activity
docker-compose logs -f backend | grep -E "(call|conversation|audio)"
```

### Emergency Procedures
1. **System Down**: Restart all services
2. **High Error Rate**: Check API service status
3. **Poor Audio Quality**: Verify ElevenLabs settings
4. **Webhook Failures**: Check network connectivity
5. **Database Issues**: Verify connection and restart if needed

Remember: Test thoroughly in a safe environment before deploying to production!