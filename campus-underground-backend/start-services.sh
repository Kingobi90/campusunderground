#!/bin/bash

# Start Campus Underground Backend Services
# This script starts both the TypeScript backend and the Python Moodle service

echo "🚀 Starting Campus Underground Backend Services..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 to use the Moodle service."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js to run the TypeScript backend."
    exit 1
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "moodle_service/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd moodle_service
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Python virtual environment already exists."
fi

# Check if .env files exist, create from examples if not
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from example..."
    cp env.example .env
    echo "⚠️ Please update the .env file with your configuration."
fi

if [ ! -f "moodle_service/.env" ]; then
    echo "📄 Creating Moodle service .env file from example..."
    cp moodle_service/.env.example moodle_service/.env
    echo "⚠️ Please update the moodle_service/.env file with your Moodle API token."
fi

# Start the Python Moodle service in the background
echo "🐍 Starting Python Moodle service..."
cd moodle_service
source venv/bin/activate
python api_server.py &
MOODLE_PID=$!
cd ..

# Wait a moment for the Moodle service to start
sleep 2

# Start the TypeScript backend
echo "📡 Starting TypeScript backend..."
npm run dev

# When the TypeScript backend is stopped, also stop the Moodle service
echo "Stopping services..."
kill $MOODLE_PID

echo "✅ All services stopped."
