#!/usr/bin/env python
"""
Simple run script for the backend server.

Usage:
    python run.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from app.main import app, settings
import uvicorn

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Online Coding Interview Platform Backend")
    print("="*60)
    print(f"📚 API Documentation: http://localhost:{settings.port}/docs")
    print(f"🔗 API URL: http://localhost:{settings.port}")
    print(f"🔌 WebSocket: ws://localhost:{settings.port}/ws/sessions/{{session_id}}")
    print("="*60)
    print("\n✅ Ready! The backend is starting...\n")
    print("Press CTRL+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
