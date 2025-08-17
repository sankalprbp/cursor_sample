# AI Voice Agent MVP - Complete Setup Script with ngrok Integration (PowerShell)
# This script sets up everything needed for a working AI voice agent on Windows

param(
    [switch]$SkipNgrok = $false
)

# Configuration
$ProjectDir = Get-Location
$EnvFile = Join-Path $ProjectDir ".env"
$NgrokUrl = ""
$NgrokProcess = $null

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Header {
    param([string]$Message)
    Write-Host "================================" -ForegroundColor Magenta
    Write-Host $Message -ForegroundColor Magenta
    Write-Host "================================" -ForegroundColor Magenta
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to install ngrok
function Install-Ngrok {
    Write-Status "Installing ngrok..."
    
    if (Test-Command "choco") {
        choco install ngrok -y
    }
    elseif (Test-Command "winget") {
        winget install ngrok.ngrok
    }
    else {
        Write-Status "Downloading ngrok manually..."
        $ngrokUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        $ngrokZip = Join-Path $env:TEMP "ngrok.zip"
        $ngrokDir = Join-Path $env:TEMP "ngrok"
        
        try {
            Invoke-WebRequest -Uri $ngrokUrl -OutFile $ngrokZip
            Expand-Archive -Path $ngrokZip -DestinationPath $ngrokDir -Force
            
            # Try to copy to a directory in PATH
            $pathDirs = $env:PATH -split ";"
            $installed = $false
            
            foreach ($dir in $pathDirs) {
                if (Test-Path $dir -PathType Container) {
                    try {
                        Copy-Item (Join-Path $ngrokDir "ngrok.exe") $dir -Force
                        $installed = $true
                        break
                    }
                    catch {
                        continue
                    }
                }
            }
            
            if (-not $installed) {
                Write-Warning "Could not install ngrok to PATH. Please add $(Join-Path $ngrokDir 'ngrok.exe') to your PATH manually."
            }
            
            Remove-Item $ngrokZip -Force -ErrorAction SilentlyContinue
        }
        catch {
            Write-Error "Failed to download ngrok: $_"
            return $false
        }
    }
    
    Write-Success "ngrok installed successfully"
    return $true
}

# Function to setup ngrok
function Setup-Ngrok {
    Write-Header "NGROK SETUP"
    
    if ($SkipNgrok) {
        Write-Warning "Skipping ngrok setup as requested"
        return $true
    }
    
    # Check if ngrok is installed
    if (-not (Test-Command "ngrok")) {
        Write-Warning "ngrok not found. Installing ngrok..."
        if (-not (Install-Ngrok)) {
            return $false
        }
    }
    else {
        Write-Success "ngrok is already installed"
    }
    
    # Check if ngrok is authenticated
    try {
        $configCheck = & ngrok config check 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Not authenticated"
        }
        Write-Success "ngrok is already authenticated"
    }
    catch {
        Write-Warning "ngrok is not authenticated"
        Write-Host ""
        Write-Host "To authenticate ngrok:" -ForegroundColor Cyan
        Write-Host "1. Go to https://dashboard.ngrok.com/get-started/your-authtoken"
        Write-Host "2. Sign up for a free account if you don't have one"
        Write-Host "3. Copy your authtoken"
        Write-Host ""
        
        $ngrokToken = Read-Host "Enter your ngrok authtoken"
        
        if ($ngrokToken) {
            try {
                & ngrok config add-authtoken $ngrokToken
                Write-Success "ngrok authenticated successfully"
            }
            catch {
                Write-Error "Failed to authenticate ngrok: $_"
                return $false
            }
        }
        else {
            Write-Error "No authtoken provided. You'll need to authenticate ngrok manually later."
            return $false
        }
    }
    
    return $true
}

