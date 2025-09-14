@echo off
REM RailOptima Installation Script for Windows
REM This script sets up RailOptima on Windows systems

setlocal enabledelayedexpansion

echo ============================================================
echo   RailOptima Installation Script for Windows
echo ============================================================
echo.

REM Check if Python is installed
echo [1] Checking Prerequisites...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! found
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
) else (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js !NODE_VERSION! found
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed
    pause
    exit /b 1
) else (
    for /f %%i in ('npm --version') do set NPM_VERSION=%%i
    echo ✅ npm !NPM_VERSION! found
)

echo.
echo [2] Setting up Python Environment...

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed

echo.
echo [3] Setting up Node.js Environment...

REM Setup frontend if directory exists
if exist "SIHH-main" (
    echo Installing frontend dependencies...
    cd SIHH-main
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install frontend dependencies
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Frontend dependencies installed
) else (
    echo ⚠️ Frontend directory not found, skipping frontend setup
)

echo.
echo [4] Creating Environment Configuration...

REM Create .env file
if not exist ".env" (
    if exist "env.example" (
        copy env.example .env >nul
        echo ✅ Created .env file from template
    ) else (
        echo Creating basic .env file...
        (
            echo # RailOptima Environment Configuration
            echo API_HOST=localhost
            echo API_PORT=8000
            echo NEXT_PUBLIC_API_URL=http://localhost:8000
            echo FRONTEND_PORT=9002
            echo DEBUG=true
            echo ENVIRONMENT=development
        ) > .env
        echo ✅ Created basic .env file
    )
    echo 📝 Please review and update .env file with your configuration
) else (
    echo ✅ .env file already exists
)

echo.
echo [5] Creating Required Directories...

REM Create directories
set directories=reports logs data temp
for %%d in (%directories%) do (
    if not exist "%%d" (
        mkdir "%%d" >nul 2>&1
        echo ✅ Created directory: %%d
    ) else (
        echo ✅ Directory already exists: %%d
    )
)

echo.
echo [6] Testing Installation...

REM Test Python imports
echo Testing Python dependencies...
python -c "import pandas, matplotlib, fastapi; print('✅ Python dependencies imported successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python dependency import failed
    pause
    exit /b 1
)

REM Test frontend
if exist "SIHH-main\node_modules" (
    echo ✅ Frontend dependencies installed successfully
) else (
    echo ⚠️ Frontend dependencies may not be properly installed
)

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo 🚀 Next Steps:
echo 1. Review and update the .env file with your configuration
echo 2. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo 3. Start the application:
echo    start-railoptima.bat
echo    OR
echo    start-railoptima.ps1
echo.
echo 📊 Access URLs:
echo    - Frontend: http://localhost:9002
echo    - API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo 📚 Documentation:
echo    - README.md - Main documentation
echo    - docs/ - Detailed module documentation
echo.
echo 🐳 Docker Support:
echo    - docker-compose up -d (production)
echo    - docker-compose --profile dev up (development)
echo.
echo 🎉 Installation completed successfully!
echo.
pause
