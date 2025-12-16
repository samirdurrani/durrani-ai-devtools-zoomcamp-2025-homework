# 📚 Online Coding Interview Platform - API Documentation

## 🎯 Overview

This directory contains the complete API specification and backend implementation for the online coding interview platform. The API enables real-time collaborative coding sessions with multi-language support and safe code execution.

## 📁 Files Included

- **`openapi.yaml`** - Complete OpenAPI 3.0 specification
- **`backend-example.py`** - Example FastAPI implementation
- **`requirements.txt`** - Python dependencies
- **`API_README.md`** - This file

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Backend

```bash
# Start the FastAPI server
python backend-example.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test with Frontend

Your React frontend is already configured to connect to this backend:

```bash
# In another terminal, start the React app
cd interview-platform
npm run dev
```

Visit http://localhost:3000 and create a session!

## 📖 Understanding the OpenAPI Specification

### What is OpenAPI?

OpenAPI (formerly Swagger) is a standard way to describe REST APIs. Think of it as a blueprint that describes:
- What endpoints are available
- What data they accept
- What responses they return
- How to authenticate

### Key Sections in `openapi.yaml`

```yaml
# 1. API Information
info:
  title: Your API name
  description: What it does
  version: API version

# 2. Server Configuration
servers:
  - url: Where your API lives

# 3. Endpoints (Paths)
paths:
  /sessions:
    post:  # Create a session
    get:   # List sessions

# 4. Data Models (Schemas)
components:
  schemas:
    SessionResponse:  # What a session looks like
    ExecuteCodeRequest:  # What to send for execution
```

### How to Read the Spec

1. **Start with `paths`**: These are your API endpoints
2. **Check `parameters`**: What you need to send
3. **Look at `responses`**: What you'll get back
4. **Review `schemas`**: The data structures used

## 🔌 API Endpoints Summary

### Session Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/sessions` | Create new interview session |
| GET | `/api/v1/sessions/{sessionId}` | Get session details |
| GET | `/api/v1/sessions` | List all sessions |
| DELETE | `/api/v1/sessions/{sessionId}` | End a session |

### Language Support
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/languages` | List supported languages |
| GET | `/api/v1/languages/{languageId}/template` | Get language template |

### Code Execution
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/sessions/{sessionId}/execute` | Execute code |

### WebSocket
| Endpoint | Purpose |
|----------|---------|
| `ws://localhost:8000/ws/sessions/{sessionId}` | Real-time collaboration |

## 🔄 WebSocket Message Flow

### Client → Server Messages

```javascript
// 1. Join a session
{
  "type": "join_session",
  "data": {
    "sessionId": "abc123",
    "displayName": "John Developer"
  }
}

// 2. Send code update
{
  "type": "code_update",
  "data": {
    "code": "console.log('Hello');",
    "language": "javascript"
  }
}

// 3. Change language
{
  "type": "language_change",
  "data": {
    "language": "python"
  }
}
```

### Server → Client Messages

```javascript
// 1. User joined notification
{
  "type": "user_joined",
  "data": {
    "participantCount": 2,
    "displayName": "Jane Candidate"
  }
}

// 2. Code update from another user
{
  "type": "code_update",
  "data": {
    "code": "def hello():\n    print('Hi')",
    "clientId": "other-user"
  }
}

// 3. Execution result
{
  "type": "execution_result",
  "data": {
    "stdout": "Hello, World!",
    "exitCode": 0
  }
}
```

## 🔐 Security Considerations

### Current Implementation (MVP)
- Sessions use random IDs (hard to guess)
- Basic input validation
- Code execution timeout (5 seconds)

### Production Recommendations
1. **Authentication**: Add JWT tokens for user auth
2. **Rate Limiting**: Prevent abuse of execution endpoint
3. **Sandboxing**: Use Docker for safe code execution
4. **Resource Limits**: CPU, memory, disk limits
5. **Input Sanitization**: Validate all inputs
6. **HTTPS**: Use SSL/TLS in production

