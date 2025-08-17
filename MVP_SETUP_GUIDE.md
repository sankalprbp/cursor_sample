# AI Voice Agent MVP - Complete Setup Guide

## 🎯 Overview

This guide will help you set up a working AI Voice Agent MVP that can:
- Receive incoming phone calls via Twilio
- Have natural conversations using OpenAI GPT
- Respond with realistic voice using ElevenLabs
- Handle real-time voice conversations
- Log and manage call data

## 📋 Prerequisites

### Required Accounts & API Keys

1. **OpenAI Account** (REQUIRED)
   - Sign up at: https://platform.openai.com/
   - Get API key from: https://platform.openai.com/api-keys
   - Minimum $5 credit recommended

2. **ElevenLabs Account** (REQUIRED)
   - Sign up at: https://elevenlabs.io/
   - Get API key from: https://elevenlabs.io/app/speech-synthesis
   - Free tier includes 10,000 characters/month

3. **Twilio Account** (REQUIRED)
   - Sign up at: https://www.twilio.com/
   - Get Account SID and Auth Token from Console
   - Purchase a phone number ($1/month)
   - $10 credit recommended for testing

### System Requirements

- **Docker & Docker Compose** (REQUIRED)
- **Git** (REQUIRED)
- **Internet connection** for API calls

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd voice-agent-platform

# Copy environment template
cp .env.example .env
```

### Step 2: Configure API Keys

Edit the `.env` file with your actual API keys:

```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# ElevenLabs Configuration (REQUIRED)
ELEVENLABS_API_KEY=your-actual-elevenlabs-key-here

# Twilio Configuration (REQUIRED)
TWILIO_ACCOUNT_SID=your-actual-twilio-account-sid
TWILIO_AUTH_TOKEN=your-actual-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Step 3: Start the System

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### Step 4: Configure Twilio Webhooks

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Phone Numbers > Manage > Active numbers**
3. Click on your purchased phone number
4. In **Voice Configuration** section, set:
   - **Webhook URL**: `http://your-public-url:8000/api/v1/voice/twilio/webhook/{call_id}`
   - **HTTP Method**: POST
   - **Status Callback URL**: `http://your-public-url:8000/api/v1/voice/twilio/status/{call_id}`

### Step 5: Test the System

1. **Health Check**: Visit http://localhost:8000/health
2. **API Docs**: Visit http://localhost:8000/docs
3. **Make a Test Call**: Call your Twilio phone number

## 📞 API Key Setup Instructions

### OpenAI API Key

1. **Create Account**: Go to https://platform.openai.com/
2. **Add Payment Method**: Go to Billing > Payment methods
3. **Add Credits**: Minimum $5 recommended
4. **Create API Key**: 
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - Add to `.env` file: `OPENAI_API_KEY=sk-your-key-here`

### ElevenLabs API Key

1. **Create Account**: Go to https://elevenlabs.io/
2. **Get API Key**:
   - Go to https://elevenlabs.io/app/speech-synthesis
   - Click on your profile (top right)
   - Go to "Profile" > "API Keys"
   - Copy your API key
   - Add to `.env` file: `ELEVENLABS_API_KEY=your-key-here`

### Twilio Setup (Detailed)

1. **Create Account**: Go to https://www.twilio.com/
2. **Get Credentials**:
   - Go to [Twilio Console](https://console.twilio.com/)
   - Copy **Account SID** and **Auth Token**
   - Add to `.env` file

3. **Buy Phone Number**:
   - Go to **Phone Numbers > Manage > Buy a number**
   - Choose a number with **Voice** capability
   - Purchase the number (~$1/month)

4. **Configure Webhooks**:
   - Go to **Phone Numbers > Manage > Active numbers**
   - Click your number
   - Set **Voice Configuration**:
     - Webhook: `http://your-domain.com:8000/api/v1/voice/twilio/webhook/{call_id}`
     - Method: POST
     - Status Callback: `http://your-domain.com:8000/api/v1/voice/twilio/status/{call_id}`

## 🔧 Configuration Details

### Environment Variables Explained

```bash
# Core System
ENVIRONMENT=development          # development/production
DEBUG=true                      # Enable debug logging
LOG_LEVEL=INFO                  # DEBUG/INFO/WARNING/ERROR

# Security
SECRET_KEY=your-secret-key      # JWT signing key (change in production)

# Database
DATABASE_URL=sqlite+aiosqlite:///./voice_agent.db  # SQLite for development

# Redis (for caching and sessions)
REDIS_URL=redis://redis:6379/0

# AI Services
OPENAI_API_KEY=sk-...          # Your OpenAI API key
OPENAI_MODEL=gpt-4             # GPT model to use
OPENAI_MAX_TOKENS=150          # Max response length
OPENAI_TEMPERATURE=0.7         # Response creativity (0.0-1.0)

ELEVENLABS_API_KEY=...         # Your ElevenLabs API key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Voice to use
ELEVENLABS_STABILITY=0.5       # Voice stability (0.0-1.0)
ELEVENLABS_SIMILARITY_BOOST=0.75  # Voice similarity (0.0-1.0)

# Twilio
TWILIO_ACCOUNT_SID=...         # Your Twilio Account SID
TWILIO_AUTH_TOKEN=...          # Your Twilio Auth Token
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number

# System URLs
BASE_URL=http://localhost:8000  # Your public URL for webhooks
ALLOWED_ORIGINS=http://localhost:3000  # Frontend URL
```

### Voice Configuration Options

You can customize the AI voice by changing these settings in `.env`:

```bash
# Different ElevenLabs voices (popular options)
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default)
ELEVENLABS_VOICE_ID=AZnzlk1XvdvUeBnXmlld  # Domi
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL  # Bella
ELEVENLABS_VOICE_ID=ErXwobaYiN019PkySvjV  # Antoni
ELEVENLABS_VOICE_ID=MF3mGyEYCl7XYWbV9V6O  # Elli
ELEVENLABS_VOICE_ID=TxGEqnHWrfWFTfGW9XjX  # Josh

# Voice quality settings
ELEVENLABS_STABILITY=0.5        # Lower = more expressive, Higher = more stable
ELEVENLABS_SIMILARITY_BOOST=0.75  # How similar to original voice
```

## 🧪 Testing Your Setup

### 1. Health Check

```bash
# Check if all services are running
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### 2. API Documentation

Visit http://localhost:8000/docs to see interactive API documentation.

### 3. Test Voice Agent (Without Phone)

```bash
# Start a test conversation
curl -X POST "http://localhost:8000/api/v1/voice/calls/start" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"caller_number": "+1234567890"}'

