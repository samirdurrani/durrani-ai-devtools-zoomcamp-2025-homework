# 🚀 Online Coding Interview Platform - Full Stack

## 📋 Overview

This is a complete online coding interview platform with:
- **Frontend**: React + Vite + Monaco Editor
- **Backend**: FastAPI + WebSockets
- **Real-time collaboration**: Multiple users can code together
- **Code execution**: Run code safely in multiple languages

## 🎯 Quick Start (One Command!)

```bash
# Run both frontend and backend together
npm run dev
```

That's it! The platform will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📦 Initial Setup (First Time Only)

### Prerequisites
- **Node.js** 18+ 
- **Python** 3.8+
- **pip** (Python package manager)
- **npm** (comes with Node.js)

### Installation Steps

```bash
# 1. Clone the repository (if you haven't already)
git clone <your-repo-url>
cd 02-coding-interview

# 2. Install concurrently (for running both services)
npm install

# 3. Install frontend dependencies
cd interview-platform
npm install
cd ..

# 4. Install backend dependencies  
cd backend
pip install -r requirements.txt
cd ..

# 5. (Optional) Install test dependencies
cd backend
pip install -r tests/requirements-test.txt
cd ..
```

### Alternative: Use the Setup Script

```bash
# This will check and install everything
./start.sh
```

## 🎮 Available Commands

All commands should be run from the `02-coding-interview` directory:

### Development Commands

```bash
# Run both frontend and backend (recommended)
npm run dev

# Run only the backend
npm run backend:dev

# Run only the frontend  
npm run frontend:dev

# Build frontend for production
npm run frontend:build
```

### Testing Commands

```bash
# Run basic tests (no server needed)
npm test

# Run backend unit tests only
npm run test:backend

# Run all backend tests (starts server automatically)
npm run test:backend:all

# Run frontend tests
npm run test:frontend

# Run integration tests (WebSocket tests)
npm run test:integration

# Run end-to-end tests
npm run test:e2e
```

### Utility Commands

```bash
# Clean up cache and build files
npm run clean

# Format code (if black is installed)
npm run format

# Install all dependencies
npm run install
```

## 🏗️ Project Structure

```
02-coding-interview/
├── package.json          # Root orchestrator (concurrently)
├── start.sh             # Quick start script
├── 
├── backend/             # FastAPI backend
│   ├── app/
│   │   ├── main.py     # FastAPI app entry
│   │   ├── api/        # API routes
│   │   ├── models/     # Domain models
│   │   ├── schemas/    # Pydantic models
│   │   ├── services/   # Business logic
│   │   └── core/       # Config & exceptions
│   ├── tests/          # Backend tests
│   └── requirements.txt
│
├── interview-platform/  # React frontend
│   ├── src/
│   │   ├── pages/      # React pages
│   │   ├── components/ # React components
│   │   ├── services/   # API & WebSocket clients
│   │   └── hooks/      # Custom React hooks
│   ├── package.json
│   └── vite.config.js
│
└── openapi.yaml        # API specification
```

## 🔧 How Concurrently Works

The `package.json` at the root uses `concurrently` to run both services:

```json
{
  "scripts": {
    "dev": "concurrently -n \"Backend,Frontend\" -c \"yellow,cyan\" \"npm run backend:dev\" \"npm run frontend:dev\""
  }
}
```

This runs both services in parallel with colored output:
- **Yellow** output = Backend (FastAPI)
- **Cyan** output = Frontend (React)

## 🧪 Testing Guide

### Quick Test (No Server Needed)
```bash
npm test
```

### Full Test Suite
```bash
# Terminal 1: Start the server
npm run backend:dev

# Terminal 2: Run all tests
cd backend && pytest
```

### Test Categories

| Test Type | Command | Server Needed? |
|-----------|---------|---------------|
| Unit Tests | `pytest -m unit` | No |
| Integration | `pytest -m integration` | Yes |
| E2E | `pytest -m e2e` | Yes |
| All | `pytest` | Yes |

## 🎯 Usage Flow

1. **Start the platform**: `npm run dev`
2. **Create a session**: Click "Start New Interview" on the frontend
3. **Share the link**: Copy the unique URL and share it
4. **Collaborate**: Multiple users can join and code together
5. **Execute code**: Click "Run" to execute the code
6. **See results**: Output appears for all participants

## 🐛 Troubleshooting

### Port Already in Use

If you see "Address already in use":

```bash
# Find what's using port 8000 (backend)
lsof -i :8000

# Find what's using port 5173 (frontend)
lsof -i :5173

# Kill the process
kill -9 <PID>
```

### WebSocket Connection Failed

1. Make sure both services are running: `npm run dev`
2. Check the browser console for errors
3. Verify the backend is accessible: http://localhost:8000/docs

### Tests Failing

1. For unit tests: Should work without server
2. For integration/e2e tests: Make sure server is running first
3. Use `npm run test:backend:all` to auto-start server

### Dependencies Installation Issues

If pip uses a private repository:
```bash
pip install --index-url https://pypi.org/simple -r requirements.txt
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 🔄 WebSocket Events

The platform uses WebSockets for real-time collaboration:

### Client → Server Messages
- `join_session`: Join a coding session
- `leave_session`: Leave the session
- `code_update`: Send code changes
- `language_change`: Change programming language
- `execute_code`: Request code execution

### Server → Client Messages
- `session_state`: Full session state
- `user_joined`: Someone joined
- `user_left`: Someone left
- `code_update`: Code was changed
- `language_changed`: Language was changed
- `execution_result`: Code execution completed

## 🚢 Deployment

For production deployment:

1. **Build frontend**:
   ```bash
   npm run frontend:build
   ```

2. **Configure backend**:
   - Set environment variables in `.env`
   - Disable debug mode
   - Configure CORS for your domain

3. **Run with production servers**:
   - Frontend: Nginx or similar
   - Backend: Gunicorn + Uvicorn workers

## 📝 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `npm test`
4. Submit a pull request

---

**Happy Coding! 🎉**

For questions or issues, please check the individual README files in `backend/` and `interview-platform/` directories.

