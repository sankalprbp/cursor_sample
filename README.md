# AI Voice Agent MVP 🤖📞

A working AI voice agent that can receive phone calls and have natural conversations using OpenAI GPT, ElevenLabs voice synthesis, and Twilio ConversationRelay.

## 🎯 What This Does

- **Answers Phone Calls**: Real AI agent that picks up when someone calls
- **Natural Conversations**: Uses OpenAI GPT for intelligent responses
- **Realistic Voice**: ElevenLabs provides human-like speech synthesis
- **Real-time Processing**: Twilio ConversationRelay for live voice streaming
- **Knowledge Integration**: AI can answer questions from your knowledge base
- **Call Management**: Complete logging and analytics

## 🚀 Quick Start (5 Minutes)

### 1. Get Your API Keys

You'll need accounts and API keys from:
- **OpenAI**: https://platform.openai.com/api-keys
- **ElevenLabs**: https://elevenlabs.io/app/speech-synthesis  
- **Twilio**: https://console.twilio.com/ (buy a phone number)

### 2. Setup & Run

```bash
# Clone and setup
git clone <your-repo>
cd voice-agent-platform

# Configure your API keys
cp .env.example .env
# Edit .env with your actual API keys

# Start the system
docker-compose up --build

# System will be ready at:
# - Backend: http://localhost:8000
# - Health Check: http://localhost:8000/health
# - API Docs: http://localhost:8000/docs
```

### 3. Configure Twilio Webhooks

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Phone Numbers > Active Numbers**
3. Click your phone number
4. Set **Voice Webhook**: `http://your-public-url:8000/api/v1/voice/twilio/webhook/{call_id}`
5. Set **Status Callback**: `http://your-public-url:8000/api/v1/voice/twilio/status/{call_id}`

### 4. Test It!

Call your Twilio phone number and have a conversation with your AI agent!

## 📋 Complete Setup Guide

For detailed setup instructions, see: **[MVP_SETUP_GUIDE.md](MVP_SETUP_GUIDE.md)**

## 🧪 Testing Your Setup

For comprehensive testing instructions, see: **[TESTING_GUIDE.md](TESTING_GUIDE.md)**

## 🛠 Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **AI**: OpenAI GPT-4 for conversations
- **Voice**: ElevenLabs for text-to-speech
- **Telephony**: Twilio ConversationRelay for real-time voice
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose

## 📁 Project Structure

```
voice-agent-platform/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── models/            # Database models
│   │   └── core/              # Configuration
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container
├── frontend/                  # Next.js frontend (optional)
├── .env.example              # Environment template
├── docker-compose.yml        # Development environment
├── MVP_SETUP_GUIDE.md        # Detailed setup instructions
├── TESTING_GUIDE.md          # Testing procedures
└── README.md                 # This file
```

## 🔧 Configuration

### Required Environment Variables

```bash
# AI Services (REQUIRED)
OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# Twilio (REQUIRED for phone calls)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# System Configuration
DATABASE_URL=sqlite+aiosqlite:///./voice_agent.db
REDIS_URL=redis://redis:6379/0
BASE_URL=http://localhost:8000
SECRET_KEY=your-secret-key
```

## 🎯 Key Features

### ✅ Implemented
- Real-time voice conversations via Twilio ConversationRelay
- OpenAI GPT integration for intelligent responses
- ElevenLabs text-to-speech for natural voice
- WebSocket handling for live audio streaming
- Call logging and transcript storage
- Knowledge base integration
- Docker containerization
- Comprehensive error handling

### 🚧 In Development
- Frontend dashboard (basic structure exists)
- Multi-tenant support (backend ready)
- Advanced analytics
- Billing integration

## 📞 How It Works

1. **Caller dials your Twilio number**
2. **Twilio connects to ConversationRelay** (real-time voice streaming)
3. **AI agent answers** with personalized greeting
4. **Speech-to-text** converts caller's voice to text
5. **OpenAI GPT** generates intelligent response
6. **ElevenLabs** converts response to natural speech
7. **Audio streams back** to caller in real-time
8. **Conversation continues** naturally with context awareness

## 🔍 Troubleshooting

### Common Issues

**"OpenAI API Error"**
- Verify API key in `.env`
- Check account has credits
- Visit: https://platform.openai.com/account/usage

**"ElevenLabs API Error"**  
- Verify API key in `.env`
- Check monthly character limit
- Visit: https://elevenlabs.io/app/speech-synthesis

**"Twilio Webhook Not Working"**
- Use ngrok for local testing: `ngrok http 8000`
- Update Twilio webhook URL with ngrok URL
- Ensure `BASE_URL` matches your public URL

**"No Audio/Poor Quality"**
- Check ElevenLabs voice settings
- Verify audio processing dependencies
- Test with different voice IDs

### Debug Commands

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f backend

# Test health
curl http://localhost:8000/health

# Check specific service
docker-compose logs redis
```

## 📊 Performance

### Target Metrics
- **Call Answer**: < 3 seconds
- **AI Response**: < 5 seconds  
- **Audio Generation**: < 2 seconds
- **Total Response**: < 8 seconds
- **Concurrent Calls**: 5+

### Monitoring
```bash
# System resources
docker stats

# Response times
docker-compose logs backend | grep "response_time"

# Error rates  
docker-compose logs backend | grep -i error
```

## 🚀 Deployment

### Local Development
```bash
docker-compose up --build
```

### Production Deployment
1. Deploy to cloud provider (AWS, GCP, Azure)
2. Configure SSL/HTTPS
3. Update Twilio webhooks to production URLs
4. Set production environment variables
5. Configure monitoring and alerts

## 📚 Documentation

- **[MVP_SETUP_GUIDE.md](MVP_SETUP_GUIDE.md)**: Complete setup instructions
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)**: Testing procedures and debugging
- **[MVP_IMPLEMENTATION_PLAN.md](MVP_IMPLEMENTATION_PLAN.md)**: Technical implementation details
- **API Docs**: http://localhost:8000/docs (when running)

## 🎉 Success Criteria

Your MVP is working when:
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] You can call your Twilio number
- [ ] AI answers with a greeting
- [ ] You can have a natural conversation
- [ ] AI responses are relevant and coherent
- [ ] Voice quality is clear and natural
- [ ] Calls are logged in the system

## 💡 Next Steps

Once your MVP is working:
1. **Add Knowledge Base**: Upload company documents for AI to reference
2. **Customize Voice**: Try different ElevenLabs voices and settings
3. **Improve Prompts**: Enhance AI personality and response quality
4. **Add Analytics**: Monitor call performance and user satisfaction
5. **Scale Up**: Deploy to production environment

## 🆘 Support

If you need help:
1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Verify all API keys are correct
4. Test each service individually
5. Check service status pages (OpenAI, ElevenLabs, Twilio)

## 📄 License

MIT License - see LICENSE file for details.

---

**🎯 Goal**: Get a working AI voice agent answering phone calls within 30 minutes!