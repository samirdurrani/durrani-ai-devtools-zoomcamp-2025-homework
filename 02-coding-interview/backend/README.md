# 🚀 Online Coding Interview Platform - Backend

A production-ready FastAPI backend for a real-time collaborative coding interview platform. Features WebSocket support for live collaboration, multi-language code execution, and comprehensive session management.

## 📚 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [WebSocket Protocol](#-websocket-protocol)
- [Testing](#-testing)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Deployment](#-deployment)

## ✨ Features

- **🔗 Session Management**: Create unique interview sessions with shareable links
- **🔄 Real-time Collaboration**: WebSocket-based live code synchronization
- **💻 Multi-language Support**: JavaScript, Python, Java, C++, and more
- **▶️ Safe Code Execution**: Sandboxed execution with timeout and resource limits
- **🛡️ Rate Limiting**: Protect against abuse with configurable limits
- **📊 Execution History**: Track all code executions in a session
- **👥 Participant Management**: Track who's in each session
- **🧪 Comprehensive Testing**: Unit and integration tests included
- **📖 Auto-generated Docs**: Interactive API documentation with Swagger UI

## 🏗️ Architecture

The backend follows a clean, layered architecture:

```
┌─────────────────┐
│   FastAPI App   │  ← Main application & middleware
├─────────────────┤
│   API Routes    │  ← HTTP & WebSocket endpoints
├─────────────────┤
│    Services     │  ← Business logic layer
├─────────────────┤
│     Models      │  ← Domain entities & schemas
├─────────────────┤
│   Data Store    │  ← In-memory (upgradeable to DB)
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the backend directory:**
```bash
cd backend
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the server:**
```bash
python -m app.main
```

The server will start at http://localhost:8000

### Quick Test

Test the API is working:
```bash
curl http://localhost:8000/api/v1/health
```

Create a session:
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"host_name": "John Interviewer"}'
```

## 📖 API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/sessions` | Create new interview session |
| `GET` | `/api/v1/sessions/{id}` | Get session details |
| `GET` | `/api/v1/sessions` | List all sessions |
| `DELETE` | `/api/v1/sessions/{id}` | End a session |

#### Language Support

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/languages` | List supported languages |
| `GET` | `/api/v1/languages/{id}/template` | Get language template |

#### Code Execution

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/sessions/{id}/execute` | Execute code safely |

### Example API Calls

**Create a Session:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/sessions",
    json={
        "host_name": "Jane Interviewer",
        "session_name": "Frontend Interview",
        "initial_language": "javascript",
        "max_participants": 5
    }
)
session = response.json()
print(f"Share this URL: {session['join_url']}")
```

**Execute Code:**
```python
response = requests.post(
    f"http://localhost:8000/api/v1/sessions/{session_id}/execute",
    json={
        "code": "print('Hello, World!')",
        "language": "python",
        "time_limit": 5000
    }
)
result = response.json()
print(f"Output: {result['stdout']}")
```

## 🔌 WebSocket Protocol

### Connection

Connect to: `ws://localhost:8000/ws/sessions/{session_id}`

### Message Format

All messages use this structure:
```json
{
    "type": "message_type",
    "data": { ... },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Client → Server Messages

**Join Session:**
```json
{
    "type": "join_session",
    "data": {
        "session_id": "abc123",
        "client_id": "user-001",
        "display_name": "John Developer"
    }
}
```

**Update Code:**
```json
{
    "type": "code_update",
    "data": {
        "session_id": "abc123",
        "client_id": "user-001",
        "code": "console.log('Hello');",
        "language": "javascript"
    }
}
```

### Server → Client Messages

**Session State (on join):**
```json
{
    "type": "session_state",
    "data": {
        "code": "current code here",
        "language": "javascript",
        "participant_count": 2,
        "participants": [...]
    }
}
```

**Code Update Broadcast:**
```json
{
    "type": "code_update",
    "data": {
        "client_id": "user-002",
        "display_name": "Jane",
        "code": "updated code",
        "language": "javascript"
    }
}
```

### WebSocket Client Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sessions/abc123');

ws.onopen = () => {
    // Join the session
    ws.send(JSON.stringify({
        type: 'join_session',
        data: {
            session_id: 'abc123',
            client_id: 'user-001',
            display_name: 'John'
        }
    }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
    
    switch(message.type) {
        case 'session_state':
            // Initial state sync
            updateEditor(message.data.code);
            break;
        case 'code_update':
            // Someone else updated code
            updateEditor(message.data.code);
            break;
    }
};
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Only unit tests (fast)
pytest -m unit

# Only integration tests
pytest -m integration

# With coverage report
pytest --cov=app --cov-report=html
```

### Test Structure

- `tests/test_health.py` - Basic API health checks
- `tests/test_sessions.py` - Session management tests
- `tests/test_languages.py` - Language endpoint tests
- `tests/test_execution.py` - Code execution tests

## ⚙️ Configuration

Configuration is managed through environment variables or the `.env` file.

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Application
APP_NAME="Coding Interview Platform"
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000

# CORS (frontend URLs)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Session Settings
SESSION_ID_LENGTH=12
MAX_SESSION_AGE_HOURS=24
MAX_PARTICIPANTS_PER_SESSION=10

