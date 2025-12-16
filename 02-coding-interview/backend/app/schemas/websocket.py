"""
WebSocket Message Schemas

Pydantic models for WebSocket messages.
These define the structure of messages sent between client and server.
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional, Union
from pydantic import BaseModel, Field


# Base message structure
class WebSocketMessage(BaseModel):
    """
    Base class for all WebSocket messages.
    
    Every message has a type field that determines how it should be handled.
    """
    type: str = Field(..., description="Message type identifier")
    timestamp: datetime = Field(default_factory=datetime.now)


# Client to Server Messages
class JoinSessionMessage(BaseModel):
    """Client wants to join a session"""
    type: Literal["join_session"]
    session_id: str
    client_id: str
    display_name: str


class LeaveSessionMessage(BaseModel):
    """Client is leaving the session"""
    type: Literal["leave_session"]
    session_id: str
    client_id: str


class CodeUpdateMessage(BaseModel):
    """Client is updating the code"""
    type: Literal["code_update"]
    session_id: str
    client_id: str
    code: str
    language: str
    cursor_position: Optional[Dict[str, int]] = None  # {"line": 10, "column": 5}


class LanguageChangeMessage(BaseModel):
    """Client is changing the language"""
    type: Literal["language_change"]
    session_id: str
    client_id: str
    language: str


class ExecuteCodeMessage(BaseModel):
    """Client wants to execute code"""
    type: Literal["execute_code"]
    session_id: str
    client_id: str
    code: str
    language: str


# Server to Client Messages
class UserJoinedMessage(BaseModel):
    """Notify clients that a user joined"""
    type: Literal["user_joined"]
    session_id: str
    client_id: str
    display_name: str
    participant_count: int
    participants: list


class UserLeftMessage(BaseModel):
    """Notify clients that a user left"""
    type: Literal["user_left"]
    session_id: str
    client_id: str
    display_name: str
    participant_count: int


class CodeUpdateBroadcast(BaseModel):
    """Broadcast code changes to all clients"""
    type: Literal["code_update"]
    session_id: str
    client_id: str
    display_name: str
    code: str
    language: str
    cursor_position: Optional[Dict[str, int]] = None


class LanguageChangeBroadcast(BaseModel):
    """Broadcast language change to all clients"""
    type: Literal["language_change"]
    session_id: str
    client_id: str
    display_name: str
    language: str


class ExecutionResultBroadcast(BaseModel):
    """Broadcast execution results to all clients"""
    type: Literal["execution_result"]
    session_id: str
    client_id: str
    result: Dict[str, Any]


class SessionStateMessage(BaseModel):
    """Send full session state (usually on join)"""
    type: Literal["session_state"]
    session_id: str
    code: str
    language: str
    participant_count: int
    participants: list


class ErrorMessage(BaseModel):
    """Error notification"""
    type: Literal["error"]
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# Union type for all possible messages
ClientMessage = Union[
    JoinSessionMessage,
    LeaveSessionMessage,
    CodeUpdateMessage,
    LanguageChangeMessage,
    ExecuteCodeMessage
]

ServerMessage = Union[
    UserJoinedMessage,
    UserLeftMessage,
    CodeUpdateBroadcast,
    LanguageChangeBroadcast,
    ExecutionResultBroadcast,
    SessionStateMessage,
    ErrorMessage
]


def parse_client_message(data: dict) -> ClientMessage:
    """
    Parse a client message based on its type.
    
    Args:
        data: Raw message data from client
        
    Returns:
        Parsed message object
        
    Raises:
        ValueError: If message type is unknown or data is invalid
    """
    message_type = data.get("type")
    
    if not message_type:
        raise ValueError("Message must have a 'type' field")
    
    message_classes = {
        "join_session": JoinSessionMessage,
        "leave_session": LeaveSessionMessage,
        "code_update": CodeUpdateMessage,
        "language_change": LanguageChangeMessage,
        "execute_code": ExecuteCodeMessage,
    }
    
    message_class = message_classes.get(message_type)
    if not message_class:
        raise ValueError(f"Unknown message type: {message_type}")
    
    return message_class(**data)
