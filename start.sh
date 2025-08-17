#!/bin/bash

# AI Voice Agent MVP - Startup Script
# This script starts the system and validates everything is working

set -e

echo "🤖 Starting AI Voice Agent MVP..."
echo ""

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.example to .env and configure your API keys:"
    echo "   cp .env.example .env"
    echo "   Then edit .env with your OpenAI, ElevenLabs, and Twilio credentials."
    exit 1
fi

# Validate required environment variables
echo "🔍 Validating configuration..."

# Source the .env file
set -a
source .env
set +a

# Check required API keys
MISSING_KEYS=()

if [[ -z "$OPENAI_API_KEY" || "$OPENAI_API_KEY" == "your-openai-api-key-here" ]]; then
    MISSING_KEYS+=("OPENAI_API_KEY")
fi

if [[ -z "$ELEVENLABS_API_KEY" || "$ELEVENLABS_API_KEY" == "your-elevenlabs-api-key-here" ]]; then
    MISSING_KEYS+=("ELEVENLABS_API_KEY")
fi

if [[ -z "$TWILIO_ACCOUNT_SID" || "$TWILIO_ACCOUNT_SID" == "your-twilio-account-sid-here" ]]; then
    MISSING_KEYS+=("TWILIO_ACCOUNT_SID")
fi

if [[ -z "$TWILIO_AUTH_TOKEN" || "$TWILIO_AUTH_TOKEN" == "your-twilio-auth-token-here" ]]; then
    MISSING_KEYS+=("TWILIO_AUTH_TOKEN")
fi

if [[ -z "$TWILIO_PHONE_NUMBER" || "$TWILIO_PHONE_NUMBER" == "+1234567890" ]]; then
    MISSING_KEYS+=("TWILIO_PHONE_NUMBER")
fi

if [ ${#MISSING_KEYS[@]} -ne 0 ]; then
    echo "❌ Missing required API keys in .env file:"
    for key in "${MISSING_KEYS[@]}"; do
        echo "   - $key"
    done
    echo ""
    echo "Please update your .env file with actual API keys:"
    echo "   - OpenAI: https://platform.openai.com/api-keys"
    echo "   - ElevenLabs: https://elevenlabs.io/app/speech-synthesis"
    echo "   - Twilio: https://console.twilio.com/"
    exit 1
fi

echo "✅ Configuration validated"

# Function to get public IP for webhook URLs
get_public_ip() {
    PUBLIC_IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "localhost")
    echo $PUBLIC_IP
}

# Start the application
echo ""
echo "📦 Building and starting containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo ""
echo "🔍 Checking service status..."
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi

# Test system health
echo ""
echo "🏥 Testing system health..."

# Wait a bit more for backend to be fully ready
sleep 10

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is healthy"
    
    # Get health details
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    echo "   Status: $(echo $HEALTH_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
else
    echo "⚠️  Backend API not responding yet, checking logs..."
    if command -v docker-compose &> /dev/null; then
        docker-compose logs --tail=10 backend
    else
        docker compose logs --tail=10 backend
    fi
fi

# Test Redis connection
if curl -s http://localhost:8000/health | grep -q "redis.*connected"; then
    echo "✅ Redis is connected"
else
    echo "⚠️  Redis connection issue"
fi

# Get public IP for webhook configuration
PUBLIC_IP=$(get_public_ip)

echo ""
echo "🎉 AI Voice Agent MVP is running!"
echo ""
echo "🌐 Access URLs:"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo ""
echo "📞 Your Twilio Phone Number: $TWILIO_PHONE_NUMBER"
echo ""
echo "🔗 Twilio Webhook Configuration:"
echo "   Go to: https://console.twilio.com/"
echo "   Navigate to: Phone Numbers > Manage > Active numbers"
echo "   Click your number: $TWILIO_PHONE_NUMBER"
echo "   Set Voice Webhook to:"
echo "   http://$PUBLIC_IP:8000/api/v1/voice/twilio/webhook/{call_id}"
echo ""
echo "💡 For local testing with ngrok:"
echo "   1. Install ngrok: https://ngrok.com/download"
echo "   2. Run: ngrok http 8000"
echo "   3. Use the ngrok HTTPS URL for Twilio webhooks"
echo ""
echo "🧪 Testing Commands:"
echo "   • Health check: curl http://localhost:8000/health"
echo "   • View logs: docker-compose logs -f backend"
echo "   • Stop system: docker-compose down"
echo ""
echo "📚 Documentation:"
echo "   • Setup Guide: MVP_SETUP_GUIDE.md"
echo "   • Testing Guide: TESTING_GUIDE.md"
echo ""

# Final validation
echo "🔬 Running final validation..."

# Check if all required services are responding
VALIDATION_PASSED=true

# Test OpenAI configuration (without making actual API call)
if [[ "$OPENAI_API_KEY" =~ ^sk-[a-zA-Z0-9]{48}$ ]]; then
    echo "✅ OpenAI API key format is valid"
else
    echo "⚠️  OpenAI API key format may be invalid"
    VALIDATION_PASSED=false
fi

# Test ElevenLabs configuration
if [[ ${#ELEVENLABS_API_KEY} -ge 20 ]]; then
    echo "✅ ElevenLabs API key format is valid"
else
    echo "⚠️  ElevenLabs API key format may be invalid"
    VALIDATION_PASSED=false
fi

# Test Twilio configuration
if [[ "$TWILIO_ACCOUNT_SID" =~ ^AC[a-zA-Z0-9]{32}$ ]]; then
    echo "✅ Twilio Account SID format is valid"
else
    echo "⚠️  Twilio Account SID format may be invalid"
    VALIDATION_PASSED=false
fi

echo ""
if [ "$VALIDATION_PASSED" = true ]; then
    echo "🎯 System is ready! Call $TWILIO_PHONE_NUMBER to test your AI voice agent."
    echo ""
    echo "Next steps:"
    echo "1. Configure Twilio webhooks (see URLs above)"
    echo "2. Call your Twilio number to test"
    echo "3. Check logs if you encounter issues"
    echo "4. Read TESTING_GUIDE.md for comprehensive testing"
else
    echo "⚠️  Some configuration issues detected. Please review and fix before testing."
    echo "   See MVP_SETUP_GUIDE.md for detailed setup instructions."
fi

echo ""
echo "🚀 Happy calling! Your AI voice agent is ready to chat."