# Send text input (for testing)
curl -X POST "http://localhost:8000/api/v1/voice/calls/{call_id}/input/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"call_id": "your-call-id", "text": "Hello, how are you?"}'
```

### 4. Test Phone Call

1. Call your Twilio phone number
2. You should hear the AI greeting
3. Speak naturally - the AI will respond
4. Check logs: `docker-compose logs -f backend`

## 🔍 Troubleshooting

### Common Issues

#### 1. "OpenAI API key not found"
- Check your `.env` file has `OPENAI_API_KEY=sk-...`
- Verify the key is valid at https://platform.openai.com/api-keys
- Ensure you have credits in your OpenAI account

#### 2. "ElevenLabs API error"
- Check your `.env` file has `ELEVENLABS_API_KEY=...`
- Verify the key at https://elevenlabs.io/app/speech-synthesis
- Check if you've exceeded your monthly character limit

#### 3. "Twilio webhook not working"
- Ensure your `BASE_URL` is publicly accessible
- Use ngrok for local testing: `ngrok http 8000`
- Update Twilio webhook URL with your ngrok URL
- Check Twilio webhook logs in console

#### 4. "Database connection error"
- Ensure Redis is running: `docker-compose ps`
- Check Redis logs: `docker-compose logs redis`
- Restart services: `docker-compose restart`

#### 5. "Call not connecting"
- Verify Twilio phone number is correct
- Check Twilio account balance
- Ensure webhook URLs are configured correctly
- Check backend logs: `docker-compose logs backend`

### Debug Commands

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f redis

# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up --build

# Check environment variables
docker-compose exec backend env | grep -E "(OPENAI|ELEVENLABS|TWILIO)"
```

## 🌐 Public URL Setup (For Webhooks)

### Option 1: ngrok (Recommended for Testing)

```bash
# Install ngrok
# Download from: https://ngrok.com/download

# Expose local port 8000
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update your .env file:
BASE_URL=https://abc123.ngrok.io

# Update Twilio webhooks with the ngrok URL
```

### Option 2: Cloud Deployment

For production, deploy to:
- **AWS EC2** with Elastic IP
- **Google Cloud Platform**
- **DigitalOcean Droplet**
- **Heroku** (with custom domain)

## 📊 Monitoring & Logs

### View Real-time Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Filter for errors
docker-compose logs backend | grep ERROR
```

### Check System Status

```bash
# Health check
curl http://localhost:8000/health

# Twilio status
curl http://localhost:8000/api/v1/voice/twilio/status
```

## 🎉 Success Checklist

- [ ] All API keys configured in `.env`
- [ ] Docker services running (`docker-compose ps`)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Twilio webhooks configured
- [ ] Test call connects and AI responds
- [ ] Voice quality is acceptable
- [ ] Conversation flows naturally

## 📞 Demo Script

Once everything is working, try this conversation:

1. **Call your Twilio number**
2. **AI**: "Hello! This is [Agent Name] from [Company]. How can I help you today?"
3. **You**: "Hi, I'm interested in your services."
4. **AI**: [Responds based on knowledge base]
5. **You**: "What are your hours?"
6. **AI**: [Provides information or asks for clarification]

## 🚀 Next Steps

Once your MVP is working:

1. **Add Knowledge Base**: Upload company documents
2. **Customize Voice**: Try different ElevenLabs voices
3. **Improve Prompts**: Enhance AI personality and responses
4. **Add Analytics**: Monitor call performance
5. **Scale Up**: Deploy to production environment

## 💡 Tips for Success

1. **Start Simple**: Get basic calling working first
2. **Test Frequently**: Make test calls during setup
3. **Monitor Costs**: Watch API usage and billing
4. **Keep Logs**: Save successful configurations
5. **Iterate**: Improve based on real conversations

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Verify API keys and configuration
4. Test each service individually
5. Check service status pages (OpenAI, ElevenLabs, Twilio)

---

**🎯 Goal**: Have a working AI voice agent that can answer phone calls and have natural conversations within 30 minutes of setup!