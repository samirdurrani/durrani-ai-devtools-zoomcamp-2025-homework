#!/bin/bash

# Docker container startup script
# This script handles both development and production modes

set -e

echo "🚀 Starting Online Coding Interview Platform..."
echo "============================================"
echo "Environment: ${NODE_ENV:-production}"
echo "Backend Port: ${PORT:-8000}"
echo "Frontend Path: ${FRONTEND_BUILD_PATH:-/app/frontend-dist}"
echo "============================================"

# Function to wait for a service
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    echo "⏳ Waiting for $service to be ready..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "✅ $service is ready!"
}

# Check if we're in development or production mode
if [ "${NODE_ENV}" = "development" ]; then
    echo "🔧 Running in DEVELOPMENT mode..."
    
    # In development, run both frontend and backend with hot reload
    cd /app
    exec concurrently \
        -n "Backend,Frontend" \
        -c "yellow,cyan" \
        "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload" \
        "cd interview-platform && npm run dev -- --host 0.0.0.0 --port 3000"
else
    echo "🏭 Running in PRODUCTION mode..."
    
    # In production, backend serves the built frontend
    cd /app/backend
    
    # Run database migrations if needed (placeholder)
    # python -m app.db.migrate
    
    # Start the backend server
    exec python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --workers ${WORKERS:-4} \
        --log-level ${LOG_LEVEL:-info} \
        --access-log
fi
