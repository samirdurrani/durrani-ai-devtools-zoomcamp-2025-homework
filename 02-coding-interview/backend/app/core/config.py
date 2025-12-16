"""
Application Configuration

This module handles all configuration settings for the application.
It uses Pydantic Settings to validate and manage environment variables.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or defaults.
    
    To override any setting, create a .env file in the project root
    or set environment variables before running the app.
    """
    
    # Application Info
    app_name: str = "Online Coding Interview Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True  # Auto-reload on code changes (development only)
    
    # CORS Settings - Which frontend URLs can connect to this backend
    cors_origins: List[str] = [
        "http://localhost:3000",  # React dev server (Create React App)
        "http://localhost:5173",  # React dev server (Vite)
        "http://localhost:8080",  # Alternative ports
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Session Configuration
    session_id_length: int = 12  # Length of generated session IDs
    max_session_age_hours: int = 24  # How long to keep sessions in memory
    max_participants_per_session: int = 10  # Maximum users in one session
    
    # WebSocket Configuration
    ws_heartbeat_interval: int = 30  # Seconds between heartbeat pings
    ws_message_size_limit: int = 65536  # Max message size in bytes (64KB)
    
    # Code Execution Configuration
    code_execution_timeout: int = 5  # Seconds before killing execution
    code_max_output_size: int = 10000  # Maximum characters in output
    enable_server_execution: bool = False  # Disabled by default for security - browser execution only
    
    # Security
    max_code_size: int = 50000  # Maximum code size in characters
    rate_limit_executions_per_minute: int = 10  # Per session
    
    # Frontend URL (for generating share links)
    frontend_url: str = "http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"  # Load settings from .env file if it exists
        case_sensitive = False  # Allow lowercase environment variables
        
        # You can override settings with environment variables
        # For example: export MAX_PARTICIPANTS_PER_SESSION=20


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    This function uses @lru_cache to ensure we only create one
    Settings instance and reuse it throughout the application.
    
    Returns:
        Settings: Application configuration
    """
    return Settings()


# Create a global settings instance for easy import
settings = get_settings()
