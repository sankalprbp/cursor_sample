# AI Voice Agent MVP - Complete Setup Guide

## 🎯 Overview

This guide will help you set up a working AI Voice Agent MVP that can:
- Receive incoming phone calls via Twilio
- Have natural conversations using OpenAI GPT
- Respond with realistic voice using ElevenLabs
- Handle real-time voice conversations with Media Streams
- Display beautiful dashboard with call logs and transcripts
- Automatically expose to public internet using ngrok

## � One-Click Setup (2 Minutes!)

### Prerequisites
- **Docker Desktop** installed and running
- **Git** installed
- **Internet connection**

### Step 1: Get Your API Keys (1 minute)

You need these 3 accounts (all have free tiers):

1. **OpenAI** → https://platform.openai.com/api-keys
2. **ElevenLabs** → https://elevenlabs.io/app/speech-synthesis  
3. **Twilio** → https://console.twilio.com/ (buy a phone number)

### Step 2: One-Click Setup

**Windows (PowerShell):**
```powershell
# Clone and setup
git clone <your-repo-url>
cd voice-agent-platform

# Copy environment template
Copy-Item .env.example .env

# Edit .env with your API keys (use notepad or any editor)
notepad .env

# Run the complete setup script
.\setup-mvp.ps1
```

**macOS/Linux (Bash):**
```bash
# Clone and setup
git clone <your-repo-url>
cd voice-agent-platform

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or vim, code, etc.

# Run the complete setup script
./setup-mvp.sh
```

### Step 3: Configure Twilio (30 seconds)

The setup script will give you the exact URLs to copy into Twilio:

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Phone Numbers > Active Numbers**
3. Click your phone number
4. Copy the webhook URLs from the setup script output
5. Save configuration

### Step 4: Test Your AI Agent

**Call your Twilio phone number** - your AI agent will answer!

## 🎉 What the Setup Script Does

### Automatic Setup Includes:
- ✅ **Validates all API keys** and configuration
- ✅ **Starts Docker services** (backend, frontend, database, cache)
- ✅ **Installs and configures ngrok** for public access
- ✅ **Creates secure tunnel** to expose your local server
- ✅ **Updates configuration** with public URLs
- ✅ **Runs health checks** to ensure everything works
- ✅ **Provides exact Twilio configuration** URLs
- ✅ **Monitors system** and keeps tunnel alive

### What You Get:
- 🎯 **Beautiful Dashboard** at http://localhost:3000
- 📞 **Working AI Phone Agent** that answers calls
- 📊 **Real-time Call Logs** and transcripts
- 🌐 **Public URL** via ngrok for Twilio webhooks
- 🔍 **System Monitoring** and health checks
- 📱 **Mobile-responsive** interface

## 🎨 Beautiful Dashboard Features

### Real-time Dashboard
- **Live Call Monitoring** - See active calls in real-time
- **Call Statistics** - Total calls, success rate, average duration
- **System Health** - Database, Redis, and service status
- **Interactive Charts** - Visual call analytics

### Call Management
- **Call History** - Complete log of all calls with details
- **Transcripts** - Full conversation transcripts for each call
- **Call Summaries** - AI-generated summaries of conversations
- **Search & Filter** - Find specific calls quickly

### System Monitoring
- **Health Checks** - Real-time system status monitoring
- **Error Tracking** - Comprehensive error logging and alerts
- **Performance Metrics** - Response times and system performance
- **Service Status** - Individual service health indicators

## 📞 Detailed API Key Setup

### OpenAI API Key (Required)

1. **Create Account**: Go to https://platform.openai.com/
2. **Add Payment Method**: Go to Billing > Payment methods
3. **Add Credits**: Minimum $5 recommended for testing
4. **Create API Key**: 
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - Add to `.env` file: `OPENAI_API_KEY=sk-your-key-here`

### ElevenLabs API Key (Required)

1. **Create Account**: Go to https://elevenlabs.io/
2. **Get API Key**:
   - Go to https://elevenlabs.io/app/speech-synthesis
   - Click on your profile (top right)
   - Go to "Profile" > "API Keys"
   - Copy your API key
   - Add to `.env` file: `ELEVENLABS_API_KEY=your-key-here`

