#!/bin/bash
echo "Starting Real-time Meeting Translator..."

# Start AI service
cd ai
uvicorn main:app --reload --port 8001 &

# Start backend
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &

# Start frontend
cd ../frontend
npm run dev &

echo "Services starting..."
echo "AI: http://localhost:8001"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"