#!/bin/bash
# =============================================================================
# AI VOICE AGENT MVP - SIMPLIFIED RUNNER (NO DOCKER)
# =============================================================================
# This script runs the MVP without Docker complexity
# Perfect for development and testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_INSTALL=false
BACKEND_ONLY=false
FRONTEND_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}🚀 AI Voice Agent MVP - Simplified Runner${NC}"
echo -e "${CYAN}=============================================${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure your API keys${NC}"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)
echo -e "${GREEN}✅ Environment variables loaded${NC}"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}⚠️  Killing process on port $port (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Function to start backend
start_backend() {
    echo -e "${YELLOW}🔧 Starting Backend...${NC}"
    
    if check_port 8000; then
        echo -e "${YELLOW}⚠️  Port 8000 is already in use. Stopping existing process...${NC}"
        kill_port 8000
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found! Please install Python 3.11+${NC}"
        exit 1
    fi
    
    local python_version=$(python3 --version)
    echo -e "${GREEN}✅ Python found: $python_version${NC}"
    
    # Install backend dependencies
    if [ "$SKIP_INSTALL" = false ]; then
        echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
        cd backend
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Install minimal dependencies for MVP
        if [ -f "requirements-minimal.txt" ]; then
            pip install -r requirements-minimal.txt
        else
            pip install -r requirements.txt
        fi
        
        cd ..
        echo -e "${GREEN}✅ Backend dependencies installed${NC}"
    fi
    
    # Start backend
    echo -e "${GREEN}🚀 Starting FastAPI backend on http://localhost:8000${NC}"
    cd backend
    source venv/bin/activate
    
    # Set environment for SQLite (simpler than PostgreSQL)
    export DATABASE_URL="sqlite+aiosqlite:///./voice_agent.db"
    export REDIS_URL="redis://localhost:6379/0"  # Will fallback to memory if Redis not available
    
    # Use simplified main file for MVP
    if [ -f "main-simple.py" ]; then
        nohup python -m uvicorn main-simple:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    else
        nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    fi
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
    local attempts=0
    while [ $attempts -lt 15 ]; do
        sleep 2
        attempts=$((attempts + 1))
        
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is ready!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Backend starting... (attempt $attempts/15)${NC}"
    done
    
    echo -e "${RED}❌ Backend failed to start after 30 seconds${NC}"
    echo -e "${YELLOW}Check backend.log for errors${NC}"
    return 1
}

# Function to start frontend
start_frontend() {
    echo -e "${YELLOW}🔧 Starting Frontend...${NC}"
    
    if check_port 3000; then
        echo -e "${YELLOW}⚠️  Port 3000 is already in use. Stopping existing process...${NC}"
        kill_port 3000
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found! Please install Node.js 18+${NC}"
        exit 1
    fi
    
    local node_version=$(node --version)
    echo -e "${GREEN}✅ Node.js found: $node_version${NC}"
    
    # Install frontend dependencies
    if [ "$SKIP_INSTALL" = false ]; then
        echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
        cd frontend
        npm install
        cd ..
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    fi
    
    # Start frontend
    echo -e "${GREEN}🚀 Starting Next.js frontend on http://localhost:3000${NC}"
    cd frontend
    
    # Set environment variables
    export NEXT_PUBLIC_API_URL="http://localhost:8000"
    export NEXT_PUBLIC_WS_URL="ws://localhost:8000"
    
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
    local attempts=0
    while [ $attempts -lt 10 ]; do
        sleep 3
        attempts=$((attempts + 1))
        
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend is ready!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Frontend starting... (attempt $attempts/10)${NC}"
    done
    
    echo -e "${RED}❌ Frontend failed to start after 30 seconds${NC}"
    echo -e "${YELLOW}Check frontend.log for errors${NC}"
    return 1
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}🛑 Cleaning up...${NC}"
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill processes on ports
    kill_port 8000
    kill_port 3000
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
if [ "$BACKEND_ONLY" = true ]; then
    start_backend
elif [ "$FRONTEND_ONLY" = true ]; then
    start_frontend
else
    # Start both
    start_backend
    if [ $? -eq 0 ]; then
        sleep 5  # Give backend time to fully start
        start_frontend
    else
        echo -e "${RED}❌ Backend failed to start, not starting frontend${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}🎉 MVP IS RUNNING!${NC}"
echo -e "${GREEN}==================${NC}"
echo -e "${CYAN}📊 Dashboard: http://localhost:3000/dashboard${NC}"
echo -e "${CYAN}🔧 API Docs:  http://localhost:8000/docs${NC}"
echo -e "${CYAN}❤️  Health:   http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}✨ Features Available:${NC}"
echo -e "  • Real-time dashboard with demo data"
echo -e "  • Voice agent API endpoints"
echo -e "  • System health monitoring"
echo -e "  • Interactive API documentation"
echo ""
echo -e "${YELLOW}🔧 To configure Twilio for phone calls:${NC}"
echo -e "  1. Run: ngrok http 8000"
echo -e "  2. Copy the ngrok URL to Twilio Console"
echo -e "  3. Set webhook: https://your-ngrok-url.ngrok.io/api/v1/voice/twilio/webhook/{call_id}"
echo ""
echo -e "${RED}Press Ctrl+C to stop all services${NC}"

# Keep script running and monitor services
while true; do
    sleep 10
    
    # Check if services are still running
    if [ "$BACKEND_ONLY" != true ] && ! check_port 8000; then
        echo -e "${YELLOW}⚠️  Backend stopped unexpectedly${NC}"
    fi
    
    if [ "$FRONTEND_ONLY" != true ] && ! check_port 3000; then
        echo -e "${YELLOW}⚠️  Frontend stopped unexpectedly${NC}"
    fi
done