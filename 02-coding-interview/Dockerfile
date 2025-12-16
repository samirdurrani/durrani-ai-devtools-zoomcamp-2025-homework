# Multi-stage Dockerfile for Online Coding Interview Platform
# Combines both frontend and backend in a single container

# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app/frontend

# Copy frontend package files
COPY interview-platform/package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy frontend source code
COPY interview-platform/ ./

# Build the React app
RUN npm run build

# Stage 2: Python backend with Node.js runtime
FROM python:3.11-slim

# Install Node.js and build dependencies
RUN apt-get update && \
    apt-get install -y \
        curl \
        gcc \
        g++ \
        make \
        python3-dev && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend-dist

# Copy root-level files (package.json for concurrently, startup scripts)
COPY package.json ./
COPY start-docker.sh ./

# Install concurrently globally
RUN npm install -g concurrently

# Make the startup script executable
RUN chmod +x start-docker.sh

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
# Backend API
EXPOSE 8000
# Frontend dev server (if needed for development)
EXPOSE 3000

# Environment variables
ENV NODE_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Disable server-side code execution for security
    ENABLE_SERVER_EXECUTION=false \
    # Configure backend to serve frontend static files
    SERVE_FRONTEND=true \
    FRONTEND_BUILD_PATH=/app/frontend-dist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command - serve both frontend and backend
# The backend will serve the frontend static files
CMD ["sh", "-c", "cd /app/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
