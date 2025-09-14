# RailOptima Startup Script for PowerShell
# This script starts both the API backend and frontend

Write-Host "Starting RailOptima System..." -ForegroundColor Green

# Check if Python is available
try {
    
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found! Please install Node.js first." -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Start API Backend
Write-Host "Starting API Backend on port 8000..." -ForegroundColor Yellow
$apiJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\support\api_support"
    python api_stub.py
}

# Wait a moment for API to start
Start-Sleep -Seconds 3

# Test API health
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✅ API Backend is running successfully!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ API Backend may not be ready yet. Check manually at http://localhost:8000/health" -ForegroundColor Yellow
}

# Start Frontend
Write-Host "Starting Frontend on port 9002..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\SIHH-main"
    npm run dev
}

# Wait for frontend to start
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🚀 RailOptima System Started!" -ForegroundColor Green
Write-Host "📊 API Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:9002" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow

# Keep script running and show job status
try {
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Check if jobs are still running
        $apiStatus = Get-Job -Id $apiJob.Id | Select-Object -ExpandProperty State
        $frontendStatus = Get-Job -Id $frontendJob.Id | Select-Object -ExpandProperty State
        
        if ($apiStatus -eq "Failed") {
            Write-Host "❌ API Backend failed!" -ForegroundColor Red
            Receive-Job -Id $apiJob.Id
        }
        
        if ($frontendStatus -eq "Failed") {
            Write-Host "❌ Frontend failed!" -ForegroundColor Red
            Receive-Job -Id $frontendJob.Id
        }
    }
} finally {
    # Cleanup jobs when script exits
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Job -Id $apiJob.Id, $frontendJob.Id
    Remove-Job -Id $apiJob.Id, $frontendJob.Id
    Write-Host "Services stopped." -ForegroundColor Green
}
