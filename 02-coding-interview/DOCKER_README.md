# 🐳 Docker Containerization Guide

## Overview

This guide covers the complete Docker setup for the Online Coding Interview Platform, with both frontend (React) and backend (FastAPI) in a single container for simplified deployment.

## 🚀 Quick Start

### One-Command Launch

```bash
# Production mode (optimized build)
./docker-run.sh prod

# Development mode (with hot reload)
./docker-run.sh dev

# Access at: http://localhost:8000
```

## 📦 What's Included

### Files Created

| File | Purpose |
|------|---------|
| `Dockerfile` | Production multi-stage build |
| `Dockerfile.dev` | Development image with tools |
| `docker-compose.yml` | Production orchestration |
| `docker-compose.dev.yml` | Development orchestration |
| `.dockerignore` | Exclude unnecessary files |
| `start-docker.sh` | Container startup script |
| `docker-run.sh` | Helper script for Docker commands |

## 🏗️ Architecture

### Production Build (Multi-Stage)

```dockerfile
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
# Build optimized React app

# Stage 2: Python backend + serve frontend
FROM python:3.11-slim
# Install dependencies, copy built frontend
# Serve both through FastAPI
```

### How It Works

1. **Frontend Build**: React app is built in the first stage
2. **Backend Setup**: Python environment with FastAPI
3. **Static Serving**: FastAPI serves the built React files
4. **Single Port**: Everything on port 8000 (simplified deployment)

## 📊 Container Configurations

### Production Container

- **Image Size**: ~500MB
- **Exposed Port**: 8000
- **Features**:
  - Optimized React build
  - FastAPI with 4 workers
  - Static file serving
  - Health checks
  - Non-root user

### Development Container

- **Image Size**: ~1.2GB
- **Exposed Ports**: 8000 (backend), 3000 (frontend)
- **Features**:
  - Hot reloading
  - Volume mounts
  - Development tools
  - Debugging support

## 🔧 Docker Commands

### Using the Helper Script

```bash
# Build images
./docker-run.sh build

# Start production
./docker-run.sh prod

# Start development
./docker-run.sh dev

# View logs
./docker-run.sh logs

# Stop services
./docker-run.sh stop

# Open shell
./docker-run.sh shell

# Run tests
./docker-run.sh test

# Clean everything
./docker-run.sh clean
```

### Manual Docker Commands

```bash
# Build production image
docker build -t coding-interview-platform:latest .

# Build development image
docker build -f Dockerfile.dev -t coding-interview-platform:dev .

# Run production with docker-compose
docker-compose up -d

# Run development with docker-compose
docker-compose -f docker-compose.dev.yml up

# View running containers
docker ps

# View logs
docker logs coding-platform -f

# Execute command in container
docker exec -it coding-platform bash

# Stop and remove containers
docker-compose down
```

## 🔍 Environment Variables

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | production | Environment mode |
| `PORT` | 8000 | Backend port |
| `SERVE_FRONTEND` | true | Serve React from FastAPI |
| `FRONTEND_BUILD_PATH` | /app/frontend-dist | Built frontend location |
| `ENABLE_SERVER_EXECUTION` | false | Server-side code execution |
| `CORS_ORIGINS` | http://localhost:8000 | Allowed origins |
| `DEBUG` | false | Debug mode |
| `WORKERS` | 4 | Uvicorn workers |

### Configuration in docker-compose.yml

```yaml
environment:
  - NODE_ENV=production
  - SERVE_FRONTEND=true
  - ENABLE_SERVER_EXECUTION=false
  - SECRET_KEY=${SECRET_KEY:-change-me}
```

## 🚀 Deployment Scenarios

### Local Development

```bash
# Start with hot reload and mounted volumes
./docker-run.sh dev

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Local Production Test

```bash
# Build and run production image
./docker-run.sh prod

# Access at: http://localhost:8000
```

### Cloud Deployment

```bash
# Build image
docker build -t coding-interview-platform:latest .

# Tag for registry
docker tag coding-interview-platform:latest your-registry/coding-platform:v1.0.0

