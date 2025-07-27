#!/bin/bash

# Campus Underground - Start All Services Script
# This script starts both the backend and frontend services for the Campus Underground project

# Print colored text
print_color() {
  local color=$1
  local text=$2
  
  case $color in
    "green") echo -e "\033[0;32m$text\033[0m" ;;
    "yellow") echo -e "\033[0;33m$text\033[0m" ;;
    "blue") echo -e "\033[0;34m$text\033[0m" ;;
    "red") echo -e "\033[0;31m$text\033[0m" ;;
    *) echo "$text" ;;
  esac
}

# Check if .env files exist and create them if they don't
check_env_files() {
  print_color "blue" "Checking environment files..."
  
  # Check backend Moodle service .env
  if [ ! -f "./campus-underground-backend/moodle_service/.env" ]; then
    print_color "yellow" "Creating Moodle service .env file..."
    cat > ./campus-underground-backend/moodle_service/.env << EOL
# Moodle API Configuration
MOODLE_URL=https://moodle.concordia.ca
MOODLE_API_TOKEN=your_moodle_api_token_here

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

FLASK_SECRET_KEY=campus-underground-secret-key
PORT=5002
EOL
    print_color "green" "Created Moodle service .env file"
    print_color "yellow" "Please update the API tokens in ./campus-underground-backend/moodle_service/.env"
  fi
  
  # Check frontend .env
  if [ ! -f "./campus-underground-frontend/.env" ]; then
    print_color "yellow" "Creating frontend .env file..."
    cat > ./campus-underground-frontend/.env << EOL
# API Configuration
REACT_APP_API_URL=http://localhost:5000
REACT_APP_PYTHON_API_URL=http://localhost:5002

# Supabase Configuration
REACT_APP_SUPABASE_URL=your_supabase_url_here
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Socket.io Configuration
REACT_APP_SOCKET_URL=http://localhost:5000
EOL
    print_color "green" "Created frontend .env file"
    print_color "yellow" "Please update the API keys in ./campus-underground-frontend/.env"
  fi
}

# Start the Python Moodle API service
start_moodle_service() {
  print_color "blue" "Starting Moodle API service..."
  
  # Check if Python is installed
  if ! command -v python3 &> /dev/null; then
    print_color "red" "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
  fi
  
  # Check if virtual environment exists, create if it doesn't
  if [ ! -d "./campus-underground-backend/moodle_service/venv" ]; then
    print_color "yellow" "Creating Python virtual environment..."
    cd ./campus-underground-backend/moodle_service
    python3 -m venv venv
    cd ../../
  fi
  
  # Activate virtual environment and install dependencies
  print_color "yellow" "Installing Python dependencies..."
  cd ./campus-underground-backend/moodle_service
  source venv/bin/activate || source venv/Scripts/activate
  pip install -r requirements.txt
  
  # Start the Flask server in the background
  print_color "green" "Starting Flask API server..."
  python api_server.py &
  MOODLE_PID=$!
  cd ../../
  
  # Save the PID to a file for later cleanup
  echo $MOODLE_PID > .moodle_service_pid
  
  print_color "green" "Moodle API service started on http://localhost:5002"
}

# Start the frontend development server
start_frontend() {
  print_color "blue" "Starting frontend development server..."
  
  # Check if Node.js is installed
  if ! command -v node &> /dev/null; then
    print_color "red" "Node.js is not installed. Please install Node.js and try again."
    exit 1
  fi
  
  # Install dependencies if node_modules doesn't exist
  if [ ! -d "./campus-underground-frontend/node_modules" ]; then
    print_color "yellow" "Installing frontend dependencies..."
    cd ./campus-underground-frontend
    npm install
    cd ..
  fi
  
  # Start the React development server
  print_color "green" "Starting React development server..."
  cd ./campus-underground-frontend
  PORT=3001 npm start &
  FRONTEND_PID=$!
  cd ..
  
  # Save the PID to a file for later cleanup
  echo $FRONTEND_PID > .frontend_pid
  
  print_color "green" "Frontend server started on http://localhost:3001"
}

# Cleanup function to kill processes on exit
cleanup() {
  print_color "yellow" "Stopping all services..."
  
  if [ -f ".moodle_service_pid" ]; then
    MOODLE_PID=$(cat .moodle_service_pid)
    kill $MOODLE_PID 2>/dev/null
    rm .moodle_service_pid
  fi
  
  if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill $FRONTEND_PID 2>/dev/null
    rm .frontend_pid
  fi
  
  print_color "green" "All services stopped"
  exit 0
}

# Set up trap to catch Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM

# Main function
main() {
  print_color "blue" "=== Campus Underground - Starting All Services ==="
  
  # Check and create .env files if needed
  check_env_files
  
  # Start services
  start_moodle_service
  start_frontend
  
  print_color "green" "=== All services started successfully ==="
  print_color "yellow" "Press Ctrl+C to stop all services"
  
  # Keep the script running to maintain background processes
  while true; do
    sleep 1
  done
}

# Run the main function
main
