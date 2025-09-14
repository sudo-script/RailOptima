@echo off
echo ========================================
echo    RailOptima Development Launcher
echo ========================================
echo.

echo Starting Backend (FastAPI)...
start "RailOptima Backend" cmd /k "cd /d %~dp0support\api_support && python api_stub.py"

echo.
echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting Frontend (Next.js)...
start "RailOptima Frontend" cmd /k "cd /d %~dp0SIHH-main && npm run dev"

echo.
echo ========================================
echo    Both servers are starting...
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend:     http://localhost:9002
echo API Docs:     http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause > nul
