#!/bin/bash

# RailOptima Startup Script for Unix-like systems (Linux/macOS)
# This script starts both the API backend and frontend

set -e

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
    print_colored $CYAN "========================================"
    print_colored $CYAN "    RailOptima Development Launcher"
    print_colored $CYAN "========================================"
    echo
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_colored $RED "❌ Virtual environment not found!"
        print_colored $YELLOW "Please run the setup script first:"
        print_colored $WHITE "  ./install.sh"
        print_colored $WHITE "  OR"
        print_colored $WHITE "  python setup-environment.py"
        exit 1
    fi
}

# Check if frontend dependencies are installed
check_frontend() {
    if [ ! -d "SIHH-main/node_modules" ]; then
        print_colored $YELLOW "⚠️ Frontend dependencies not found!"
        print_colored $BLUE "Installing frontend dependencies..."
        cd SIHH-main
        npm install
        cd ..
        print_colored $GREEN "✅ Frontend dependencies installed"
    fi
}

# Start API backend
start_api() {
    print_colored $GREEN "Starting Backend (FastAPI)..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start API in background
    cd support/api_support
    python api_stub.py &
    API_PID=$!
    cd ../..
    
    print_colored $GREEN "✅ Backend started (PID: $API_PID)"
}

# Start frontend
start_frontend() {
    print_colored $GREEN "Starting Frontend (Next.js)..."
    
    cd SIHH-main
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    print_colored $GREEN "✅ Frontend started (PID: $FRONTEND_PID)"
}

# Wait for services to start
wait_for_services() {
    print_colored $YELLOW "Waiting for services to start..."
    
    # Wait for API
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_colored $GREEN "✅ API is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_colored $YELLOW "⚠️ API may not be ready yet"
        fi
        sleep 1
    done
    
    # Wait for frontend
    for i in {1..30}; do
        if curl -s http://localhost:9002 > /dev/null 2>&1; then
            print_colored $GREEN "✅ Frontend is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_colored $YELLOW "⚠️ Frontend may not be ready yet"
        fi
        sleep 1
    done
}

# Show access information
show_access_info() {
    echo
    print_colored $CYAN "========================================"
    print_colored $CYAN "    Both servers are running!"
    print_colored $CYAN "========================================"
    echo
    print_colored $WHITE "Backend API:  http://localhost:8000"
    print_colored $WHITE "Frontend:     http://localhost:9002"
    print_colored $WHITE "API Docs:     http://localhost:8000/docs"
    echo
    print_colored $YELLOW "Press Ctrl+C to stop both services"
    echo
}

# Cleanup function
cleanup() {
    print_colored $YELLOW "Stopping services..."
    
    # Kill background processes
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on the ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:9002 | xargs kill -9 2>/dev/null || true
    
    print_colored $GREEN "Services stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_header
    
    # Check prerequisites
    check_venv
    check_frontend
    
    # Start services
    start_api
    sleep 3
    start_frontend
    
    # Wait for services to be ready
    wait_for_services
    
    # Show access information
    show_access_info
    
    # Keep script running
    while true; do
        sleep 10
        
        # Check if processes are still running
        if ! kill -0 $API_PID 2>/dev/null; then
            print_colored $RED "❌ API Backend stopped unexpectedly!"
            break
        fi
        
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            print_colored $RED "❌ Frontend stopped unexpectedly!"
            break
        fi
    done
}

# Run main function
main "$@"
