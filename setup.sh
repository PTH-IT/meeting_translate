#!/bin/bash
echo "Setting up Real-time Meeting Translator..."

# Setup backend
cd backend
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

echo "Setup complete! Run ./start.sh to launch."