### Twilio Setup (Required)

1. **Create Account**: Go to https://www.twilio.com/
2. **Get Credentials**:
   - Go to [Twilio Console](https://console.twilio.com/)
   - Copy **Account SID** and **Auth Token**
   - Add to `.env` file

3. **Buy Phone Number**:
   - Go to **Phone Numbers > Manage > Buy a number**
   - Choose a number with **Voice** capability
   - Purchase the number (~$1/month)

4. **Configure Webhooks** (Done automatically by setup script):
   - The setup script provides exact URLs to copy
   - Just paste them into Twilio Console as instructed

### ngrok Setup (Automatic)

The setup script automatically:
- **Installs ngrok** if not present
- **Authenticates ngrok** (you provide the token)
- **Creates secure tunnel** to your local server
- **Updates configuration** with public URLs
- **Provides Twilio webhook URLs** ready to copy

## 🔧 Advanced Configuration

### Environment Variables Explained

The setup script creates a minimal `.env` file with only required variables:

```bash
# Core System
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=dev-secret-key-change-in-production-12345

# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./voice_agent.db

# Redis Cache
REDIS_URL=redis://redis:6379/0

# AI Services (REQUIRED - Add your actual keys)
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=150
OPENAI_TEMPERATURE=0.7

ELEVENLABS_API_KEY=your-elevenlabs-key-here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.75

# Twilio (REQUIRED - Add your actual credentials)
TWILIO_ACCOUNT_SID=your-twilio-account-sid-here
TWILIO_AUTH_TOKEN=your-twilio-auth-token-here
TWILIO_PHONE_NUMBER=+1234567890

# System URLs (Updated automatically by setup script)
BASE_URL=http://localhost:8000  # Changes to ngrok URL
ALLOWED_ORIGINS=http://localhost:3000
WEBHOOK_SECRET=dev-webhook-secret-change-in-production
```

### Voice Customization Options

Try different ElevenLabs voices by changing the `ELEVENLABS_VOICE_ID`:

```bash
# Popular voice options
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default, female)
ELEVENLABS_VOICE_ID=AZnzlk1XvdvUeBnXmlld  # Domi (female)
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL  # Bella (female)
ELEVENLABS_VOICE_ID=ErXwobaYiN019PkySvjV  # Antoni (male)
ELEVENLABS_VOICE_ID=MF3mGyEYCl7XYWbV9V6O  # Elli (female)
ELEVENLABS_VOICE_ID=TxGEqnHWrfWFTfGW9XjX  # Josh (male)

# Voice quality settings
ELEVENLABS_STABILITY=0.5        # 0.0 = more expressive, 1.0 = more stable
ELEVENLABS_SIMILARITY_BOOST=0.75  # 0.0 = more variation, 1.0 = more similar
```

## 🧪 Testing Your Setup

### 1. Automated Health Checks

The setup script automatically tests:
- ✅ **Backend API** health endpoint
- ✅ **Database** connectivity  
- ✅ **Redis** cache connection
- ✅ **Frontend** accessibility
- ✅ **ngrok tunnel** functionality

### 2. Dashboard Access

Visit your dashboard at **http://localhost:3000**:
- **Real-time stats** - See system metrics
- **Call history** - View all calls and transcripts  
- **System status** - Monitor service health
- **Beautiful UI** - Mobile-responsive design

### 3. API Documentation

Interactive API docs at **http://localhost:8000/docs**:
- **Test endpoints** directly in browser
- **View schemas** and request/response formats
- **Authentication** examples and flows

### 4. Phone Call Testing

**Call your Twilio phone number** and:
1. **AI should answer** within 2-3 seconds
2. **Have a conversation** - speak naturally
3. **Check dashboard** for real-time call logs
4. **View transcript** after call ends

## 🔍 Troubleshooting

### Setup Script Issues

#### "API Keys Missing"
**Problem**: Setup script reports missing API keys
**Solution**: 
1. Edit `.env` file with actual API keys (not placeholder values)
2. Ensure no extra spaces or quotes around keys
3. Restart setup script after updating keys

#### "Docker Not Running"
**Problem**: Docker daemon not accessible
**Solution**:
1. **Windows**: Start Docker Desktop
2. **Mac**: Start Docker Desktop  
3. **Linux**: `sudo systemctl start docker`
4. Wait for Docker to fully start, then retry

#### "ngrok Authentication Failed"
**Problem**: ngrok requires authentication
**Solution**:
1. Go to https://dashboard.ngrok.com/get-started/your-authtoken
2. Sign up for free account
3. Copy your authtoken
4. Enter when prompted by setup script

### Runtime Issues

#### "Backend Health Check Failed"
**Problem**: Backend not responding
**Solution**:
```bash
# Check backend logs
docker-compose logs backend

# Common fixes:
docker-compose restart backend
docker-compose up --build backend
```

#### "Twilio Webhooks Not Working"
**Problem**: Calls connect but AI doesn't respond
**Solution**:
1. **Check ngrok tunnel**: Visit ngrok URL in browser
2. **Verify webhook URLs**: Must match setup script output exactly
3. **Check Twilio logs**: Console > Monitor > Logs
4. **Test webhook**: `curl YOUR_NGROK_URL/health`

#### "AI Not Responding"
**Problem**: Call connects but no AI voice
**Solution**:
1. **Check API keys**: Verify OpenAI and ElevenLabs keys are valid
2. **Check credits**: Ensure accounts have sufficient credits
3. **View logs**: `docker-compose logs backend | grep -i error`
4. **Test APIs**: Visit http://localhost:8000/docs

#### "Poor Audio Quality"
**Problem**: Robotic or distorted voice
**Solution**:
1. **Try different voice**: Change `ELEVENLABS_VOICE_ID` in `.env`
2. **Adjust settings**: Modify `ELEVENLABS_STABILITY` (0.3-0.8)
3. **Check connection**: Ensure stable internet connection
4. **Restart services**: `docker-compose restart`

### Debug Commands

```bash
# Complete system status
docker-compose ps
curl http://localhost:8000/health

# View all logs in real-time
docker-compose logs -f

# Check specific service
docker-compose logs backend | tail -50
docker-compose logs frontend | tail -20

# Test individual components
curl http://localhost:8000/docs          # API docs
curl http://localhost:3000               # Frontend
curl YOUR_NGROK_URL/health              # Public access

# Restart everything
docker-compose down
docker-compose up --build

# Emergency reset
docker-compose down -v  # Removes volumes
docker system prune -f  # Cleans Docker
./setup-mvp.sh          # Fresh start
```

### Getting Help

#### Check These First:
1. **Setup script output** - Look for error messages
2. **Docker logs** - `docker-compose logs -f`
3. **ngrok status** - Visit http://localhost:4040
4. **API documentation** - http://localhost:8000/docs
5. **Dashboard** - http://localhost:3000

#### Common Log Locations:
- **Backend errors**: `docker-compose logs backend`
- **Frontend issues**: `docker-compose logs frontend`  
- **Database problems**: `docker-compose logs postgres`
- **ngrok issues**: Check `ngrok.log` file

#### Still Need Help?
1. **Run setup script again** - Often fixes configuration issues
2. **Check service status pages**:
   - OpenAI: https://status.openai.com/
   - ElevenLabs: https://status.elevenlabs.io/
   - Twilio: https://status.twilio.com/
3. **Verify account limits** - Check API usage and credits

## � SuccessU Checklist

After running the setup script, verify these items:

### ✅ System Health
- [ ] **Setup script completed** without errors
- [ ] **Docker services running**: `docker-compose ps` shows all services up
- [ ] **Backend healthy**: Visit http://localhost:8000/health
- [ ] **Frontend accessible**: Visit http://localhost:3000
- [ ] **ngrok tunnel active**: Public URL working

### ✅ API Integration  
- [ ] **OpenAI connected**: No API key errors in logs
- [ ] **ElevenLabs working**: Voice synthesis functioning
- [ ] **Twilio configured**: Webhook URLs set correctly
- [ ] **Database connected**: SQLite/PostgreSQL accessible
- [ ] **Redis running**: Cache service operational

### ✅ Phone Testing
- [ ] **Call connects**: Twilio number answers
- [ ] **AI responds**: Voice agent speaks greeting
- [ ] **Conversation flows**: Natural back-and-forth dialog
- [ ] **Call logs**: Dashboard shows call history
- [ ] **Transcripts saved**: Full conversation recorded

## 📞 Demo Conversation Script

Test your AI agent with this sample conversation:

**📱 Call your Twilio number**

**🤖 AI**: "Hello! This is your AI assistant. How can I help you today?"

**👤 You**: "Hi, what can you tell me about your services?"

**🤖 AI**: "I'd be happy to help you learn about our services. What specific area are you interested in?"

**👤 You**: "What are your business hours?"

**🤖 AI**: [Responds with configured business information]

**👤 You**: "Thank you, that's helpful!"

**🤖 AI**: "You're welcome! Is there anything else I can help you with today?"

## 🚀 Next Steps After MVP

### Immediate Improvements (Day 1)
1. **Upload Knowledge Base**:
   - Add company documents, FAQs, product info
   - Test AI responses with your specific content
   
2. **Customize AI Personality**:
   - Edit system prompts for your brand voice
   - Adjust response style and tone

3. **Test Different Scenarios**:
   - Try various conversation types
   - Test edge cases and error handling

### Short-term Enhancements (Week 1)
1. **Voice Optimization**:
   - Try different ElevenLabs voices
   - Adjust stability and similarity settings
   - Test audio quality on different devices

2. **Dashboard Customization**:
   - Add your company branding
   - Configure analytics preferences
   - Set up monitoring alerts

3. **Performance Tuning**:
   - Monitor response times
   - Optimize for your call volume
   - Test concurrent call handling

### Production Deployment (Month 1)
1. **Cloud Deployment**:
   - Deploy to AWS, GCP, or Azure
   - Set up production database
   - Configure SSL certificates

2. **Advanced Features**:
   - Multi-language support
   - Advanced analytics
   - CRM integration
   - Billing and usage tracking

## 💡 Pro Tips

### Optimization Tips
- **Response Speed**: Keep AI responses under 200 words for natural flow
- **Voice Quality**: Test different voices with your target audience
- **Error Handling**: Always have fallback responses ready
- **Monitoring**: Set up alerts for system issues

### Cost Management
- **OpenAI**: Monitor token usage, use GPT-3.5 for simple responses
- **ElevenLabs**: Track character usage, cache common responses
- **Twilio**: Monitor call minutes and SMS usage
- **Infrastructure**: Use appropriate instance sizes

### Security Best Practices
- **API Keys**: Never commit keys to version control
- **Webhooks**: Validate Twilio signatures
- **Access Control**: Implement proper authentication
- **Data Privacy**: Follow GDPR/CCPA guidelines

## 🆘 Emergency Procedures

### System Down
```bash
# Quick restart
docker-compose restart

# Full rebuild
docker-compose down
docker-compose up --build

# Emergency reset
docker-compose down -v
./setup-mvp.sh
```

### High Error Rate
1. **Check API status pages**
2. **Verify account credits/limits**
3. **Review recent configuration changes**
4. **Check system resource usage**

### Poor Call Quality
1. **Test different ElevenLabs voices**
2. **Check internet connection stability**
3. **Verify Twilio account status**
4. **Monitor system performance**

## 📊 Monitoring Your System

### Key Metrics to Watch
- **Call Success Rate**: Should be >95%
- **Response Time**: Target <5 seconds
- **Audio Quality**: Monitor user feedback
- **System Uptime**: Aim for 99.9%
- **API Usage**: Track costs and limits

### Dashboard Features
- **Real-time Call Status**: See active calls
- **Historical Analytics**: Trends and patterns
- **Error Tracking**: System issues and failures
- **Performance Metrics**: Response times and quality

---

## 🎯 Mission Accomplished!

**Congratulations!** 🎉 You now have a fully functional AI voice agent that can:

✅ **Answer phone calls** automatically  
✅ **Have natural conversations** using advanced AI  
✅ **Provide realistic voice responses** with ElevenLabs  
✅ **Log and analyze all interactions** in a beautiful dashboard  
✅ **Scale to handle multiple concurrent calls**  
✅ **Integrate with your existing business systems**  

**Your AI voice agent is ready to revolutionize your customer interactions!** 🚀📞