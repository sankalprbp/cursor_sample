#!/bin/bash

# AI Voice Agent MVP - Complete Setup Script with ngrok Integration
# This script sets up everything needed for a working AI voice agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NGROK_CONFIG_DIR="$HOME/.ngrok2"
NGROK_CONFIG_FILE="$NGROK_CONFIG_DIR/ngrok.yml"
PROJECT_DIR=$(pwd)
ENV_FILE="$PROJECT_DIR/.env"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install ngrok
install_ngrok() {
    print_status "Installing ngrok..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install ngrok/ngrok/ngrok
        else
            print_error "Homebrew not found. Please install ngrok manually from https://ngrok.com/download"
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
        echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
        sudo apt update && sudo apt install ngrok
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows (Git Bash/Cygwin)
        print_status "Downloading ngrok for Windows..."
        curl -L -o ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip
        unzip ngrok.zip
        mv ngrok.exe /usr/local/bin/ 2>/dev/null || mv ngrok.exe ~/bin/ 2>/dev/null || {
            print_warning "Could not move ngrok to PATH. Please move ngrok.exe to a directory in your PATH manually."
        }
        rm -f ngrok.zip
    else
        print_error "Unsupported operating system. Please install ngrok manually from https://ngrok.com/download"
        return 1
    fi
    
    print_success "ngrok installed successfully"
}

# Function to setup ngrok
setup_ngrok() {
    print_header "NGROK SETUP"
    
    # Check if ngrok is installed
    if ! command_exists ngrok; then
        print_warning "ngrok not found. Installing ngrok..."
        install_ngrok
    else
        print_success "ngrok is already installed"
    fi
    
    # Check if ngrok is authenticated
    if ! ngrok config check >/dev/null 2>&1; then
        print_warning "ngrok is not authenticated"
        echo ""
        echo -e "${CYAN}To authenticate ngrok:${NC}"
        echo "1. Go to https://dashboard.ngrok.com/get-started/your-authtoken"
        echo "2. Sign up for a free account if you don't have one"
        echo "3. Copy your authtoken"
        echo ""
        read -p "Enter your ngrok authtoken: " NGROK_TOKEN
        
        if [[ -n "$NGROK_TOKEN" ]]; then
            ngrok config add-authtoken "$NGROK_TOKEN"
            print_success "ngrok authenticated successfully"
        else
            print_error "No authtoken provided. You'll need to authenticate ngrok manually later."
            return 1
        fi
    else
        print_success "ngrok is already authenticated"
    fi
}