# Push to registry
docker push your-registry/coding-platform:v1.0.0

# Deploy (example with docker run)
docker run -d \
  -p 80:8000 \
  -e NODE_ENV=production \
  -e SECRET_KEY=your-secret-key \
  --name coding-platform \
  your-registry/coding-platform:v1.0.0
```

## 📈 Performance Optimization

### Image Size Optimization

1. **Multi-stage build** - Separate build and runtime
2. **Alpine/slim base** - Minimal OS footprint
3. **.dockerignore** - Exclude unnecessary files
4. **Layer caching** - Optimize build order

### Runtime Optimization

1. **Multiple workers** - Uvicorn with 4 workers
2. **Static file serving** - Nginx-like performance
3. **Health checks** - Auto-restart unhealthy containers
4. **Resource limits** - Set in docker-compose

```yaml
resources:
  limits:
    cpus: '2'
    memory: 2G
  reservations:
    cpus: '1'
    memory: 1G
```

## 🔒 Security Considerations

### Built-in Security

1. **Non-root user** - Container runs as `appuser`
2. **Read-only volumes** - Source code mounted read-only
3. **No server execution** - Code runs in browser only
4. **Environment isolation** - Separate dev/prod configs
5. **Secret management** - Use Docker secrets or env files

### Security Best Practices

```bash
# Use secrets file
echo "SECRET_KEY=your-secret-key" > .env
docker-compose --env-file .env up

# Scan for vulnerabilities
docker scan coding-interview-platform:latest

# Run with limited privileges
docker run --security-opt no-new-privileges \
  --cap-drop ALL \
  coding-interview-platform:latest
```

## 🧪 Testing in Docker

### Run Tests

```bash
# Run all tests
./docker-run.sh test

# Run specific test file
docker-compose run --rm coding-platform \
  pytest /app/backend/tests/test_sessions.py -v

# Run with coverage
docker-compose run --rm coding-platform \
  pytest --cov=app /app/backend/tests
```

### Interactive Testing

```bash
# Open Python shell
docker-compose run --rm coding-platform \
  python -c "from app.main import app; import code; code.interact(local=locals())"

# Run linting
docker-compose run --rm coding-platform \
  flake8 /app/backend/app
```

## 📊 Container Health Monitoring

### Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Monitor Health

```bash
# Check health status
docker inspect coding-platform --format='{{.State.Health.Status}}'

# View health logs
docker inspect coding-platform --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t coding-platform:${{ github.sha }} .
      
      - name: Run tests
        run: docker run coding-platform:${{ github.sha }} pytest
      
      - name: Push to registry
        run: |
          docker tag coding-platform:${{ github.sha }} ${{ secrets.REGISTRY }}/coding-platform:latest
          docker push ${{ secrets.REGISTRY }}/coding-platform:latest
```

## 🐛 Troubleshooting

### Common Issues

#### Container won't start
```bash
# Check logs
docker logs coding-platform

# Verify port availability
lsof -i :8000
```

#### Frontend not loading
```bash
# Verify frontend was built
docker exec coding-platform ls -la /app/frontend-dist

# Check environment variable
docker exec coding-platform env | grep SERVE_FRONTEND
```

#### WebSocket connection fails
```bash
# Check CORS settings
docker exec coding-platform env | grep CORS

# Verify WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost:8000/ws/sessions/test
```

## 📚 Advanced Usage

### Custom Nginx Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://coding-platform:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coding-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: coding-platform
  template:
    metadata:
      labels:
        app: coding-platform
    spec:
      containers:
      - name: app
        image: your-registry/coding-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: NODE_ENV
          value: "production"
```

## 🎯 Production Checklist

- [ ] Change `SECRET_KEY` from default
- [ ] Update `CORS_ORIGINS` for your domain
- [ ] Set `DEBUG=false`
- [ ] Configure proper logging
- [ ] Set up monitoring/alerting
- [ ] Configure backup strategy
- [ ] Set resource limits
- [ ] Enable HTTPS/TLS
- [ ] Set up health checks
- [ ] Configure auto-scaling

## 📄 License

MIT - See LICENSE file for details
