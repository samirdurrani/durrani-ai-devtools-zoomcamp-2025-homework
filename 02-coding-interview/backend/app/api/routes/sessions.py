"""
Sessions API Routes

Endpoints for managing coding interview sessions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.session import (
    CreateSessionRequest,
    SessionResponse,
    SessionDetails,
    SessionListResponse,
    ParticipantInfo,
    ExecutionSummary
)
from app.services.session_manager import session_manager
from app.core.config import settings


# Create a router for session endpoints
router = APIRouter(
    prefix="/api/v1/sessions",
    tags=["Sessions"]
)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new session",
    description="Creates a new coding interview session and returns a shareable URL"
)
async def create_session(
    request: CreateSessionRequest = CreateSessionRequest()
):
    """
    Create a new coding interview session.
    
    The session will be initialized with default code for the selected language.
    A unique session ID will be generated for sharing.
    
    Args:
        request: Optional session configuration
        
    Returns:
        Created session with join URL
    """
    # Create the session
    session = session_manager.create_session(
        host_name=request.host_name or "Anonymous Host",
        session_name=request.session_name,
        initial_language=request.initial_language,
        max_participants=request.max_participants
    )
    
    # Generate join URL
    join_url = f"{settings.frontend_url}/session/{session.session_id}"
    
    # Return response
    return SessionResponse(
        session_id=session.session_id,
        join_url=join_url,
        created_at=session.created_at,
        host_name=session.host_name,
        status=session.status.value,
        participant_count=session.participant_count
    )


@router.get(
    "",
    response_model=SessionListResponse,
    summary="List sessions",
    description="Returns a list of all sessions, optionally filtered by status"
)
async def list_sessions(
    status: Optional[str] = Query(
        "active",
        description="Filter by session status (active, completed, all)"
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of sessions to return"
    )
):
    """
    List all sessions.
    
    This endpoint is mainly for debugging and admin purposes.
    In production, it should be restricted to authenticated admins.
    
    Args:
        status: Optional status filter
        limit: Maximum number of results
        
    Returns:
        List of sessions with summary information
    """
    # Get sessions from manager
    if status == "all":
        sessions = session_manager.list_sessions()
    else:
        from app.models.domain import SessionStatus
        try:
            status_enum = SessionStatus(status) if status else SessionStatus.ACTIVE
            sessions = session_manager.list_sessions(status=status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    # Apply limit
    sessions = sessions[:limit]
    
    # Convert to response format
    session_responses = []
    for session in sessions:
        join_url = f"{settings.frontend_url}/session/{session.session_id}"
        session_responses.append(
            SessionResponse(
                session_id=session.session_id,
                join_url=join_url,
                created_at=session.created_at,
                host_name=session.host_name,
                status=session.status.value,
                participant_count=session.participant_count
            )
        )
    
    return SessionListResponse(
        sessions=session_responses,
        total=len(session_responses)
    )


@router.get(
    "/{session_id}",
    response_model=SessionDetails,
    summary="Get session details",
    description="Returns detailed information about a specific session"
)
async def get_session(session_id: str):
    """
    Get detailed information about a session.
    
    This includes current code, participants, and execution history.
    Used when a participant joins to sync their state.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Detailed session information
        
    Raises:
        404: If session doesn't exist
    """
    # Get session from manager
    try:
        session = session_manager.get_session(session_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # Generate join URL
    join_url = f"{settings.frontend_url}/session/{session.session_id}"
    
    # Convert participants
    participants = [
        ParticipantInfo(
            client_id=p.client_id,
            display_name=p.display_name,
            role=p.role.value,
            joined_at=p.joined_at,
            is_connected=p.is_connected
        )
        for p in session.participants
        if p.is_connected
    ]
    
    # Convert execution history (last 10)
    execution_history = [
        ExecutionSummary(
            timestamp=e.timestamp,
            language=e.language,
            stdout=e.stdout[:500] if e.stdout else "",  # Truncate
            success=e.success,
            duration=e.duration_ms
        )
        for e in session.execution_history[-10:]
    ]
    
    # Return detailed response
    return SessionDetails(
        session_id=session.session_id,
        join_url=join_url,
        created_at=session.created_at,
        updated_at=session.updated_at,
        host_name=session.host_name,
        session_name=session.session_name,
        status=session.status.value,
        participant_count=session.participant_count,
        max_participants=session.max_participants,
        participants=participants,
        current_code=session.current_code,
        current_language=session.current_language,
        execution_history=execution_history
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End a session",
    description="Marks a session as completed and disconnects all participants"
)
async def end_session(session_id: str):
    """
    End a coding session.
    
    This marks the session as completed and disconnects all participants.
    Only the session host should be able to end a session.
    
    Args:
        session_id: Session to end
        
    Raises:
        404: If session doesn't exist
    """
    try:
        session_manager.end_session(session_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # In a real implementation, we would also:
    # 1. Verify the requester is the session host
    # 2. Disconnect all WebSocket connections
    # 3. Send notifications to participants
    
    return None  # 204 No Content
