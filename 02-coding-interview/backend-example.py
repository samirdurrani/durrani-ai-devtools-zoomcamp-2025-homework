"""
FastAPI Backend Example for Online Coding Interview Platform
This is a simplified example showing how to implement the OpenAPI spec with FastAPI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import asyncio
import json

# ============================================================================
# PYDANTIC MODELS (matching OpenAPI schemas)
# ============================================================================

class CreateSessionRequest(BaseModel):
    """Request model for creating a new session"""
    hostName: Optional[str] = Field(None, max_length=50, description="Display name of host")
    sessionName: Optional[str] = Field(None, max_length=100, description="Session title")
    initialLanguage: str = Field("javascript", description="Starting language")
    maxParticipants: int = Field(5, ge=2, le=10, description="Max participants")

class SessionResponse(BaseModel):
    """Response model for created session"""
    sessionId: str
    joinUrl: str
    createdAt: datetime
    hostName: Optional[str]
    status: str
    participantCount: int

class Language(BaseModel):
    """Programming language information"""
    id: str
    name: str
    version: str
    canRunInBrowser: bool
    defaultCode: str
    fileExtension: str
    monacoLanguage: str

class ExecuteCodeRequest(BaseModel):
    """Request model for code execution"""
    code: str = Field(..., max_length=50000, description="Code to execute")
    language: str = Field(..., description="Programming language")
    stdin: str = Field("", description="Standard input")
    timeLimit: int = Field(5000, ge=100, le=10000, description="Time limit in ms")

class ExecutionResponse(BaseModel):
    """Response model for code execution"""
    sessionId: str
    language: str
    stdout: str
    stderr: str
    exitCode: int
    duration: int
    success: bool
    error: Optional[str]
    timestamp: datetime

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Online Coding Interview Platform API",
    description="Backend API for real-time collaborative coding interviews",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc"     # ReDoc at http://localhost:8000/redoc
)

# ============================================================================
# CORS CONFIGURATION (allows React frontend to connect)
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React development server
        "http://localhost:5173",      # Vite development server
        "https://yourdomain.com"      # Production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)

# ============================================================================
# IN-MEMORY STORAGE (replace with database in production)
# ============================================================================

# Store active sessions
sessions_db: Dict[str, Dict[str, Any]] = {}

# Store WebSocket connections for each session
session_connections: Dict[str, List[WebSocket]] = {}

# Supported languages
LANGUAGES = [
    {
        "id": "javascript",
        "name": "JavaScript",
        "version": "ES2022",
        "canRunInBrowser": True,
        "defaultCode": "// Welcome to the coding interview platform!\\n// Start writing your JavaScript code here\\n\\nfunction solution() {\\n  console.log(\\"Hello, World!\\");\\n}\\n\\nsolution();",
        "fileExtension": ".js",
        "monacoLanguage": "javascript"
    },
    {
        "id": "python",
        "name": "Python",
        "version": "3.11",
        "canRunInBrowser": False,
        "defaultCode": "# Welcome to the coding interview platform!\\n# Start writing your Python code here\\n\\ndef solution():\\n    print(\\"Hello, World!\\")\\n\\nsolution()",
        "fileExtension": ".py",
        "monacoLanguage": "python"
    },
    {
        "id": "java",
        "name": "Java",
        "version": "17",
        "canRunInBrowser": False,
        "defaultCode": "// Welcome to the coding interview platform!\\n// Start writing your Java code here\\n\\npublic class Main {\\n    public static void main(String[] args) {\\n        System.out.println(\\"Hello, World!\\");\\n    }\\n}",
        "fileExtension": ".java",
        "monacoLanguage": "java"
    },
    {
        "id": "cpp",
        "name": "C++",
        "version": "17",
        "canRunInBrowser": False,
        "defaultCode": "// Welcome to the coding interview platform!\\n// Start writing your C++ code here\\n\\n#include <iostream>\\nusing namespace std;\\n\\nint main() {\\n    cout << \\"Hello, World!\\" << endl;\\n    return 0;\\n}",
        "fileExtension": ".cpp",
        "monacoLanguage": "cpp"
    }
]

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/api/v1/health")
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "websocket": "active",
            "executor": "ready"
        }
    }

@app.post("/api/v1/sessions", status_code=status.HTTP_201_CREATED, response_model=SessionResponse)
async def create_session(request: CreateSessionRequest = None):
    """
    Create a new coding interview session
    
    This endpoint is called when an interviewer clicks "Create New Interview"
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())[:12]  # Use first 12 chars for shorter URLs
    
    # Create session object
    session = {
        "sessionId": session_id,
        "joinUrl": f"http://localhost:3000/session/{session_id}",
        "createdAt": datetime.now(),
        "hostName": request.hostName if request else "Anonymous Host",
        "sessionName": request.sessionName if request else None,
        "status": "active",
        "participantCount": 0,
        "participants": [],
        "currentCode": LANGUAGES[0]["defaultCode"],  # Default to JavaScript
        "currentLanguage": request.initialLanguage if request else "javascript",
        "maxParticipants": request.maxParticipants if request else 5,
        "executionHistory": []
    }
    
    # Store in database
    sessions_db[session_id] = session
    session_connections[session_id] = []
    
    # Return response
    return SessionResponse(
        sessionId=session_id,
        joinUrl=session["joinUrl"],
        createdAt=session["createdAt"],
        hostName=session["hostName"],
        status=session["status"],
        participantCount=session["participantCount"]
    )

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get details of a specific session
    
    Called when a user joins a session to get the current state
    """
    if session_id not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SESSION_NOT_FOUND",
                "message": f"Session {session_id} does not exist",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    return sessions_db[session_id]

@app.get("/api/v1/sessions")
async def list_sessions(status: str = "active", limit: int = 20):
    """
    List all sessions (for admin/debugging)
    
    In production, this would be restricted to authenticated admins
    """
    # Filter sessions by status
    filtered_sessions = []
    for session in sessions_db.values():
        if status == "all" or session["status"] == status:
            filtered_sessions.append({
                "sessionId": session["sessionId"],
                "createdAt": session["createdAt"],
                "hostName": session["hostName"],
                "participantCount": session["participantCount"],
                "status": session["status"]
            })
    
    # Apply limit
    filtered_sessions = filtered_sessions[:limit]
    
    return {
        "sessions": filtered_sessions,
        "total": len(filtered_sessions)
    }

@app.get("/api/v1/languages")
async def list_languages():
    """
    Get list of supported programming languages
    
    Used to populate the language dropdown in the editor
    """
    return {"languages": LANGUAGES}

@app.get("/api/v1/languages/{language_id}/template")
async def get_language_template(language_id: str):
    """Get the default template for a specific language"""
    for lang in LANGUAGES:
        if lang["id"] == language_id:
            return {
                "languageId": language_id,
                "template": lang["defaultCode"]
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "LANGUAGE_NOT_FOUND",
            "message": f"Language {language_id} is not supported",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.post("/api/v1/sessions/{session_id}/execute", response_model=ExecutionResponse)
async def execute_code(session_id: str, request: ExecuteCodeRequest):
    """
    Execute code for a session
    
    NOTE: This is a simplified example. In production, you would:
    1. Use Docker containers for sandboxing
    2. Implement proper resource limits
    3. Use a queue system for execution
    4. Store results in a database
    """
    
    if session_id not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SESSION_NOT_FOUND", "message": "Session not found"}
        )
    
    # Simulate code execution (replace with actual execution logic)
    # In production, you'd use subprocess with timeout, Docker, or a service like Judge0
    
    if request.language == "python":
        # Example Python execution (UNSAFE - for demonstration only!)
        try:
            import subprocess
            import tempfile
            
            # Write code to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(request.code)
                temp_file = f.name
            
            # Execute with timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=request.timeLimit / 1000,  # Convert ms to seconds
                input=request.stdin
            )
            
            return ExecutionResponse(
                sessionId=session_id,
                language=request.language,
                stdout=result.stdout[:5000],  # Limit output size
                stderr=result.stderr[:5000],
                exitCode=result.returncode,
                duration=100,  # Would measure actual duration
                success=result.returncode == 0,
                error=None if result.returncode == 0 else "Runtime error",
                timestamp=datetime.now()
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResponse(
                sessionId=session_id,
                language=request.language,
                stdout="",
                stderr="",
                exitCode=-1,
                duration=request.timeLimit,
                success=False,
                error=f"Execution timed out after {request.timeLimit}ms",
                timestamp=datetime.now()
            )
        except Exception as e:
            return ExecutionResponse(
                sessionId=session_id,
                language=request.language,
                stdout="",
                stderr=str(e),
                exitCode=1,
                duration=0,
                success=False,
                error="Execution failed",
                timestamp=datetime.now()
            )
    
    # For other languages, return a mock response
    return ExecutionResponse(
        sessionId=session_id,
        language=request.language,
        stdout="Hello, World!\\n(This is a mock execution result)",
        stderr="",
        exitCode=0,
        duration=15,
        success=True,
        error=None,
        timestamp=datetime.now()
    )

# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time collaboration
    
    Handles:
    - User joining/leaving
    - Code synchronization
    - Language changes
    - Execution results broadcasting
    """
    
    # Check if session exists
    if session_id not in sessions_db:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "data": {
                "code": "SESSION_NOT_FOUND",
                "message": f"Session {session_id} does not exist"
            },
            "timestamp": datetime.now().isoformat()
        })
        await websocket.close()
        return
    
    # Accept connection
    await websocket.accept()
    
    # Add to session connections
    if session_id not in session_connections:
        session_connections[session_id] = []
    session_connections[session_id].append(websocket)
    
    # Update participant count
    sessions_db[session_id]["participantCount"] = len(session_connections[session_id])
    
    # Send current session state to new user
    await websocket.send_json({
        "type": "session_state",
        "data": {
            "sessionId": session_id,
            "code": sessions_db[session_id]["currentCode"],
            "language": sessions_db[session_id]["currentLanguage"],
            "participantCount": sessions_db[session_id]["participantCount"],
            "participants": sessions_db[session_id]["participants"]
        },
        "timestamp": datetime.now().isoformat()
    })
    
    # Broadcast user joined to all other participants
    for connection in session_connections[session_id]:
        if connection != websocket:
            try:
                await connection.send_json({
                    "type": "user_joined",
                    "data": {
                        "sessionId": session_id,
                        "participantCount": sessions_db[session_id]["participantCount"]
                    },
                    "timestamp": datetime.now().isoformat()
                })
            except:
                pass
    
    try:
        # Handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            message_data = data.get("data", {})
            
            # Handle different message types
            if message_type == "code_update":
                # Update session code
                sessions_db[session_id]["currentCode"] = message_data.get("code", "")
                
                # Broadcast to all other participants
                for connection in session_connections[session_id]:
                    if connection != websocket:
                        try:
                            await connection.send_json({
                                "type": "code_update",
                                "data": message_data,
                                "timestamp": datetime.now().isoformat()
                            })
                        except:
                            pass
            
            elif message_type == "language_change":
                # Update session language
                sessions_db[session_id]["currentLanguage"] = message_data.get("language", "javascript")
                
                # Broadcast to all other participants
                for connection in session_connections[session_id]:
                    if connection != websocket:
                        try:
                            await connection.send_json({
                                "type": "language_change",
                                "data": message_data,
                                "timestamp": datetime.now().isoformat()
                            })
                        except:
                            pass
            
            elif message_type == "execute_code":
                # Execute code and broadcast result
                # (In production, this would call the execution service)
                execution_result = {
                    "stdout": "Hello, World!",
                    "stderr": "",
                    "exitCode": 0,
                    "duration": 15,
                    "success": True
                }
                
                # Broadcast execution result to all participants
                for connection in session_connections[session_id]:
                    try:
                        await connection.send_json({
                            "type": "execution_result",
                            "data": {
                                "sessionId": session_id,
                                "result": execution_result
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                    except:
                        pass
    
    except WebSocketDisconnect:
        # Remove from connections
        session_connections[session_id].remove(websocket)
        sessions_db[session_id]["participantCount"] = len(session_connections[session_id])
        
        # Broadcast user left to remaining participants
        for connection in session_connections[session_id]:
            try:
                await connection.send_json({
                    "type": "user_left",
                    "data": {
                        "sessionId": session_id,
                        "participantCount": sessions_db[session_id]["participantCount"]
                    },
                    "timestamp": datetime.now().isoformat()
                })
            except:
                pass

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Online Coding Interview Platform API")
    print("📚 Documentation available at: http://localhost:8000/docs")
    print("🔗 API running at: http://localhost:8000")
    print("")
    print("To test the API:")
    print("1. Visit http://localhost:8000/docs for interactive documentation")
    print("2. Start your React frontend: cd interview-platform && npm run dev")
    print("3. Create a session and start coding!")
    
    # Run the FastAPI application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes during development
        log_level="info"
    )
