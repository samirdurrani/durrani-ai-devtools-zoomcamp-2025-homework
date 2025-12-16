#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Online Coding Interview Platform${NC}"
echo "================================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check if concurrently is installed
if [ ! -d "node_modules/concurrently" ]; then
    echo -e "${YELLOW}📦 Installing concurrently...${NC}"
    npm install --save-dev concurrently
fi

# Check if frontend dependencies are installed
if [ ! -d "interview-platform/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd interview-platform && npm install && cd ..
fi

echo -e "${GREEN}✅ All dependencies are ready!${NC}"
echo ""
echo "Starting services..."
echo "===================="
echo -e "${YELLOW}Backend:${NC}  http://localhost:8000"
echo -e "${YELLOW}Frontend:${NC} http://localhost:5173"
echo -e "${YELLOW}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop all services"
echo "===================="
echo ""

# Start both services using concurrently
npm run dev