# Function to validate environment variables
function Test-Environment {
    Write-Header "ENVIRONMENT VALIDATION"
    
    if (-not (Test-Path $EnvFile)) {
        Write-Error ".env file not found!"
        Write-Host "Please copy .env.example to .env and configure your API keys:"
        Write-Host "Copy-Item .env.example .env"
        return $false
    }
    
    # Read .env file
    $envVars = @{}
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $envVars[$matches[1]] = $matches[2]
        }
    }
    
    # Check required API keys
    $missingKeys = @()
    
    $requiredKeys = @{
        "OPENAI_API_KEY" = "your-openai-api-key-here"
        "ELEVENLABS_API_KEY" = "your-elevenlabs-api-key-here"
        "TWILIO_ACCOUNT_SID" = "your-twilio-account-sid-here"
        "TWILIO_AUTH_TOKEN" = "your-twilio-auth-token-here"
        "TWILIO_PHONE_NUMBER" = "+1234567890"
    }
    
    foreach ($key in $requiredKeys.Keys) {
        if (-not $envVars.ContainsKey($key) -or $envVars[$key] -eq $requiredKeys[$key] -or [string]::IsNullOrEmpty($envVars[$key])) {
            $missingKeys += $key
        }
    }
    
    if ($missingKeys.Count -gt 0) {
        Write-Error "Missing required API keys in .env file:"
        foreach ($key in $missingKeys) {
            Write-Host "   - $key"
        }
        Write-Host ""
        Write-Host "Please update your .env file with actual API keys:"
        Write-Host "   - OpenAI: https://platform.openai.com/api-keys"
        Write-Host "   - ElevenLabs: https://elevenlabs.io/app/speech-synthesis"
        Write-Host "   - Twilio: https://console.twilio.com/"
        return $false
    }
    
    Write-Success "All required API keys are configured"
    return $true
}

# Function to check Docker
function Test-Docker {
    Write-Header "DOCKER VALIDATION"
    
    if (-not (Test-Command "docker")) {
        Write-Error "Docker is not installed!"
        Write-Host "Please install Docker Desktop from: https://docs.docker.com/desktop/install/windows/"
        return $false
    }
    
    if (-not (Test-Command "docker-compose") -and -not (Test-Command "docker")) {
        Write-Error "Docker Compose is not available!"
        Write-Host "Please ensure Docker Desktop is properly installed."
        return $false
    }
    
    # Check if Docker daemon is running
    try {
        & docker info | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker daemon not running"
        }
    }
    catch {
        Write-Error "Docker daemon is not running!"
        Write-Host "Please start Docker Desktop and try again."
        return $false
    }
    
    Write-Success "Docker is installed and running"
    return $true
}

# Function to start services
function Start-Services {
    Write-Header "STARTING SERVICES"
    
    Write-Status "Building and starting Docker containers..."
    
    # Stop any existing containers
    try {
        if (Test-Command "docker-compose") {
            & docker-compose down 2>$null
            & docker-compose up --build -d
        }
        else {
            & docker compose down 2>$null
            & docker compose up --build -d
        }
    }
    catch {
        Write-Error "Failed to start Docker services: $_"
        return $false
    }
    
    Write-Status "Waiting for services to start..."
    Start-Sleep -Seconds 20
    
    # Check service status
    Write-Status "Checking service status..."
    try {
        if (Test-Command "docker-compose") {
            & docker-compose ps
        }
        else {
            & docker compose ps
        }
    }
    catch {
        Write-Warning "Could not check service status"
    }
    
    return $true
}

# Function to wait for backend to be ready
function Wait-ForBackend {
    Write-Status "Waiting for backend to be ready..."
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "Backend is ready!"
                return $true
            }
        }
        catch {
            # Continue trying
        }
        
        Write-Status "Attempt $attempt/$maxAttempts - Backend not ready yet..."
        Start-Sleep -Seconds 2
        $attempt++
    }
    
    Write-Error "Backend failed to start within expected time"
    Write-Status "Checking backend logs..."
    try {
        if (Test-Command "docker-compose") {
            & docker-compose logs --tail=20 backend
        }
        else {
            & docker compose logs --tail=20 backend
        }
    }
    catch {
        Write-Warning "Could not retrieve backend logs"
    }
    
    return $false
}

