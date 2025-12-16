"""
Session Manager Service

This service handles all session-related operations including:
- Creating and managing sessions
- Adding/removing participants
- Updating code and language
- Storing execution results

Currently uses in-memory storage but designed to easily swap to a database.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from threading import Lock

from app.models.domain import Session, Participant, ExecutionResult, SessionStatus, ParticipantRole
from app.core.config import settings
from app.core.exceptions import SessionNotFoundException, SessionFullException


class SessionManager:
    """
    Manages all active coding sessions.
    
    This is a singleton class that maintains the state of all sessions
    in memory. In production, this would be replaced with a database.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the session manager"""
        if self._initialized:
            return
        
        # Store sessions in a dictionary with session_id as key
        self._sessions: Dict[str, Session] = {}
        
        # Lock for thread-safe operations
        self._session_lock = Lock()
        
        # Track execution counts for rate limiting (session_id -> count)
        self._execution_counts: Dict[str, List[datetime]] = {}
        
        self._initialized = True
    
    def create_session(
        self,
        host_name: str = "Anonymous Host",
        session_name: Optional[str] = None,
        initial_language: str = "javascript",
        max_participants: int = 5
    ) -> Session:
        """
        Create a new coding session.
        
        Args:
            host_name: Name of the session host
            session_name: Optional name for the session
            initial_language: Starting programming language
            max_participants: Maximum number of participants
            
        Returns:
            Created Session object
        """
        # Generate unique session ID
        session_id = self._generate_session_id()
        
        # Get default code for the language
        default_code = self._get_default_code(initial_language)
        
        # Create the session
        session = Session(
            session_id=session_id,
            created_at=datetime.now(),
            host_name=host_name,
            session_name=session_name,
            status=SessionStatus.ACTIVE,
            current_code=default_code,
            current_language=initial_language,
            max_participants=max_participants
        )
        
        # Store the session (thread-safe)
        with self._session_lock:
            self._sessions[session_id] = session
            self._execution_counts[session_id] = []
        
        # Clean up old sessions
        self._cleanup_old_sessions()
        
        return session
    
    def get_session(self, session_id: str) -> Session:
        """
        Get a session by ID.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session object
            
        Raises:
            SessionNotFoundException: If session doesn't exist
        """
        session = self._sessions.get(session_id)
        if not session:
            raise SessionNotFoundException(session_id)
        return session
    
    def list_sessions(self, status: Optional[SessionStatus] = None) -> List[Session]:
        """
        List all sessions, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of sessions
        """
        sessions = list(self._sessions.values())
        
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        
        return sessions
    
    def update_session_code(
        self,
        session_id: str,
        code: str,
        language: str
    ) -> Session:
        """
        Update the code and language in a session.
        
        Args:
            session_id: Session to update
            code: New code content
            language: Programming language
            
        Returns:
            Updated session
        """
        session = self.get_session(session_id)
        session.update_code(code, language)
        return session
    
    def add_participant(
        self,
        session_id: str,
        client_id: str,
        display_name: str,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
        connection_id: Optional[str] = None
    ) -> Participant:
        """
        Add a participant to a session.
        
        Args:
            session_id: Session to join
            client_id: Unique client identifier
            display_name: Name to display
            role: Participant role
            connection_id: WebSocket connection ID
            
        Returns:
            Created Participant object
            
        Raises:
            SessionFullException: If session is at capacity
        """
        session = self.get_session(session_id)
        
        # Check if session is full (unless rejoining)
        existing = session.get_participant(client_id)
        if not existing and session.is_full:
            raise SessionFullException(session_id, session.max_participants)
        
        # Create participant
        participant = Participant(
            client_id=client_id,
            display_name=display_name,
            role=role,
            joined_at=datetime.now(),
            connection_id=connection_id,
            is_connected=True
        )
        
        # Add to session
        session.add_participant(participant)
        
        return participant
    
    def remove_participant(
        self,
        session_id: str,
        client_id: str
    ) -> None:
        """
        Remove a participant from a session.
        
        Args:
            session_id: Session to leave
            client_id: Client to remove
        """
        session = self.get_session(session_id)
        session.remove_participant(client_id)
    
    def add_execution_result(
        self,
        session_id: str,
        result: ExecutionResult
    ) -> None:
        """
        Add an execution result to a session's history.
        
        Args:
            session_id: Session where code was executed
            result: Execution result to store
        """
        session = self.get_session(session_id)
        session.add_execution_result(result)
    
    def check_rate_limit(self, session_id: str) -> bool:
        """
        Check if session has exceeded execution rate limit.
        
        Args:
            session_id: Session to check
            
        Returns:
            True if within limit, False if exceeded
        """
        if session_id not in self._execution_counts:
            self._execution_counts[session_id] = []
        
        # Remove executions older than 1 minute
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        self._execution_counts[session_id] = [
            dt for dt in self._execution_counts[session_id]
            if dt > cutoff
        ]
        
        # Check if under limit
        current_count = len(self._execution_counts[session_id])
        if current_count >= settings.rate_limit_executions_per_minute:
            return False
        
        # Add this execution
        self._execution_counts[session_id].append(now)
        return True
    
    def end_session(self, session_id: str) -> None:
        """
        Mark a session as completed.
        
        Args:
            session_id: Session to end
        """
        session = self.get_session(session_id)
        session.status = SessionStatus.COMPLETED
        session.updated_at = datetime.now()
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete a session entirely.
        
        Args:
            session_id: Session to delete
        """
        with self._session_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
            if session_id in self._execution_counts:
                del self._execution_counts[session_id]
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        Returns:
            Random alphanumeric string
        """
        while True:
            # Generate random string
            session_id = ''.join(
                random.choices(
                    string.ascii_lowercase + string.digits,
                    k=settings.session_id_length
                )
            )
            
            # Ensure it's unique
            if session_id not in self._sessions:
                return session_id
    
    def _get_default_code(self, language: str) -> str:
        """
        Get default code template for a language.
        
        Args:
            language: Programming language ID
            
        Returns:
            Default code template
        """
        # This would normally come from the language configuration
        templates = {
            "javascript": """// Welcome to the coding interview platform!
// Start writing your JavaScript code here

function solution() {
  console.log("Hello, World!");
}

solution();""",
            "python": """# Welcome to the coding interview platform!
# Start writing your Python code here

def solution():
    print("Hello, World!")

solution()""",
            "java": """// Welcome to the coding interview platform!
// Start writing your Java code here

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}""",
            "cpp": """// Welcome to the coding interview platform!
// Start writing your C++ code here

#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}"""
        }
        
        return templates.get(language, "// Start coding here...")
    
    def _cleanup_old_sessions(self) -> None:
        """
        Remove sessions older than configured max age.
        
        This prevents memory leaks from abandoned sessions.
        """
        if len(self._sessions) < 100:  # Only cleanup if we have many sessions
            return
        
        cutoff = datetime.now() - timedelta(hours=settings.max_session_age_hours)
        
        with self._session_lock:
            # Find old sessions
            old_sessions = [
                sid for sid, session in self._sessions.items()
                if session.updated_at < cutoff and session.status != SessionStatus.ACTIVE
            ]
            
            # Delete them
            for session_id in old_sessions:
                del self._sessions[session_id]
                if session_id in self._execution_counts:
                    del self._execution_counts[session_id]


# Create a global instance
session_manager = SessionManager()
