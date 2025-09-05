# Simple MVP Starter Script
Write-Host "🚀 Starting AI Voice Agent MVP..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure your API keys" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment file found" -ForegroundColor Green

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Setting up backend..." -ForegroundColor Yellow

# Setup backend
Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements-minimal.txt") {
    pip install -r requirements-minimal.txt
} else {
    pip install fastapi uvicorn pydantic python-dotenv
}

Write-Host "✅ Backend setup complete" -ForegroundColor Green

# Start backend
Write-Host "🚀 Starting backend server..." -ForegroundColor Green
if (Test-Path "main-simple.py") {
    Start-Process -FilePath "python" -ArgumentList "main-simple.py" -NoNewWindow
} else {
    Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -NoNewWindow
}

Set-Location ..

# Wait for backend
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep 5

# Setup frontend
Write-Host ""
Write-Host "🔧 Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
npm install

Write-Host "✅ Frontend setup complete" -ForegroundColor Green

# Start frontend
Write-Host "🚀 Starting frontend server..." -ForegroundColor Green
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow

Set-Location ..

Write-Host ""
Write-Host "🎉 MVP IS STARTING!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "📊 Dashboard: http://localhost:3000/dashboard" -ForegroundColor Cyan
Write-Host "🔧 API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "❤️  Health:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Please wait 30-60 seconds for services to fully start..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Red

# Keep script running
try {
    while ($true) {
        Start-Sleep 10
    }
} catch {
    Write-Host "Stopping services..." -ForegroundColor Yellow
}