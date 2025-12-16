"""
Domain Models

These are the core data structures used throughout the application.
They represent the business entities like Sessions, Participants, etc.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SessionStatus(str, Enum):
    """Status of a coding session"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ParticipantRole(str, Enum):
    """Role of a participant in a session"""
    HOST = "host"
    PARTICIPANT = "participant"
    VIEWER = "viewer"


@dataclass
class Participant:
    """
    Represents a user in a coding session.
    
    Each participant has a unique client_id and can have different roles.
    """
    client_id: str
    display_name: str
    role: ParticipantRole
    joined_at: datetime
    connection_id: Optional[str] = None  # WebSocket connection ID
    is_connected: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "client_id": self.client_id,
            "display_name": self.display_name,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "is_connected": self.is_connected
        }


@dataclass
class ExecutionResult:
    """
    Result of code execution.
    
    Contains output, errors, and metadata about the execution.
    """
    session_id: str
    language: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    executed_by: Optional[str] = None  # client_id of executor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "language": self.language,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "duration": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "executed_by": self.executed_by
        }


@dataclass
class Session:
    """
    Represents a coding interview session.
    
    This is the main entity that holds all information about a coding session,
    including participants, code, and execution history.
    """
    session_id: str
    created_at: datetime
    host_name: str
    session_name: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    current_code: str = ""
    current_language: str = "javascript"
    participants: List[Participant] = field(default_factory=list)
    execution_history: List[ExecutionResult] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)
    max_participants: int = 10
    
    @property
    def participant_count(self) -> int:
        """Get count of connected participants"""
        return len([p for p in self.participants if p.is_connected])
    
    @property
    def is_full(self) -> bool:
        """Check if session has reached max participants"""
        return self.participant_count >= self.max_participants
    
    def add_participant(self, participant: Participant) -> None:
        """Add a participant to the session"""
        # Remove existing participant with same client_id if any
        self.participants = [
            p for p in self.participants 
            if p.client_id != participant.client_id
        ]
        self.participants.append(participant)
        self.updated_at = datetime.now()
    
    def remove_participant(self, client_id: str) -> None:
        """Remove a participant from the session"""
        for participant in self.participants:
            if participant.client_id == client_id:
                participant.is_connected = False
                break
        self.updated_at = datetime.now()
    
    def get_participant(self, client_id: str) -> Optional[Participant]:
        """Get a participant by client_id"""
        for participant in self.participants:
            if participant.client_id == client_id:
                return participant
        return None
    
    def update_code(self, code: str, language: str) -> None:
        """Update the current code and language"""
        self.current_code = code
        self.current_language = language
        self.updated_at = datetime.now()
    
    def add_execution_result(self, result: ExecutionResult) -> None:
        """Add an execution result to history"""
        self.execution_history.append(result)
        # Keep only last 50 executions to prevent memory issues
        if len(self.execution_history) > 50:
            self.execution_history = self.execution_history[-50:]
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "host_name": self.host_name,
            "session_name": self.session_name,
            "status": self.status.value,
            "current_code": self.current_code,
            "current_language": self.current_language,
            "participant_count": self.participant_count,
            "max_participants": self.max_participants,
            "participants": [p.to_dict() for p in self.participants if p.is_connected],
            "execution_history": [e.to_dict() for e in self.execution_history[-10:]]  # Last 10
        }


@dataclass
class Language:
    """
    Represents a supported programming language.
    
    Contains metadata about the language including default code templates.
    """
    id: str
    name: str
    version: str
    file_extension: str
    monaco_language: str  # Language ID for Monaco editor
    can_run_in_browser: bool
    default_code: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "file_extension": self.file_extension,
            "monaco_language": self.monaco_language,
            "can_run_in_browser": self.can_run_in_browser,
            "default_code": self.default_code
        }
