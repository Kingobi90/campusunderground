#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Campus Underground Project...${NC}"

# Define default ports
MOODLE_PORT=5000
BACKEND_PORT=5002
FRONTEND_PORT=3001

# Check if ports are available, if not increment until available
check_port() {
  local port=$1
  local service=$2
  while lsof -i :$port >/dev/null 2>&1; do
    echo -e "${YELLOW}Port $port is already in use, trying $port+1 for $service...${NC}"
    port=$((port+1))
  done
  echo $port
}

# Get available ports
MOODLE_PORT=$(check_port $MOODLE_PORT "Moodle API")
BACKEND_PORT=$(check_port $BACKEND_PORT "Backend")
FRONTEND_PORT=$(check_port $FRONTEND_PORT "Frontend")

# Update the config file with the correct ports
CONFIG_FILE="$(dirname "$0")/campus-underground-frontend/src/config/api.ts"
echo -e "${YELLOW}Updating API configuration with ports: Backend=$BACKEND_PORT, Moodle=$MOODLE_PORT${NC}"
cat > "$CONFIG_FILE" << EOF
export const NODE_API = process.env.REACT_APP_NODE_API_URL || 'http://localhost:$BACKEND_PORT';
export const PYTHON_API = process.env.REACT_APP_PYTHON_API_URL || 'http://localhost:$MOODLE_PORT'; 
EOF

# Update the Moodle API port
MOODLE_APP_FILE="$(dirname "$0")/moodle-api-client/web_app.py"
sed -i.bak "s/app.run(debug=True, port=[0-9]\+)/app.run(debug=True, port=$MOODLE_PORT)/" "$MOODLE_APP_FILE"
rm -f "${MOODLE_APP_FILE}.bak"

# Start the Moodle API client (Python Flask app)
echo -e "${GREEN}Starting Moodle API client on port $MOODLE_PORT...${NC}"
cd "$(dirname "$0")/moodle-api-client"
source venv/bin/activate 2>/dev/null || echo -e "${YELLOW}No virtual environment found, using system Python${NC}"
python web_app.py &
MOODLE_PID=$!
echo -e "${GREEN}Started Moodle API client (PID: $MOODLE_PID)${NC}"

# Start the Node.js backend
echo -e "${GREEN}Starting Node.js backend on port $BACKEND_PORT...${NC}"
cd "$(dirname "$0")/campus-underground-backend"
PORT=$BACKEND_PORT npm run dev &
BACKEND_PID=$!
echo -e "${GREEN}Started Node.js backend (PID: $BACKEND_PID)${NC}"

# Start the React frontend
echo -e "${GREEN}Starting React frontend on port $FRONTEND_PORT...${NC}"
cd "$(dirname "$0")/campus-underground-frontend"
PORT=$FRONTEND_PORT npm start &
FRONTEND_PID=$!
echo -e "${GREEN}Started React frontend (PID: $FRONTEND_PID)${NC}"

echo -e "\n${GREEN}All servers are running!${NC}"
echo -e "${GREEN}- Moodle API client: http://localhost:$MOODLE_PORT${NC}"
echo -e "${GREEN}- Node.js backend: http://localhost:$BACKEND_PORT${NC}"
echo -e "${GREEN}- React frontend: http://localhost:$FRONTEND_PORT${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Function to kill all processes when script is terminated
function cleanup {
  echo -e "\n${YELLOW}Stopping all servers...${NC}"
  kill $MOODLE_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null
  echo -e "${GREEN}All servers stopped.${NC}"
  exit 0
}

# Register the cleanup function to run when script receives SIGINT
trap cleanup SIGINT

# Keep the script running
wait
