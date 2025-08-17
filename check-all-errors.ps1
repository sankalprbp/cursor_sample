# Complete Error Checking Script
Write-Host "AI Voice Agent MVP - Complete Error Check" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue
Write-Host ""

$ErrorCount = 0

function Test-FileExists {
    param([string]$FilePath, [string]$Description)
    Write-Host "Checking $Description... " -NoNewline
    if (Test-Path $FilePath) {
        Write-Host "OK" -ForegroundColor Green
        return $true
    } else {
        Write-Host "MISSING" -ForegroundColor Red
        $script:ErrorCount++
        return $false
    }
}

function Test-FileContent {
    param([string]$FilePath, [string]$Pattern, [string]$Description)
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $Pattern) {
            Write-Host "$Description - OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "$Description - FAILED" -ForegroundColor Red
            $script:ErrorCount++
            return $false
        }
    } else {
        Write-Host "File not found: $FilePath" -ForegroundColor Red
        $script:ErrorCount++
        return $false
    }
}

Write-Host "Core Files Check:" -ForegroundColor Cyan
Test-FileExists "frontend/src/app/dashboard/page.tsx" "Dashboard Page"
Test-FileExists "backend/main.py" "Backend Main"
Test-FileExists "docker-compose.yml" "Docker Compose"
Test-FileExists ".env.example" "Environment Template"

Write-Host ""
Write-Host "Frontend Check:" -ForegroundColor Cyan
Test-FileContent "frontend/src/app/dashboard/page.tsx" "export default function Dashboard" "Dashboard Export"
Test-FileContent "frontend/package.json" "next" "Next.js Dependency"

Write-Host ""
Write-Host "Backend Check:" -ForegroundColor Cyan
Test-FileContent "backend/main.py" "FastAPI" "FastAPI Import"
Test-FileContent "backend/requirements.txt" "fastapi" "FastAPI Dependency"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Blue

if ($ErrorCount -eq 0) {
    Write-Host "ALL CHECKS PASSED - NO ERRORS FOUND!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FOUND $ErrorCount ERRORS" -ForegroundColor Red
    exit 1
}