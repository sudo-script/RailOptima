@echo off
echo Starting RailOptima System...

echo.
echo Starting API Backend on port 8000...
start "RailOptima API" cmd /k "cd /d "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\support\api_support" && python api_stub.py"

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend on port 9002...
start "RailOptima Frontend" cmd /k "cd /d "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\SIHH-main" && npm run dev"

echo.
echo ✅ RailOptima System Started!
echo 📊 API Backend: http://localhost:8000
echo 📊 API Docs: http://localhost:8000/docs
echo 🌐 Frontend: http://localhost:9002
echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
pause
