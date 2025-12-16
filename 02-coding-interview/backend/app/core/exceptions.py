"""
Custom Exception Classes

These exceptions help us handle errors in a consistent way across the application.
FastAPI will automatically convert these to appropriate HTTP responses.
"""

from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """
    Base exception class for all API exceptions.
    
    This provides a consistent structure for error responses.
    """
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class SessionNotFoundException(BaseAPIException):
    """Raised when a session is not found"""
    
    def __init__(self, session_id: str):
        super().__init__(
            status_code=404,
            error_code="SESSION_NOT_FOUND",
            message=f"Session {session_id} does not exist",
            details={"session_id": session_id}
        )


class SessionFullException(BaseAPIException):
    """Raised when a session has reached maximum participants"""
    
    def __init__(self, session_id: str, max_participants: int):
        super().__init__(
            status_code=403,
            error_code="SESSION_FULL",
            message=f"Session {session_id} is full (max {max_participants} participants)",
            details={
                "session_id": session_id,
                "max_participants": max_participants
            }
        )


class LanguageNotSupportedException(BaseAPIException):
    """Raised when requesting an unsupported language"""
    
    def __init__(self, language: str):
        super().__init__(
            status_code=400,
            error_code="LANGUAGE_NOT_SUPPORTED",
            message=f"Language '{language}' is not supported",
            details={"language": language}
        )


class CodeExecutionException(BaseAPIException):
    """Raised when code execution fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            error_code="EXECUTION_FAILED",
            message=message,
            details=details or {}
        )


class RateLimitExceededException(BaseAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: str):
        super().__init__(
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded: {limit} requests per {window}",
            details={"limit": limit, "window": window}
        )


class InvalidWebSocketMessageException(BaseAPIException):
    """Raised when WebSocket message is invalid"""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=400,
            error_code="INVALID_WEBSOCKET_MESSAGE",
            message=message,
            details={}
        )
