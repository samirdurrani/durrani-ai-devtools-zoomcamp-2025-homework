"""
Session Schemas

Pydantic models for validating session-related requests and responses.
These ensure that data coming in and going out of our API is properly structured.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CreateSessionRequest(BaseModel):
    """
    Request model for creating a new session.
    
    All fields are optional - the backend will provide defaults.
    """
    host_name: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Display name of the session host"
    )
    session_name: Optional[str] = Field(
        None, 
        max_length=100, 
        description="Optional name for the session"
    )
    initial_language: str = Field(
        "javascript", 
        description="Starting programming language"
    )
    max_participants: int = Field(
        5, 
        ge=2, 
        le=20, 
        description="Maximum number of participants"
    )
    
    @field_validator('initial_language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Ensure language is lowercase"""
        return v.lower()
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "host_name": "John Interviewer",
                "session_name": "Frontend Developer Interview",
                "initial_language": "javascript",
                "max_participants": 5
            }
        }


class SessionResponse(BaseModel):
    """
    Response model for a created session.
    
    Contains the session ID and join URL for sharing.
    """
    session_id: str = Field(..., description="Unique session identifier")
    join_url: str = Field(..., description="URL to share with participants")
    created_at: datetime = Field(..., description="Session creation timestamp")
    host_name: str = Field(..., description="Name of the session host")
    status: str = Field(..., description="Current session status")
    participant_count: int = Field(..., description="Number of connected participants")
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "session_id": "abc123xyz789",
                "join_url": "http://localhost:3000/session/abc123xyz789",
                "created_at": "2024-01-15T10:30:00Z",
                "host_name": "John Interviewer",
                "status": "active",
                "participant_count": 1
            }
        }


class ParticipantInfo(BaseModel):
    """Information about a session participant"""
    client_id: str
    display_name: str
    role: str
    joined_at: datetime
    is_connected: bool


class ExecutionSummary(BaseModel):
    """Summary of a code execution"""
    timestamp: datetime
    language: str
    stdout: str = Field(..., max_length=500)  # Truncated output
    success: bool
    duration: int = Field(..., description="Execution time in milliseconds")


class SessionDetails(BaseModel):
    """
    Detailed session information.
    
    Includes current code, participants, and execution history.
    """
    session_id: str
    join_url: str
    created_at: datetime
    updated_at: datetime
    host_name: str
    session_name: Optional[str]
    status: str
    participant_count: int
    max_participants: int
    participants: List[ParticipantInfo]
    current_code: str
    current_language: str
    execution_history: List[ExecutionSummary]
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "session_id": "abc123xyz789",
                "join_url": "http://localhost:3000/session/abc123xyz789",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:45:00Z",
                "host_name": "John Interviewer",
                "session_name": "Frontend Interview",
                "status": "active",
                "participant_count": 2,
                "max_participants": 5,
                "participants": [
                    {
                        "client_id": "client-001",
                        "display_name": "John Interviewer",
                        "role": "host",
                        "joined_at": "2024-01-15T10:30:00Z",
                        "is_connected": True
                    }
                ],
                "current_code": "console.log('Hello, World!');",
                "current_language": "javascript",
                "execution_history": []
            }
        }


class SessionListResponse(BaseModel):
    """Response for listing sessions"""
    sessions: List[SessionResponse]
    total: int = Field(..., description="Total number of sessions")


class LanguageInfo(BaseModel):
    """Information about a supported language"""
    id: str
    name: str
    version: str
    file_extension: str
    monaco_language: str
    can_run_in_browser: bool
    default_code: str


class LanguageListResponse(BaseModel):
    """Response for listing supported languages"""
    languages: List[LanguageInfo]