# Function to start ngrok tunnel
function Start-Ngrok {
    Write-Header "STARTING NGROK TUNNEL"
    
    if ($SkipNgrok) {
        Write-Warning "Skipping ngrok tunnel as requested"
        return $true
    }
    
    # Kill any existing ngrok processes
    Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    
    Write-Status "Starting ngrok tunnel on port 8000..."
    
    # Start ngrok in background
    try {
        $NgrokProcess = Start-Process -FilePath "ngrok" -ArgumentList "http", "8000", "--log=stdout" -NoNewWindow -PassThru -RedirectStandardOutput "ngrok.log"
        Start-Sleep -Seconds 5
        
        # Get the public URL
        $maxAttempts = 10
        $attempt = 1
        
        while ($attempt -le $maxAttempts) {
            try {
                $tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 5
                $NgrokUrl = ($tunnels.tunnels | Where-Object { $_.proto -eq "https" }).public_url
                
                if ($NgrokUrl) {
                    Write-Success "ngrok tunnel started successfully!"
                    Write-Host "Public URL: $NgrokUrl"
                    break
                }
            }
            catch {
                # Continue trying
            }
            
            Write-Status "Attempt $attempt/$maxAttempts - Waiting for ngrok tunnel..."
            Start-Sleep -Seconds 2
            $attempt++
        }
        
        if (-not $NgrokUrl) {
            Write-Error "Failed to get ngrok URL"
            Write-Status "Checking ngrok logs..."
            if (Test-Path "ngrok.log") {
                Get-Content "ngrok.log" -Tail 20
            }
            return $false
        }
        
        # Update BASE_URL in .env file
        if (Test-Path $EnvFile) {
            $envContent = Get-Content $EnvFile
            $newContent = @()
            $baseUrlFound = $false
            
            foreach ($line in $envContent) {
                if ($line -match '^BASE_URL=') {
                    $newContent += "BASE_URL=$NgrokUrl"
                    $baseUrlFound = $true
                }
                else {
                    $newContent += $line
                }
            }
            
            if (-not $baseUrlFound) {
                $newContent += "BASE_URL=$NgrokUrl"
            }
            
            $newContent | Set-Content $EnvFile
            Write-Success "Updated BASE_URL in .env file"
        }
        
        # Save ngrok info for later use
        $NgrokUrl | Set-Content ".ngrok_url"
        $NgrokProcess.Id | Set-Content ".ngrok_pid"
        
        return $true
    }
    catch {
        Write-Error "Failed to start ngrok: $_"
        return $false
    }
}

# Function to test system health
function Test-System {
    Write-Header "SYSTEM HEALTH CHECK"
    
    Write-Status "Testing backend health..."
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
        
        if ($healthResponse.status -eq "healthy") {
            Write-Success "Backend health check passed"
        }
        else {
            Write-Error "Backend health check failed"
            Write-Host "Response: $($healthResponse | ConvertTo-Json)"
            return $false
        }
    }
    catch {
        Write-Error "Backend health check failed: $_"
        return $false
    }
    
    Write-Status "Testing frontend..."
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        Write-Success "Frontend is accessible"
    }
    catch {
        Write-Warning "Frontend may still be starting up"
    }
    
    if ($NgrokUrl) {
        Write-Status "Testing ngrok tunnel..."
        try {
            $tunnelResponse = Invoke-WebRequest -Uri "$NgrokUrl/health" -UseBasicParsing -TimeoutSec 10
            Write-Success "ngrok tunnel is working"
        }
        catch {
            Write-Warning "ngrok tunnel may not be fully ready yet"
        }
    }
    
    return $true
}

