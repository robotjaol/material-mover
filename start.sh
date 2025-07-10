#!/bin/bash

echo "Starting Pallet Flow Diagnostic Platform..."

# Start backend server
echo "Starting FastAPI backend server..."
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "Starting Next.js frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Platform is starting up..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait $BACKEND_PID $FRONTEND_PID 