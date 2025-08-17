#!/bin/bash

# Complete System Verification Script
# Verifies that all components are working together seamlessly

echo "🔍 AI Voice Agent MVP - Complete System Verification"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0

# Function to check endpoint
check_endpoint() {
    local url=$1
    local name=$2
    local expected_content=$3
    
    echo -n "Checking $name... "
    
    if response=$(curl -s "$url" 2>/dev/null); then
        if [[ -z "$expected_content" ]] || echo "$response" | grep -q "$expected_content"; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        else
            echo -e "${RED}❌ FAIL (unexpected content)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ FAIL (not accessible)${NC}"
        return 1
    fi
}

# Check backend services
echo -e "${BLUE}Backend Services:${NC}"
check_endpoint "http://localhost:8000/health" "Health Check" "healthy" || ((ERRORS++))
check_endpoint "http://localhost:8000/api/v1/voice/calls/demo" "Demo Calls API" "calls" || ((ERRORS++))
check_endpoint "http://localhost:8000/api/v1/voice/system/status" "System Status API" "status" || ((ERRORS++))
check_endpoint "http://localhost:8000/docs" "API Documentation" "swagger" || ((ERRORS++))

echo ""
echo -e "${BLUE}Frontend Services:${NC}"
check_endpoint "http://localhost:3000" "Frontend Home" "Voice Agent" || ((ERRORS++))
check_endpoint "http://localhost:3000/dashboard" "Dashboard (No Auth)" "Dashboard" || ((ERRORS++))

echo ""
echo -e "${BLUE}Integration Tests:${NC}"

# Test if dashboard can fetch data from backend
echo -n "Dashboard API Integration... "
if curl -s "http://localhost:3000/dashboard" | grep -q "Dashboard" && curl -s "http://localhost:8000/api/v1/voice/calls/demo" | grep -q "calls"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    ((ERRORS++))
fi

# Test CORS
echo -n "CORS Configuration... "
if curl -s -H "Origin: http://localhost:3000" "http://localhost:8000/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    ((ERRORS++))
fi

echo ""
echo "=================================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL SYSTEMS OPERATIONAL!${NC}"
    echo ""
    echo -e "${BLUE}✅ Ready to use:${NC}"
    echo "   • Dashboard: http://localhost:3000/dashboard"
    echo "   • API Docs: http://localhost:8000/docs"
    echo "   • Health: http://localhost:8000/health"
    echo ""
    echo -e "${GREEN}🚀 Your AI Voice Agent MVP is ready!${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS issues${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "   • Check if all services are running: docker-compose ps"
    echo "   • View logs: docker-compose logs -f"
    echo "   • Restart services: docker-compose restart"
    echo ""
    exit 1
fi