# Function to display final instructions
function Show-FinalInstructions {
    Write-Header "SETUP COMPLETE!"
    
    Write-Host ""
    Write-Host "🎉 Your AI Voice Agent MVP is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Access URLs:" -ForegroundColor Cyan
    Write-Host "   • Frontend Dashboard: http://localhost:3000"
    Write-Host "   • Backend API: http://localhost:8000"
    Write-Host "   • API Documentation: http://localhost:8000/docs"
    if ($NgrokUrl) {
        Write-Host "   • Public URL (ngrok): $NgrokUrl"
    }
    Write-Host ""
    
    # Read Twilio phone number from .env
    $envVars = @{}
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $envVars[$matches[1]] = $matches[2]
        }
    }
    
    if ($NgrokUrl -and $envVars.ContainsKey("TWILIO_PHONE_NUMBER")) {
        Write-Host "📞 Twilio Configuration:" -ForegroundColor Cyan
        Write-Host "   1. Go to: https://console.twilio.com/"
        Write-Host "   2. Navigate to: Phone Numbers > Manage > Active numbers"
        Write-Host "   3. Click your phone number: $($envVars['TWILIO_PHONE_NUMBER'])"
        Write-Host "   4. Set Voice Webhook to:"
        Write-Host "      $NgrokUrl/api/v1/voice/twilio/webhook/{call_id}"
        Write-Host "   5. Set Status Callback to:"
        Write-Host "      $NgrokUrl/api/v1/voice/twilio/status/{call_id}"
        Write-Host "   6. Save the configuration"
        Write-Host ""
        Write-Host "🧪 Testing:" -ForegroundColor Cyan
        Write-Host "   • Call your Twilio number: $($envVars['TWILIO_PHONE_NUMBER'])"
        Write-Host "   • The AI agent should answer and have a conversation"
        Write-Host "   • Check the dashboard for call logs and transcripts"
        Write-Host ""
    }
    
    Write-Host "📋 Useful Commands:" -ForegroundColor Cyan
    Write-Host "   • View logs: docker-compose logs -f"
    Write-Host "   • Stop system: docker-compose down"
    if ($NgrokProcess) {
        Write-Host "   • Stop ngrok: Stop-Process -Id $($NgrokProcess.Id)"
    }
    Write-Host "   • Restart: .\setup-mvp.ps1"
    Write-Host ""
    Write-Host "⚠️  Important Notes:" -ForegroundColor Yellow
    Write-Host "   • Keep this PowerShell window open to maintain the ngrok tunnel"
    Write-Host "   • The ngrok URL changes each time you restart (free plan)"
    Write-Host "   • Update Twilio webhooks if you restart ngrok"
    Write-Host "   • Check logs if calls don't work as expected"
    Write-Host ""
    Write-Host "🚀 Your AI voice agent is ready to take calls!" -ForegroundColor Green
}

# Function to cleanup on exit
function Cleanup {
    Write-Status "Cleaning up..."
    
    if (Test-Path ".ngrok_pid") {
        try {
            $ngrokPid = Get-Content ".ngrok_pid"
            Stop-Process -Id $ngrokPid -Force -ErrorAction SilentlyContinue
        }
        catch {
            # Ignore errors
        }
        Remove-Item ".ngrok_pid", ".ngrok_url", "ngrok.log" -Force -ErrorAction SilentlyContinue
    }
    
    if ($NgrokProcess) {
        try {
            Stop-Process -Id $NgrokProcess.Id -Force -ErrorAction SilentlyContinue
        }
        catch {
            # Ignore errors
        }
    }
}

# Main execution
function Main {
    try {
        Write-Header "AI VOICE AGENT MVP SETUP"
        Write-Host "This script will set up your complete AI voice agent with ngrok integration"
        Write-Host ""
        
        # Validate prerequisites
        if (-not (Test-Environment)) { exit 1 }
        if (-not (Test-Docker)) { exit 1 }
        if (-not (Setup-Ngrok)) { exit 1 }
        
        # Start services
        if (-not (Start-Services)) { exit 1 }
        if (-not (Wait-ForBackend)) { exit 1 }
        if (-not (Start-Ngrok)) { exit 1 }
        
        # Test system
        if (-not (Test-System)) {
            Write-Warning "Some health checks failed, but system may still work"
        }
        
        # Show final instructions
        Show-FinalInstructions
        
        # Keep script running to maintain ngrok tunnel
        if ($NgrokProcess -and -not $SkipNgrok) {
            Write-Host ""
            Write-Status "Press Ctrl+C to stop the system and ngrok tunnel"
            Write-Host ""
            
            # Monitor system
            try {
                while ($true) {
                    Start-Sleep -Seconds 30
                    
                    try {
                        Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 | Out-Null
                    }
                    catch {
                        Write-Warning "Backend health check failed - system may be down"
                    }
                    
                    if ($NgrokUrl) {
                        try {
                            Invoke-WebRequest -Uri "$NgrokUrl/health" -UseBasicParsing -TimeoutSec 5 | Out-Null
                        }
                        catch {
                            Write-Warning "ngrok tunnel may be down"
                        }
                    }
                }
            }
            catch {
                # User pressed Ctrl+C
                Write-Status "Shutting down..."
            }
        }
    }
    finally {
        Cleanup
    }
}

# Handle Ctrl+C gracefully
$null = Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

# Run main function
Main