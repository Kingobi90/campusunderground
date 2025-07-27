#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Campus Underground with Direct Moodle Integration...${NC}"

# Kill any existing Node processes
echo -e "${YELLOW}Stopping any existing Node processes...${NC}"
killall node 2>/dev/null

# Set fixed ports
FRONTEND_PORT=3000

echo -e "${GREEN}Starting React frontend on port $FRONTEND_PORT...${NC}"
cd /Users/obinna.c/Campus\ UnderGround/campus-underground-frontend
npm start
