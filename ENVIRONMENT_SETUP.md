# RailOptima Environment Setup Guide

This guide provides comprehensive instructions for setting up RailOptima on any machine, ensuring the project runs consistently across different environments.

## 📋 Prerequisites

Before setting up RailOptima, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download from python.org](https://python.org)
- **Node.js 16+** - [Download from nodejs.org](https://nodejs.org)
- **npm** (comes with Node.js)

### Optional Software
- **Docker** - [Download from docker.com](https://docker.com) (for containerized deployment)
- **Git** - [Download from git-scm.com](https://git-scm.com) (for version control)

## 🚀 Quick Setup (Recommended)

### Windows
1. **Run the installation script:**
   ```cmd
   install.bat
   ```

2. **Or use PowerShell:**
   ```powershell
   python setup-environment.py
   ```

### Linux/macOS
1. **Make the script executable:**
   ```bash
   chmod +x install.sh
   ```

2. **Run the installation script:**
   ```bash
   ./install.sh
   ```

3. **Or use Python setup:**
   ```bash
   python3 setup-environment.py
   ```

## 🔧 Manual Setup

If you prefer to set up the environment manually:

### 1. Clone/Download the Project
```bash
git clone <repository-url>
cd RailOptima
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Node.js Environment
```bash
# Navigate to frontend directory
cd SIHH-main

# Install dependencies
npm install

# Return to project root
cd ..
```

### 4. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# (See Environment Variables section below)
```

### 5. Create Required Directories
```bash
mkdir -p reports logs data temp
```

## 🐳 Docker Setup

For containerized deployment:

### Production Environment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Development Environment
```bash
# Start development environment with hot reload
docker-compose --profile dev up

# Or build development image
docker build -f Dockerfile.dev -t railoptima-dev .
docker run -p 8000:8000 -p 9002:9002 -v $(pwd):/app railoptima-dev
```

### Individual Services
```bash
# Start only API
docker-compose up api

# Start only frontend
docker-compose up frontend
```

## ⚙️ Environment Variables

The `.env` file contains configuration for the application. Key variables:

### API Configuration
```env
API_HOST=localhost          # API server host
API_PORT=8000              # API server port
API_BASE_URL=http://localhost:8000  # Full API URL
```

### Frontend Configuration
```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # API URL for frontend
FRONTEND_PORT=9002         # Frontend server port
NEXT_PUBLIC_APP_NAME=RailOptima  # Application name
```

### Development Settings
```env
DEBUG=true                 # Enable debug mode
ENVIRONMENT=development    # Environment type
LOG_LEVEL=INFO            # Logging level
```

### Optional Services
```env
# Database (if using)
DATABASE_URL=sqlite:///./railoptima.db

# External APIs
GOOGLE_AI_API_KEY=your_key_here
FIREBASE_PROJECT_ID=your_project_id
```

## 🏃‍♂️ Running the Application

### Method 1: Using Startup Scripts
```bash
# Windows
start-railoptima.bat
# or
start-railoptima.ps1

# Linux/macOS
./start-railoptima.sh  # (if available)
```

### Method 2: Manual Start
```bash
# Terminal 1: Start API Backend
cd support/api_support
python api_stub.py

# Terminal 2: Start Frontend
cd SIHH-main
npm run dev
```

### Method 3: Using Python Setup Script
```bash
python setup-environment.py
```

## 🌐 Access URLs

Once running, access the application at:

- **Frontend**: http://localhost:9002
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Troubleshooting

### Common Issues

#### Python Dependencies
```bash
# If pip install fails, try:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# For specific package issues:
pip install --force-reinstall <package-name>
```

#### Node.js Dependencies
```bash
# Clear npm cache and reinstall
cd SIHH-main
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Port Conflicts
If ports 8000 or 9002 are in use:
1. Update `.env` file with different ports
2. Or stop conflicting services:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # Linux/macOS
   lsof -ti:8000 | xargs kill -9
   ```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Platform-Specific Issues

#### Windows
- Ensure Python and Node.js are in PATH
- Run PowerShell as Administrator if needed
- Check Windows Defender/antivirus settings

#### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for easier package management

#### Linux
- Install build essentials: `sudo apt-get install build-essential`
- Ensure proper permissions for scripts: `chmod +x *.sh`

## 📁 Project Structure

```
RailOptima/
├── optimizer/              # Core optimization logic
├── support/               # API support and utilities
├── SIHH-main/            # Frontend application
├── Audit/                # Audit and validation tools
├── docs/                 # Documentation
├── reports/              # Generated reports
├── docker/               # Docker configuration
├── requirements.txt      # Python dependencies
├── env.example          # Environment template
├── .env                 # Environment configuration
├── setup-environment.py # Python setup script
├── install.sh           # Unix installation script
├── install.bat          # Windows installation script
├── Dockerfile           # Production Docker image
├── Dockerfile.dev       # Development Docker image
└── docker-compose.yml   # Docker services
```

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
# Python dependencies
pip install -r requirements.txt --upgrade

# Node.js dependencies
cd SIHH-main
npm update
```

### Environment Refresh
```bash
# Recreate environment from scratch
rm -rf venv node_modules
python setup-environment.py
```

## 📞 Support

If you encounter issues:

1. Check this documentation
2. Review the logs in `reports/` directory
3. Check the troubleshooting section above
4. Ensure all prerequisites are installed correctly

## 🎯 Next Steps

After successful setup:

1. Review the main [README.md](README.md) for usage instructions
2. Explore the [docs/](docs/) directory for detailed module documentation
3. Check the [API documentation](http://localhost:8000/docs) when running
4. Customize the `.env` file for your specific needs

---

**Happy coding with RailOptima! 🚆**
