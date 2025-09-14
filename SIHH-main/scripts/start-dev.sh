#!/bin/bash

# Start both frontend and backend for development

echo "Starting RailOptima Development Environment..."

# Start FastAPI backend in background
echo "Starting FastAPI backend on port 8000..."
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py &
BACKEND_PID=$!

# Go back to root directory
cd ..

# Start Next.js frontend
echo "Starting Next.js frontend on port 3000..."
npm run dev &
FRONTEND_PID=$!

echo "Development environment started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "Backend Docs: http://localhost:8000/docs"

# Wait for user to stop
echo "Press Ctrl+C to stop both servers"
wait $BACKEND_PID $FRONTEND_PID
