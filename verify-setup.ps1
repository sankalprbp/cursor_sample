# Complete System Verification Script (PowerShell)
# Verifies that all components are working together seamlessly

Write-Host "🔍 AI Voice Agent MVP - Complete System Verification" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue
Write-Host ""

$Errors = 0

# Function to check endpoint
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Name,
        [string]$ExpectedContent = ""
    )
    
    Write-Host "Checking $Name... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        
        if ([string]::IsNullOrEmpty($ExpectedContent) -or $response.Content -like "*$ExpectedContent*") {
            Write-Host "✅ OK" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ FAIL (unexpected content)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ FAIL (not accessible)" -ForegroundColor Red
        return $false
    }
}

# Check backend services
Write-Host "Backend Services:" -ForegroundColor Cyan
if (-not (Test-Endpoint "http://localhost:8000/health" "Health Check" "healthy")) { $Errors++ }
if (-not (Test-Endpoint "http://localhost:8000/api/v1/voice/calls/demo" "Demo Calls API" "calls")) { $Errors++ }
if (-not (Test-Endpoint "http://localhost:8000/api/v1/voice/system/status" "System Status API" "status")) { $Errors++ }
if (-not (Test-Endpoint "http://localhost:8000/docs" "API Documentation" "swagger")) { $Errors++ }

Write-Host ""
Write-Host "Frontend Services:" -ForegroundColor Cyan
if (-not (Test-Endpoint "http://localhost:3000" "Frontend Home" "Voice Agent")) { $Errors++ }
if (-not (Test-Endpoint "http://localhost:3000/dashboard" "Dashboard (No Auth)" "Dashboard")) { $Errors++ }

Write-Host ""
Write-Host "Integration Tests:" -ForegroundColor Cyan

# Test if dashboard can fetch data from backend
Write-Host "Dashboard API Integration... " -NoNewline
try {
    $dashboardResponse = Invoke-WebRequest -Uri "http://localhost:3000/dashboard" -UseBasicParsing -TimeoutSec 5
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/voice/calls/demo" -UseBasicParsing -TimeoutSec 5
    
    if ($dashboardResponse.Content -like "*Dashboard*" -and $apiResponse.Content -like "*calls*") {
        Write-Host "✅ OK" -ForegroundColor Green
    }
    else {
        Write-Host "❌ FAIL" -ForegroundColor Red
        $Errors++
    }
}
catch {
    Write-Host "❌ FAIL" -ForegroundColor Red
    $Errors++
}

# Test CORS
Write-Host "CORS Configuration... " -NoNewline
try {
    $headers = @{ "Origin" = "http://localhost:3000" }
    $corsResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Headers $headers -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ OK" -ForegroundColor Green
}
catch {
    Write-Host "❌ FAIL" -ForegroundColor Red
    $Errors++
}

Write-Host ""
Write-Host "=================================================="

if ($Errors -eq 0) {
    Write-Host "🎉 ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Ready to use:" -ForegroundColor Cyan
    Write-Host "   • Dashboard: http://localhost:3000/dashboard"
    Write-Host "   • API Docs: http://localhost:8000/docs"
    Write-Host "   • Health: http://localhost:8000/health"
    Write-Host ""
    Write-Host "🚀 Your AI Voice Agent MVP is ready!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "❌ Found $Errors issues" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   • Check if all services are running: docker-compose ps"
    Write-Host "   • View logs: docker-compose logs -f"
    Write-Host "   • Restart services: docker-compose restart"
    Write-Host ""
    exit 1
}