# Function to validate environment variables
validate_env() {
    print_header "ENVIRONMENT VALIDATION"
    
    if [[ ! -f "$ENV_FILE" ]]; then
        print_error ".env file not found!"
        echo "Please copy .env.example to .env and configure your API keys:"
        echo "cp .env.example .env"
        return 1
    fi
    
    # Source the .env file
    set -a
    source "$ENV_FILE"
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
    
    if [[ ${#MISSING_KEYS[@]} -ne 0 ]]; then
        print_error "Missing required API keys in .env file:"
        for key in "${MISSING_KEYS[@]}"; do
            echo "   - $key"
        done
        echo ""
        echo "Please update your .env file with actual API keys:"
        echo "   - OpenAI: https://platform.openai.com/api-keys"
        echo "   - ElevenLabs: https://elevenlabs.io/app/speech-synthesis"
        echo "   - Twilio: https://console.twilio.com/"
        return 1
    fi
    
    print_success "All required API keys are configured"
}

# Function to check Docker
check_docker() {
    print_header "DOCKER VALIDATION"
    
    if ! command_exists docker; then
        print_error "Docker is not installed!"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running!"
        echo "Please start Docker and try again."
        return 1
    fi
    
    print_success "Docker is installed and running"
}

# Function to start services
start_services() {
    print_header "STARTING SERVICES"
    
    print_status "Building and starting Docker containers..."
    
    # Stop any existing containers
    if command_exists docker-compose; then
        docker-compose down >/dev/null 2>&1 || true
        docker-compose up --build -d
    else
        docker compose down >/dev/null 2>&1 || true
        docker compose up --build -d
    fi
    
    print_status "Waiting for services to start..."
    sleep 20
    
    # Check service status
    print_status "Checking service status..."
    if command_exists docker-compose; then
        docker-compose ps
    else
        docker compose ps
    fi
}

# Function to wait for backend to be ready
wait_for_backend() {
    print_status "Waiting for backend to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Backend not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Backend failed to start within expected time"
    print_status "Checking backend logs..."
    if command_exists docker-compose; then
        docker-compose logs --tail=20 backend
    else
        docker compose logs --tail=20 backend
    fi
    return 1
}

# Function to start ngrok tunnel
start_ngrok() {
    print_header "STARTING NGROK TUNNEL"
    
    # Kill any existing ngrok processes
    pkill -f ngrok >/dev/null 2>&1 || true
    sleep 2
    
    print_status "Starting ngrok tunnel on port 8000..."
    
    # Start ngrok in background
    ngrok http 8000 --log=stdout > ngrok.log 2>&1 &
    NGROK_PID=$!
    
    # Wait for ngrok to start
    sleep 5
    
    # Get the public URL
    local max_attempts=10
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1)
        
        if [[ -n "$NGROK_URL" ]]; then
            print_success "ngrok tunnel started successfully!"
            echo "Public URL: $NGROK_URL"
            break
        fi
        
        print_status "Attempt $attempt/$max_attempts - Waiting for ngrok tunnel..."
        sleep 2
        ((attempt++))
    done
    
    if [[ -z "$NGROK_URL" ]]; then
        print_error "Failed to get ngrok URL"
        print_status "Checking ngrok logs..."
        tail -20 ngrok.log
        return 1
    fi
    
    # Update BASE_URL in .env file
    if [[ -f "$ENV_FILE" ]]; then
        if grep -q "^BASE_URL=" "$ENV_FILE"; then
            sed -i.bak "s|^BASE_URL=.*|BASE_URL=$NGROK_URL|" "$ENV_FILE"
        else
            echo "BASE_URL=$NGROK_URL" >> "$ENV_FILE"
        fi
        print_success "Updated BASE_URL in .env file"
    fi
    
    # Save ngrok info for later use
    echo "$NGROK_URL" > .ngrok_url
    echo "$NGROK_PID" > .ngrok_pid
}

# Function to test system health
test_system() {
    print_header "SYSTEM HEALTH CHECK"
    
    print_status "Testing backend health..."
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    
    if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        echo "Response: $HEALTH_RESPONSE"
        return 1
    fi
    
    print_status "Testing frontend..."
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is accessible"
        
        # Test dashboard specifically
        DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/dashboard)
        if [[ "$DASHBOARD_STATUS" == "200" ]]; then
            print_success "Dashboard is accessible without authentication"
        else
            print_warning "Dashboard returned HTTP $DASHBOARD_STATUS"
        fi
    else
        print_warning "Frontend may still be starting up"
    fi
    
    print_status "Testing ngrok tunnel..."
    if [[ -n "$NGROK_URL" ]]; then
        if curl -s "$NGROK_URL/health" >/dev/null 2>&1; then
            print_success "ngrok tunnel is working"
        else
            print_warning "ngrok tunnel may not be fully ready yet"
        fi
    fi
}

# Function to display final instructions
show_final_instructions() {
    print_header "SETUP COMPLETE!"
    
    echo ""
    echo -e "${GREEN}🎉 Your AI Voice Agent MVP is ready!${NC}"
    echo ""
    echo -e "${CYAN}📱 Access URLs:${NC}"
    echo "   • Frontend Dashboard: http://localhost:3000"
    echo "   • Backend API: http://localhost:8000"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Public URL (ngrok): $NGROK_URL"
    echo ""
    echo -e "${CYAN}📞 Twilio Configuration:${NC}"
    echo "   1. Go to: https://console.twilio.com/"
    echo "   2. Navigate to: Phone Numbers > Manage > Active numbers"
    echo "   3. Click your phone number: $TWILIO_PHONE_NUMBER"
    echo "   4. Set Voice Webhook to:"
    echo "      $NGROK_URL/api/v1/voice/twilio/webhook/{call_id}"
    echo "   5. Set Status Callback to:"
    echo "      $NGROK_URL/api/v1/voice/twilio/status/{call_id}"
    echo "   6. Save the configuration"
    echo ""
    echo -e "${CYAN}🧪 Testing:${NC}"
    echo "   • Call your Twilio number: $TWILIO_PHONE_NUMBER"
    echo "   • The AI agent should answer and have a conversation"
    echo "   • Check the dashboard for call logs and transcripts"
    echo ""
    echo -e "${CYAN}📋 Useful Commands:${NC}"
    echo "   • View logs: docker-compose logs -f"
    echo "   • Stop system: docker-compose down"
    echo "   • Stop ngrok: kill \$(cat .ngrok_pid)"
    echo "   • Restart: ./setup-mvp.sh"
    echo ""
    echo -e "${YELLOW}⚠️  Important Notes:${NC}"
    echo "   • Keep this terminal open to maintain the ngrok tunnel"
    echo "   • The ngrok URL changes each time you restart (free plan)"
    echo "   • Update Twilio webhooks if you restart ngrok"
    echo "   • Check logs if calls don't work as expected"
    echo ""
    echo -e "${GREEN}🚀 Your AI voice agent is ready to take calls!${NC}"
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    if [[ -f .ngrok_pid ]]; then
        NGROK_PID=$(cat .ngrok_pid)
        kill "$NGROK_PID" >/dev/null 2>&1 || true
        rm -f .ngrok_pid .ngrok_url ngrok.log
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    print_header "AI VOICE AGENT MVP SETUP"
    echo "This script will set up your complete AI voice agent with ngrok integration"
    echo ""
    
    # Validate prerequisites
    validate_env || exit 1
    check_docker || exit 1
    setup_ngrok || exit 1
    
    # Start services
    start_services || exit 1
    wait_for_backend || exit 1
    start_ngrok || exit 1
    
    # Test system
    test_system || print_warning "Some health checks failed, but system may still work"
    
    # Show final instructions
    show_final_instructions
    
    # Run verification
    echo ""
    print_status "Running final system verification..."
    if ./verify-setup.sh; then
        print_success "System verification passed!"
    else
        print_warning "Some verification checks failed, but system may still work"
    fi
    
    # Keep script running to maintain ngrok tunnel
    echo ""
    print_status "Press Ctrl+C to stop the system and ngrok tunnel"
    echo ""
    
    # Monitor system
    while true; do
        sleep 30
        if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_warning "Backend health check failed - system may be down"
        fi
        
        if [[ -n "$NGROK_URL" ]] && ! curl -s "$NGROK_URL/health" >/dev/null 2>&1; then
            print_warning "ngrok tunnel may be down"
        fi
    done
}

# Run main function
main "$@"