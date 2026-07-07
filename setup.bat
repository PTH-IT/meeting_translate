@echo off
echo Setting up Real-time Meeting Translator...

REM Setup backend
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt

REM Setup frontend
cd ..\frontend
npm install

echo Setup complete! Run start.bat to launch.