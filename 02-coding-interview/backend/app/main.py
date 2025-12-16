"""
Main FastAPI Application

This is the entry point for the FastAPI backend server.
It sets up the application, middleware, routes, and error handlers.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import BaseAPIException

# Import routers
from app.api.routes import health, sessions, languages, execution, websocket


# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title="Online Coding Interview Platform API",
    description="""
## 🎯 Overview

Backend API for a real-time collaborative coding interview platform.

## ✨ Features

- **Session Management**: Create and manage interview sessions
- **Real-time Collaboration**: WebSocket-based live code sharing
- **Multi-language Support**: JavaScript, Python, Java, C++ and more
- **Safe Code Execution**: Sandboxed execution with timeout protection
- **Rate Limiting**: Prevent abuse of execution endpoints

## 🔌 WebSocket Endpoint

Connect to `/ws/sessions/{session_id}` for real-time collaboration.

## 📚 Documentation

- **OpenAPI Schema**: Available at `/openapi.json`
- **Interactive Docs**: This page (Swagger UI)
- **Alternative Docs**: Available at `/redoc`
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS middleware
# This allows the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Which URLs can access this API
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Exception handlers
@app.exception_handler(BaseAPIException)
async def handle_api_exception(request: Request, exc: BaseAPIException):
    """
    Handle custom API exceptions.
    
    Converts our custom exceptions to proper HTTP responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    
    Provides clean error messages when request data is invalid.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"][1:]),  # Skip 'body'
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": {"errors": errors},
            "timestamp": datetime.now().isoformat()
        }
    )


# Include routers
# Each router handles a specific group of endpoints
app.include_router(health.router)  # Health check endpoints
app.include_router(sessions.router)  # Session management
app.include_router(languages.router)  # Language information
app.include_router(execution.router)  # Code execution
app.include_router(websocket.router)  # WebSocket for real-time


# Serve frontend static files if configured
# This is used when running in a container with the built frontend
serve_frontend = os.getenv("SERVE_FRONTEND", "false").lower() == "true"
frontend_build_path = os.getenv("FRONTEND_BUILD_PATH", "/app/frontend-dist")

if serve_frontend and os.path.exists(frontend_build_path):
    logger.info(f"Serving frontend static files from {frontend_build_path}")
    
    # Mount static files for assets
    app.mount("/assets", StaticFiles(directory=f"{frontend_build_path}/assets"), name="assets")
    
    # Serve index.html for the root and all non-API routes (for React Router)
    @app.get("/{path:path}")
    async def serve_frontend_app(path: str):
        """
        Serve the React frontend application.
        Returns index.html for all non-API routes to support client-side routing.
        """
        # Skip API routes and WebSocket
        if path.startswith("api/") or path.startswith("ws/") or path.startswith("docs") or path.startswith("redoc") or path.startswith("openapi"):
            return {"error": "Not found"}
        
        index_path = Path(frontend_build_path) / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            return {"error": "Frontend not found"}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - provides basic API information.
    
    Returns:
        API information and useful links
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Online Coding Interview Platform API",
        "documentation": {
            "interactive": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "sessions": "/api/v1/sessions",
            "languages": "/api/v1/languages",
            "websocket": "/ws/sessions/{session_id}"
        },
        "timestamp": datetime.now().isoformat()
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    
    Initialize services, load configuration, etc.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Server execution enabled: {settings.enable_server_execution}")
    
    # In production, you would:
    # - Connect to database
    # - Initialize background tasks
    # - Load ML models
    # - Set up monitoring


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    
    Clean up resources, close connections, etc.
    """
    logger.info("Shutting down application")
    
    # In production, you would:
    # - Close database connections
    # - Stop background tasks
    # - Save state if needed


# Main entry point for running with Python
if __name__ == "__main__":
    import uvicorn
    
    # Print startup information
    print("\n" + "="*50)
    print("🚀 Online Coding Interview Platform Backend")
    print("="*50)
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔗 API Base URL: http://{settings.host}:{settings.port}")
    print(f"🔌 WebSocket Endpoint: ws://{settings.host}:{settings.port}/ws/sessions/{{session_id}}")
    print("="*50)
    print("\nStarting server...")
    print("Press CTRL+C to stop\n")
    
    # Run the server
    uvicorn.run(
        "app.main:app",  # Module path to the app
        host=settings.host,
        port=settings.port,
        reload=settings.reload,  # Auto-reload on code changes
        log_level=settings.log_level.lower()
    )
