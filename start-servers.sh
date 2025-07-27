#!/bin/bash

# Start the Moodle API client (Python Flask app)
cd "$(dirname "$0")/moodle-api-client"
source venv/bin/activate
python web_app.py &
MOODLE_PID=$!
echo "Started Moodle API client (PID: $MOODLE_PID)"

# Start the Node.js backend
cd "$(dirname "$0")/campus-underground-backend"
npm run dev &
BACKEND_PID=$!
echo "Started Node.js backend (PID: $BACKEND_PID)"

# Start the React frontend
cd "$(dirname "$0")/campus-underground-frontend"
npm start &
FRONTEND_PID=$!
echo "Started React frontend (PID: $FRONTEND_PID)"

echo "All servers are running!"
echo "- Moodle API client: http://localhost:5000"
echo "- Node.js backend: http://localhost:5001"
echo "- React frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to kill all processes when script is terminated
function cleanup {
  echo "Stopping all servers..."
  kill $MOODLE_PID $BACKEND_PID $FRONTEND_PID
  exit 0
}

# Register the cleanup function to run when script receives SIGINT
trap cleanup SIGINT

# Keep the script running
wait
