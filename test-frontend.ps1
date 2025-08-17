# Test Frontend Accessibility Script (PowerShell)
# This script tests if the frontend dashboard is accessible without authentication

Write-Host "🧪 Testing Frontend Dashboard Accessibility..." -ForegroundColor Blue
Write-Host ""

# Test if frontend is running
Write-Host "1. Testing if frontend is accessible..." -ForegroundColor Cyan
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend is running at http://localhost:3000" -ForegroundColor Green
}
catch {
    Write-Host "❌ Frontend is not accessible at http://localhost:3000" -ForegroundColor Red
    Write-Host "   Make sure to run: docker-compose up -d frontend" -ForegroundColor Yellow
    exit 1
}

# Test dashboard page specifically
Write-Host ""
Write-Host "2. Testing dashboard page..." -ForegroundColor Cyan
try {
    $dashboardResponse = Invoke-WebRequest -Uri "http://localhost:3000/dashboard" -UseBasicParsing -TimeoutSec 5
    if ($dashboardResponse.StatusCode -eq 200) {
        Write-Host "✅ Dashboard is accessible at http://localhost:3000/dashboard" -ForegroundColor Green
        $dashboardAccessible = $true
    }
    else {
        Write-Host "❌ Dashboard returned HTTP $($dashboardResponse.StatusCode)" -ForegroundColor Red
        $dashboardAccessible = $false
    }
}
catch {
    Write-Host "❌ Dashboard is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    $dashboardAccessible = $false
}

# Test backend API
Write-Host ""
Write-Host "3. Testing backend API..." -ForegroundColor Cyan
try {
    $backendResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ Backend API is running at http://localhost:8000" -ForegroundColor Green
}
catch {
    Write-Host "❌ Backend API is not accessible" -ForegroundColor Red
    Write-Host "   Make sure to run: docker-compose up -d backend" -ForegroundColor Yellow
}

# Test demo endpoints
Write-Host ""
Write-Host "4. Testing demo endpoints..." -ForegroundColor Cyan
try {
    $callsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/voice/calls/demo" -TimeoutSec 5
    if ($callsResponse.calls) {
        Write-Host "✅ Demo calls endpoint is working" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Demo calls endpoint returned unexpected data" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Demo calls endpoint is not working: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Frontend Dashboard Test Results:" -ForegroundColor Magenta
Write-Host "   • Main page: http://localhost:3000"
Write-Host "   • Dashboard: http://localhost:3000/dashboard"
Write-Host "   • API Docs: http://localhost:8000/docs"
Write-Host ""

if ($dashboardAccessible) {
    Write-Host "🎉 SUCCESS: Dashboard is accessible without authentication!" -ForegroundColor Green
    Write-Host "   You can now access the dashboard at http://localhost:3000/dashboard" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Dashboard may not be fully accessible. Check the logs:" -ForegroundColor Yellow
    Write-Host "   docker-compose logs frontend" -ForegroundColor Yellow
}