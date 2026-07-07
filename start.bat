@echo off
echo Starting Real-time Meeting Translator...

REM Start AI service in new window
cd ai
start "AI Service" cmd /c "uvicorn main:app --reload --port 8001"

REM Start backend in new window
cd ..\backend
start "Backend Server" cmd /c "venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

REM Start frontend
cd ..\frontend
start "Frontend Dev" cmd /c "npm run dev"

echo Services starting...
echo AI: http://localhost:8001
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000