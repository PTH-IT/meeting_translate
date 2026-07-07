# PowerShell script to start all services
Write-Host "Starting Real-time Meeting Translator..."

# Start AI service
Start-Process -FilePath "powershell" -ArgumentList "-Command `cd '$PWD\ai'; uvicorn main:app --reload --port 8001`" -WindowStyle NewWindow

# Start backend
Start-Process -FilePath "powershell" -ArgumentList "-Command `cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000`" -WindowStyle NewWindow

# Start frontend
Start-Process -FilePath "powershell" -ArgumentList "-Command `cd '$PWD\frontend'; npm run dev`" -WindowStyle NewWindow

Write-Host "Services starting..."
Write-Host "AI: http://localhost:8001"
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"