## 🏗️ Extending the API

### Adding a New Endpoint

1. **Update OpenAPI spec** (`openapi.yaml`):
```yaml
paths:
  /api/v1/your-endpoint:
    get:
      summary: What it does
      responses:
        '200':
          description: Success
```

2. **Add to FastAPI** (`backend-example.py`):
```python
@app.get("/api/v1/your-endpoint")
async def your_function():
    return {"message": "Hello"}
```

### Adding a New Language

1. **Update LANGUAGES list**:
```python
LANGUAGES.append({
    "id": "rust",
    "name": "Rust",
    "canRunInBrowser": False,
    "defaultCode": "fn main() { println!(\"Hello\"); }"
})
```

2. **Add execution logic** in `execute_code()` function

## 🧪 Testing the API

### Using the Interactive Docs

1. Visit http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using cURL

```bash
# Create a session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"hostName": "John Interviewer"}'

# Get session details
curl http://localhost:8000/api/v1/sessions/abc123

# Execute code
curl -X POST http://localhost:8000/api/v1/sessions/abc123/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello\")",
    "language": "python"
  }'
```

### Using the Frontend

The React frontend automatically uses all these endpoints:
1. Create session → `POST /sessions`
2. Join session → `GET /sessions/{id}` + WebSocket
3. Run code → `POST /sessions/{id}/execute`

## 🌟 Best Practices

### API Design
✅ **DO**:
- Use consistent naming (camelCase for JSON)
- Return appropriate HTTP status codes
- Include timestamps in responses
- Validate all inputs

❌ **DON'T**:
- Expose internal errors to clients
- Allow unlimited resource usage
- Trust client input without validation

### WebSocket Communication
✅ **DO**:
- Send acknowledgments for important messages
- Include timestamps
- Handle reconnection gracefully
- Clean up on disconnect

❌ **DON'T**:
- Send sensitive data over WebSocket
- Broadcast unnecessary updates
- Keep dead connections

## 📈 Monitoring & Debugging

### Check API Health
```bash
curl http://localhost:8000/api/v1/health
```

### View Logs
The FastAPI server logs all requests:
```
INFO:     127.0.0.1:55341 - "POST /api/v1/sessions HTTP/1.1" 201
INFO:     WebSocket connection accepted for session abc123
INFO:     127.0.0.1:55342 - "POST /api/v1/sessions/abc123/execute HTTP/1.1" 200
```

### Debug WebSocket
Use browser DevTools:
1. Open Network tab
2. Filter by "WS"
3. Click on WebSocket connection
4. View messages in real-time

## 🚀 Deployment Checklist

- [ ] Set up environment variables
- [ ] Configure CORS for production domain
- [ ] Set up Redis for session storage
- [ ] Implement proper code sandboxing
- [ ] Add authentication/authorization
- [ ] Set up monitoring (e.g., Prometheus)
- [ ] Configure rate limiting
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Use HTTPS with valid certificates
- [ ] Set up database for persistence

## 💡 Tips for Beginners

1. **Start Simple**: Get basic endpoints working first
2. **Use the Docs**: http://localhost:8000/docs is your friend
3. **Test Incrementally**: Test each endpoint as you build
4. **Check Errors**: Look at both frontend console and backend logs
5. **Ask Questions**: The spec has detailed descriptions for everything

## 🆘 Common Issues

### CORS Error
**Problem**: "CORS policy blocked request"
**Solution**: Check `allow_origins` in FastAPI middleware

### WebSocket Won't Connect
**Problem**: "WebSocket connection failed"
**Solution**: 
- Check if backend is running
- Verify WebSocket URL
- Check browser console

### Code Execution Fails
**Problem**: "Execution failed"
**Solution**:
- Check if language is supported
- Verify code syntax
- Check timeout settings

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/)

---

**Remember**: This is a learning project! Feel free to experiment, break things, and learn from the process. The API is designed to be beginner-friendly while following professional best practices.
