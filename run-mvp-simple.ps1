#!/usr/bin/env pwsh
# =============================================================================
# AI VOICE AGENT MVP - SIMPLIFIED RUNNER (NO DOCKER)
# =============================================================================
# This script runs the MVP without Docker complexity
# Perfect for development and testing

param(
    [switch]$SkipInstall,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

Write-Host "🚀 AI Voice Agent MVP - Simplified Runner" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure your API keys" -ForegroundColor Yellow
    exit 1
}

# Load environment variables
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

Write-Host "✅ Environment variables loaded" -ForegroundColor Green

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Function to start backend
function Start-Backend {
    Write-Host "🔧 Starting Backend..." -ForegroundColor Yellow
    
    if (Test-Port 8000) {
        Write-Host "⚠️  Port 8000 is already in use. Stopping existing process..." -ForegroundColor Yellow
        try {
            $process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
            if ($process) {
                Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
                Start-Sleep 2
            }
        } catch {
            Write-Host "Could not stop existing process on port 8000" -ForegroundColor Yellow
        }
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
        exit 1
    }
    
    # Install backend dependencies
    if (-not $SkipInstall) {
        Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
        Set-Location backend
        
        # Create virtual environment if it doesn't exist
        if (-not (Test-Path "venv")) {
            python -m venv venv
        }
        
        # Activate virtual environment
        & .\venv\Scripts\Activate.ps1
        
        # Install minimal dependencies for MVP
        if (Test-Path "requirements-minimal.txt") {
            pip install -r requirements-minimal.txt
        } else {
            pip install -r requirements.txt
        }
        
        Set-Location ..
        Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
    }
    
    # Start backend
    Write-Host "🚀 Starting FastAPI backend on http://localhost:8000" -ForegroundColor Green
    Set-Location backend
    & .\venv\Scripts\Activate.ps1
    
    # Set environment for SQLite (simpler than PostgreSQL)
    $env:DATABASE_URL = "sqlite+aiosqlite:///./voice_agent.db"
    $env:REDIS_URL = "redis://localhost:6379/0"  # Will fallback to memory if Redis not available
    
    # Use simplified main file for MVP
    if (Test-Path "main-simple.py") {
        Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main-simple:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -NoNewWindow
    } else {
        Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -NoNewWindow
    }
    Set-Location ..
    
    # Wait for backend to start
    Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
    $attempts = 0
    do {
        Start-Sleep 2
        $attempts++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Backend is ready!" -ForegroundColor Green
                break
            }
        } catch {
            # Continue waiting
        }
        
        if ($attempts -gt 15) {
            Write-Host "❌ Backend failed to start after 30 seconds" -ForegroundColor Red
            Write-Host "Check the backend logs for errors" -ForegroundColor Yellow
            break
        }
        
        Write-Host "⏳ Backend starting... (attempt $attempts/15)" -ForegroundColor Yellow
    } while ($true)
}

# Function to start frontend
function Start-Frontend {
    Write-Host "🔧 Starting Frontend..." -ForegroundColor Yellow
    
    if (Test-Port 3000) {
        Write-Host "⚠️  Port 3000 is already in use. Stopping existing process..." -ForegroundColor Yellow
        try {
            $process = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
            if ($process) {
                Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
                Start-Sleep 2
            }
        } catch {
            Write-Host "Could not stop existing process on port 3000" -ForegroundColor Yellow
        }
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
        exit 1
    }
    
    # Install frontend dependencies
    if (-not $SkipInstall) {
        Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
        Set-Location frontend
        npm install
        Set-Location ..
        Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
    }
    
    # Start frontend
    Write-Host "🚀 Starting Next.js frontend on http://localhost:3000" -ForegroundColor Green
    Set-Location frontend
    
    # Set environment variables
    $env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
    $env:NEXT_PUBLIC_WS_URL = "ws://localhost:8000"
    
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow
    Set-Location ..
    
    # Wait for frontend to start
    Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
    $attempts = 0
    do {
        Start-Sleep 3
        $attempts++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Frontend is ready!" -ForegroundColor Green
                break
            }
        } catch {
            # Continue waiting
        }
        
        if ($attempts -gt 10) {
            Write-Host "❌ Frontend failed to start after 30 seconds" -ForegroundColor Red
            Write-Host "Check the frontend logs for errors" -ForegroundColor Yellow
            break
        }
        
        Write-Host "⏳ Frontend starting... (attempt $attempts/10)" -ForegroundColor Yellow
    } while ($true)
}

# Main execution
try {
    if ($BackendOnly) {
        Start-Backend
    } elseif ($FrontendOnly) {
        Start-Frontend
    } else {
        # Start both
        Start-Backend
        Start-Sleep 5  # Give backend time to fully start
        Start-Frontend
    }
    
    Write-Host ""
    Write-Host "🎉 MVP IS RUNNING!" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host "📊 Dashboard: http://localhost:3000/dashboard" -ForegroundColor Cyan
    Write-Host "🔧 API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "❤️  Health:   http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✨ Features Available:" -ForegroundColor Yellow
    Write-Host "  • Real-time dashboard with demo data" -ForegroundColor White
    Write-Host "  • Voice agent API endpoints" -ForegroundColor White
    Write-Host "  • System health monitoring" -ForegroundColor White
    Write-Host "  • Interactive API documentation" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 To configure Twilio for phone calls:" -ForegroundColor Yellow
    Write-Host "  1. Run: ngrok http 8000" -ForegroundColor White
    Write-Host "  2. Copy the ngrok URL to Twilio Console" -ForegroundColor White
    Write-Host "  3. Set webhook: https://your-ngrok-url.ngrok.io/api/v1/voice/twilio/webhook/{call_id}" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Red
    
    # Keep script running
    while ($true) {
        Start-Sleep 10
        
        # Check if services are still running
        $backendRunning = Test-Port 8000
        $frontendRunning = Test-Port 3000
        
        if (-not $backendRunning -and -not $BackendOnly) {
            Write-Host "⚠️  Backend stopped unexpectedly" -ForegroundColor Yellow
        }
        
        if (-not $frontendRunning -and -not $FrontendOnly) {
            Write-Host "⚠️  Frontend stopped unexpectedly" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Write-Host "🛑 Cleaning up..." -ForegroundColor Yellow
    
    # Stop processes on ports 8000 and 3000
    try {
        Get-Process | Where-Object { $_.ProcessName -eq "python" -or $_.ProcessName -eq "node" } | ForEach-Object {
            try {
                $_.Kill()
            } catch {
                # Ignore errors when killing processes
            }
        }
    } catch {
        # Ignore cleanup errors
    }
    
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}