#!/bin/bash

# Test Frontend Accessibility Script
# This script tests if the frontend dashboard is accessible without authentication

echo "🧪 Testing Frontend Dashboard Accessibility..."
echo ""

# Test if frontend is running
echo "1. Testing if frontend is accessible..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend is not accessible at http://localhost:3000"
    echo "   Make sure to run: docker-compose up -d frontend"
    exit 1
fi

# Test dashboard page specifically
echo ""
echo "2. Testing dashboard page..."
DASHBOARD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/dashboard)
if [ "$DASHBOARD_RESPONSE" = "200" ]; then
    echo "✅ Dashboard is accessible at http://localhost:3000/dashboard"
else
    echo "❌ Dashboard returned HTTP $DASHBOARD_RESPONSE"
fi

# Test backend API
echo ""
echo "3. Testing backend API..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running at http://localhost:8000"
else
    echo "❌ Backend API is not accessible"
    echo "   Make sure to run: docker-compose up -d backend"
fi

# Test demo endpoints
echo ""
echo "4. Testing demo endpoints..."
CALLS_RESPONSE=$(curl -s http://localhost:8000/api/v1/voice/calls/demo)
if echo "$CALLS_RESPONSE" | grep -q "calls"; then
    echo "✅ Demo calls endpoint is working"
else
    echo "❌ Demo calls endpoint is not working"
fi

echo ""
echo "🎯 Frontend Dashboard Test Results:"
echo "   • Main page: http://localhost:3000"
echo "   • Dashboard: http://localhost:3000/dashboard"
echo "   • API Docs: http://localhost:8000/docs"
echo ""

if [ "$DASHBOARD_RESPONSE" = "200" ]; then
    echo "🎉 SUCCESS: Dashboard is accessible without authentication!"
    echo "   You can now access the dashboard at http://localhost:3000/dashboard"
else
    echo "⚠️  Dashboard may not be fully accessible. Check the logs:"
    echo "   docker-compose logs frontend"
fi