# Code Execution
CODE_EXECUTION_TIMEOUT=5
CODE_MAX_OUTPUT_SIZE=10000
ENABLE_SERVER_EXECUTION=true

# Rate Limiting
RATE_LIMIT_EXECUTIONS_PER_MINUTE=10

# Frontend URL (for generating share links)
FRONTEND_URL=http://localhost:3000
```

### Configuration Classes

All settings are defined in `app/core/config.py` with defaults and validation.

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   └── routes/            # API endpoints
│   │       ├── health.py      # Health checks
│   │       ├── sessions.py    # Session management
│   │       ├── languages.py   # Language support
│   │       ├── execution.py   # Code execution
│   │       └── websocket.py   # WebSocket endpoint
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   └── exceptions.py     # Custom exceptions
│   ├── models/
│   │   └── domain.py         # Domain models
│   ├── schemas/
│   │   ├── session.py        # Request/response schemas
│   │   ├── execution.py      # Execution schemas
│   │   └── websocket.py      # WebSocket messages
│   ├── services/
│   │   ├── session_manager.py    # Session logic
│   │   ├── connection_manager.py # WebSocket connections
│   │   └── code_executor.py      # Code execution
│   └── data/
│       └── languages.json     # Language configuration
├── tests/
│   ├── conftest.py           # Test fixtures
│   └── test_*.py             # Test files
├── requirements.txt           # Dependencies
├── pytest.ini                # Test configuration
└── README.md                 # This file
```

## 🔒 Security

### Current Security Features

- **Rate Limiting**: Prevents execution abuse
- **Input Validation**: All inputs validated with Pydantic
- **Timeout Protection**: Code execution time limits
- **Resource Limits**: Memory and CPU limits for execution (Unix only)
- **CORS Protection**: Only configured origins can access API
- **No Network Access**: Executed code cannot access network

### Security Best Practices

1. **For Production:**
   - Use HTTPS with valid certificates
   - Implement proper authentication (JWT tokens)
   - Use Docker containers for code execution
   - Add request signing for sensitive operations
   - Implement audit logging
   - Use a real database with encryption

2. **Code Execution:**
   - Current implementation uses subprocess (development only)
   - For production, use Docker containers or services like Judge0
   - Never trust user input - always validate and sanitize
   - Set strict resource limits

## 🚢 Deployment

### Development

```bash
# With auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

1. **Using Gunicorn:**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Using Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. **Environment Variables:**
```bash
export ENABLE_SERVER_EXECUTION=false  # Disable in production
export DEBUG=false
export CORS_ORIGINS='["https://yourdomain.com"]'
```

### Database Migration

To migrate from in-memory to a real database:

1. Install database driver (e.g., `pip install asyncpg`)
2. Update `SessionManager` in `services/session_manager.py`
3. Add database models with SQLAlchemy/Tortoise ORM
4. Update configuration with database URL

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Metrics to Track

- Active sessions count
- WebSocket connections
- Code executions per minute
- Average execution time
- Error rates

### Logging

Logs are configured in `app/main.py`. For production, consider:
- Structured logging with JSON
- Log aggregation (ELK stack)
- Error tracking (Sentry)

## 🤝 API Client Examples

### Python Client

```python
import requests
import websocket

class CodingInterviewClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def create_session(self, host_name):
        response = requests.post(
            f"{self.base_url}/api/v1/sessions",
            json={"host_name": host_name}
        )
        return response.json()
    
    def execute_code(self, session_id, code, language):
        response = requests.post(
            f"{self.base_url}/api/v1/sessions/{session_id}/execute",
            json={"code": code, "language": language}
        )
        return response.json()
```

### JavaScript/React Integration

```javascript
// API Service
class APIService {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    async createSession(hostName) {
        const response = await fetch(`${this.baseURL}/api/v1/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ host_name: hostName })
        });
        return response.json();
    }
}

// WebSocket Service
class WebSocketService {
    connect(sessionId) {
        this.ws = new WebSocket(`ws://localhost:8000/ws/sessions/${sessionId}`);
        // ... handle events
    }
}
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in .env or command line
uvicorn app.main:app --port 8001
```

**CORS errors:**
- Check `CORS_ORIGINS` in configuration
- Ensure frontend URL is included

**WebSocket connection fails:**
- Check firewall/proxy settings
- Verify WebSocket URL format
- Check browser console for errors

**Code execution fails:**
- Check if language is installed (for server execution)
- Verify `ENABLE_SERVER_EXECUTION` is true
- Check file permissions

## 📚 Learning Resources

This codebase demonstrates:
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation using Python types
- **WebSockets**: Real-time bidirectional communication
- **Clean Architecture**: Separation of concerns
- **Async/Await**: Asynchronous programming in Python
- **Testing**: Pytest with fixtures and marks
- **Type Hints**: Python type annotations

## 🎯 Next Steps

1. **Add Authentication**: Implement JWT tokens for secure access
2. **Database Integration**: Replace in-memory storage with PostgreSQL
3. **Docker Support**: Containerize the application
4. **Message Queue**: Add Redis for pub/sub and caching
5. **Monitoring**: Add Prometheus metrics and Grafana dashboards
6. **CI/CD**: Set up GitHub Actions or GitLab CI

## 📄 License

MIT License - Feel free to use this for learning or commercial purposes.

---

**Built with ❤️ using FastAPI, designed for beginners to understand and experts to extend!**
