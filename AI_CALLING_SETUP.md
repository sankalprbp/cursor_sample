# AI Calling Feature Setup Guide

This guide will help you set up the AI calling feature using Twilio, OpenAI, and ElevenLabs.

## 🚀 Overview

The AI calling feature allows you to make real phone calls where an AI agent handles the conversation using:
- **Twilio**: For phone call infrastructure
- **OpenAI**: For AI conversation handling
- **ElevenLabs**: For voice synthesis

## 📋 Prerequisites

Before setting up the AI calling feature, you need accounts and API keys from:

1. **Twilio Account** (Required)
2. **OpenAI Account** (Required)
3. **ElevenLabs Account** (Required)

## 🔑 Required API Keys

### 1. Twilio Setup

**Step 1: Create Twilio Account**
1. Go to [Twilio Console](https://console.twilio.com/)
2. Sign up for a free account
3. Verify your phone number

**Step 2: Get Your Credentials**
1. In the Twilio Console, go to "Account" → "API Keys & Tokens"
2. Copy your:
   - **Account SID**
   - **Auth Token**

**Step 3: Get a Phone Number**
1. Go to "Phone Numbers" → "Manage" → "Buy a number"
2. Purchase a phone number (free trial accounts get $15 credit)
3. Copy the phone number

**Step 4: Configure Webhooks**
1. Go to "Phone Numbers" → "Manage" → "Active numbers"
2. Click on your number
3. Set the webhook URL to: `http://your-domain.com/api/v1/voice/twilio/webhook/{call_id}`
4. Set the status callback URL to: `http://your-domain.com/api/v1/voice/twilio/status/{call_id}`

### 2. OpenAI Setup

**Step 1: Create OpenAI Account**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up for an account
3. Add payment method (required for API usage)

**Step 2: Get API Key**
1. Go to [API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the API key (starts with `sk-`)

### 3. ElevenLabs Setup

**Step 1: Create ElevenLabs Account**
1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for a free account
3. Verify your email

**Step 2: Get API Key**
1. Go to your [Profile](https://elevenlabs.io/app/profile)
2. Copy your API key

**Step 3: Choose a Voice (Optional)**
1. Go to [Voice Library](https://elevenlabs.io/app/voice-library)
2. Select a voice or create a custom one
3. Copy the Voice ID

## ⚙️ Environment Configuration

### Step 1: Copy Environment Template
```bash
cp .env.example .env
```

### Step 2: Update Required Variables

Edit your `.env` file and add your API keys:

```bash
# Twilio Configuration (REQUIRED)
TWILIO_ACCOUNT_SID=your-account-sid-from-twilio
TWILIO_AUTH_TOKEN=your-auth-token-from-twilio
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here

# ElevenLabs Configuration (REQUIRED)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# Base URL for webhooks
BASE_URL=http://localhost:8000
```

### Step 3: Optional Configuration

For production, you may also want to configure:

```bash
# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:password@localhost:5432/voice_agent_db

# Redis (for session management)
REDIS_URL=redis://localhost:6379/0

# AWS S3 (for audio storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET_AUDIO=your-audio-bucket
```

## 🚀 Testing the Setup

### Step 1: Start the Application
```bash
# Start the backend
cd backend
python -m uvicorn main:app --reload

# Start the frontend (in another terminal)
cd frontend
npm run dev
```

### Step 2: Check Twilio Status
1. Go to your dashboard at `http://localhost:3000/dashboard`
2. Look for the "AI Phone Call" panel
3. Check if "Twilio Ready" is displayed in green

### Step 3: Make a Test Call
1. Enter a phone number in the AI calling panel
2. Click "Make Call"
3. The AI agent should answer and start a conversation

## 🔧 Troubleshooting

### Twilio Issues

**Problem: "Twilio service is not configured"**
- Solution: Check that all Twilio environment variables are set correctly
- Verify your Account SID and Auth Token are correct

**Problem: "Failed to initiate call"**
- Solution: Check your Twilio phone number is active
- Verify you have sufficient credits in your Twilio account
- Check webhook URLs are accessible from the internet

### OpenAI Issues

**Problem: "OpenAI API error"**
- Solution: Verify your OpenAI API key is correct
- Check you have sufficient credits in your OpenAI account
- Ensure the API key has the correct permissions

### ElevenLabs Issues

**Problem: "Voice synthesis failed"**
- Solution: Verify your ElevenLabs API key is correct
- Check you have sufficient characters in your ElevenLabs account
- Try a different voice ID if the default one doesn't work

## 📱 Production Deployment

### Webhook Configuration
For production, you need to configure webhooks that are accessible from the internet:

1. **Use a public domain** for your API
2. **Set up SSL/HTTPS** (required by Twilio)
3. **Update BASE_URL** in your environment variables
4. **Configure Twilio webhooks** to point to your production domain

### Example Production Environment
```bash
BASE_URL=https://your-domain.com
TWILIO_ACCOUNT_SID=your-production-sid
TWILIO_AUTH_TOKEN=your-production-token
TWILIO_PHONE_NUMBER=+1234567890
OPENAI_API_KEY=sk-your-production-key
ELEVENLABS_API_KEY=your-production-key
```

## 💰 Cost Estimation

### Twilio Costs
- **Phone Number**: ~$1/month per number
- **Outbound Calls**: ~$0.01-0.02/minute
- **Inbound Calls**: ~$0.0085/minute

### OpenAI Costs
- **GPT-4**: ~$0.03/1K tokens
- **GPT-3.5**: ~$0.002/1K tokens

### ElevenLabs Costs
- **Free Tier**: 10,000 characters/month
- **Paid Plans**: Starting at $22/month for 30,000 characters

## 🔒 Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate API keys** regularly
4. **Monitor usage** to prevent unexpected charges
5. **Set up webhook validation** in production

## 📞 Support

If you encounter issues:

1. Check the application logs for detailed error messages
2. Verify all API keys are correct and have sufficient credits
3. Test webhook endpoints are accessible
4. Check Twilio console for call logs and errors

## 🎯 Next Steps

Once the AI calling feature is working:

1. **Customize the AI agent** personality and responses
2. **Upload knowledge base** documents for better responses
3. **Set up call analytics** and monitoring
4. **Configure call routing** and transfer logic
5. **Implement billing** and usage tracking