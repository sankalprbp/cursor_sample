#!/bin/bash

# Voice Agent Platform Startup Script
# This script starts the application and provides webhook URLs for Twilio configuration

set -e

echo "🚀 Starting Voice Agent Platform..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to get the public IP address
get_public_ip() {
    # Try to get public IP
    PUBLIC_IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "localhost")
    echo $PUBLIC_IP
}

# Function to get local IP address
get_local_ip() {
    # Get local IP address
    LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
    echo $LOCAL_IP
}

# Start the application
echo "📦 Building and starting containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi

# Get IP addresses
PUBLIC_IP=$(get_public_ip)
LOCAL_IP=$(get_local_ip)

echo ""
echo "✅ Voice Agent Platform is now running!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend Dashboard: http://$LOCAL_IP"
echo "   Backend API: http://$LOCAL_IP:8000"
echo "   API Documentation: http://$LOCAL_IP/docs"
echo ""
echo "🔗 Twilio Webhook URLs (use these in your Twilio console):"
echo ""
echo "📞 Webhook URL:"
echo "   http://$PUBLIC_IP/api/v1/voice/twilio/webhook/{call_id}"
echo ""
echo "📊 Status Callback URL:"
echo "   http://$PUBLIC_IP/api/v1/voice/twilio/status/{call_id}"
echo ""
echo "📝 Instructions:"
echo "   1. Copy the webhook URLs above"
echo "   2. Go to your Twilio Console"
echo "   3. Navigate to Phone Numbers > Manage > Active numbers"
echo "   4. Click on your phone number"
echo "   5. In the 'Voice Configuration' section:"
echo "      - Set 'Webhook URL' to: http://$PUBLIC_IP/api/v1/voice/twilio/webhook/{call_id}"
echo "      - Set 'Status Callback URL' to: http://$PUBLIC_IP/api/v1/voice/twilio/status/{call_id}"
echo "   6. Save the configuration"
echo ""
echo "🔧 Demo Mode:"
echo "   The dashboard is accessible without login at: http://$LOCAL_IP/dashboard"
echo "   You can test the AI calling functionality there."
echo ""
echo "📋 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo ""

# Check if the application is responding
echo "🔍 Testing application connectivity..."
if curl -s http://localhost > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend may still be starting up..."
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is responding"
else
    echo "⚠️  Backend API may still be starting up..."
fi

echo ""
echo "🎉 Setup complete! Your Voice Agent Platform is ready for Twilio integration."