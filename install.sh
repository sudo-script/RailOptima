#!/bin/bash

# RailOptima Installation Script for Unix-like systems (Linux/macOS)
# This script sets up RailOptima on Unix-like systems

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Print colored output
print_colored() {
    echo -e "${1}${2}${NC}"
}

print_header() {
    print_colored $CYAN "============================================================"
    print_colored $CYAN "  $1"
    print_colored $CYAN "============================================================"
}

print_step() {
    print_colored $YELLOW "\n[$1] $2"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_step "1" "Checking Prerequisites"
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_colored $GREEN "✅ Python $PYTHON_VERSION found"
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_colored $GREEN "✅ Python $PYTHON_VERSION found"
        else
            print_colored $RED "❌ Python 3.x is required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_colored $RED "❌ Python is not installed"
        print_colored $YELLOW "Please install Python 3.8+ from https://python.org"
        exit 1
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_colored $GREEN "✅ Node.js $NODE_VERSION found"
    else
        print_colored $RED "❌ Node.js is not installed"
        print_colored $YELLOW "Please install Node.js from https://nodejs.org"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_colored $GREEN "✅ npm $NPM_VERSION found"
    else
        print_colored $RED "❌ npm is not installed"
        exit 1
    fi
}

# Setup Python environment
setup_python() {
    print_step "2" "Setting up Python Environment"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_colored $BLUE "Creating virtual environment..."
        if command_exists python3; then
            python3 -m venv venv
        else
            python -m venv venv
        fi
        print_colored $GREEN "✅ Virtual environment created"
    else
        print_colored $GREEN "✅ Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_colored $BLUE "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_colored $BLUE "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_colored $BLUE "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_colored $GREEN "✅ Python environment setup complete"
}

# Setup Node.js environment
setup_node() {
    print_step "3" "Setting up Node.js Environment"
    
    if [ -d "SIHH-main" ]; then
        print_colored $BLUE "Installing frontend dependencies..."
        cd SIHH-main
        npm install
        cd ..
        print_colored $GREEN "✅ Frontend dependencies installed"
    else
        print_colored $YELLOW "⚠️ Frontend directory not found, skipping frontend setup"
    fi
}

# Create environment file
create_env_file() {
    print_step "4" "Creating Environment Configuration"
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_colored $GREEN "✅ Created .env file from template"
        else
            print_colored $YELLOW "⚠️ env.example not found, creating basic .env file"
            cat > .env << EOF
# RailOptima Environment Configuration
API_HOST=localhost
API_PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000
FRONTEND_PORT=9002
DEBUG=true
ENVIRONMENT=development
EOF
        fi
        print_colored $YELLOW "📝 Please review and update .env file with your configuration"
    else
        print_colored $GREEN "✅ .env file already exists"
    fi
}

# Create directories
create_directories() {
    print_step "5" "Creating Required Directories"
    
    directories=("reports" "logs" "data" "temp")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_colored $GREEN "✅ Created directory: $dir"
        else
            print_colored $GREEN "✅ Directory already exists: $dir"
        fi
    done
}

# Test installation
test_installation() {
    print_step "6" "Testing Installation"
    
    # Activate virtual environment for testing
    source venv/bin/activate
    
    # Test Python imports
    print_colored $BLUE "Testing Python dependencies..."
    python -c "
import pandas
import matplotlib
import fastapi
print('✅ Python dependencies imported successfully')
" 2>/dev/null || {
        print_colored $RED "❌ Python dependency import failed"
        return 1
    }
    
    # Test frontend
    if [ -d "SIHH-main" ] && [ -d "SIHH-main/node_modules" ]; then
        print_colored $GREEN "✅ Frontend dependencies installed successfully"
    else
        print_colored $YELLOW "⚠️ Frontend dependencies may not be properly installed"
    fi
    
    return 0
}

# Print next steps
print_next_steps() {
    print_header "Installation Complete!"
    
    print_colored $WHITE "\n🚀 Next Steps:"
    print_colored $WHITE "1. Review and update the .env file with your configuration"
    print_colored $WHITE "2. Activate the virtual environment:"
    print_colored $CYAN "   source venv/bin/activate"
    print_colored $WHITE "3. Start the application:"
    print_colored $CYAN "   python setup-environment.py"
    print_colored $CYAN "   # OR manually start the services"
    
    print_colored $WHITE "\n📊 Access URLs:"
    print_colored $CYAN "   - Frontend: http://localhost:9002"
    print_colored $CYAN "   - API: http://localhost:8000"
    print_colored $CYAN "   - API Docs: http://localhost:8000/docs"
    
    print_colored $WHITE "\n📚 Documentation:"
    print_colored $WHITE "   - README.md - Main documentation"
    print_colored $WHITE "   - docs/ - Detailed module documentation"
    
    print_colored $WHITE "\n🐳 Docker Support:"
    print_colored $WHITE "   - docker-compose up -d (production)"
    print_colored $WHITE "   - docker-compose --profile dev up (development)"
}

# Main installation function
main() {
    print_header "RailOptima Installation"
    print_colored $WHITE "This script will install RailOptima on your system."
    
    # Run installation steps
    check_prerequisites
    setup_python
    setup_node
    create_env_file
    create_directories
    
    if test_installation; then
        print_next_steps
        print_colored $GREEN "\n🎉 Installation completed successfully!"
        exit 0
    else
        print_colored $RED "\n❌ Installation failed. Please check the errors above."
        exit 1
    fi
}

# Handle script interruption
trap 'print_colored $YELLOW "\n\nInstallation cancelled by user."; exit 1' INT

# Run main function
main "$@"
