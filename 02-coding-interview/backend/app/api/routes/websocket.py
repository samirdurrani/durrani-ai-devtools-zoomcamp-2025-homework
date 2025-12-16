"""
WebSocket API Route

Real-time collaboration endpoint for coding sessions.
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

from app.services.session_manager import session_manager
from app.services.connection_manager import connection_manager
from app.services.code_executor import code_executor
from app.models.domain import ParticipantRole, ExecutionResult
from app.schemas.websocket import parse_client_message
from app.core.config import settings


# Set up logging
logger = logging.getLogger(__name__)

# Create a router for WebSocket endpoint
router = APIRouter()


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time collaboration.
    
    This handles all real-time communication for a coding session including:
    - Code synchronization
    - Language changes
    - User presence
    - Execution results
    
    Message Format:
    ```json
    {
        "type": "message_type",
        "data": {...},
        "timestamp": "ISO 8601 timestamp"
    }
    ```
    
    Args:
        websocket: WebSocket connection
        session_id: Session to join
    """
    client_id = None
    
    try:
        # Check if session exists
        try:
            session = session_manager.get_session(session_id)
        except:
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
        connection_id = await connection_manager.connect(websocket, session_id, "unknown")
        
        logger.info(f"WebSocket connected for session {session_id}")
        
        # Main message loop
        while True:
            # Receive message from client
            try:
                data = await websocket.receive_json()
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {
                        "code": "INVALID_JSON",
                        "message": "Invalid JSON format"
                    },
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            # Parse message
            try:
                message = parse_client_message(data)
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {
                        "code": "INVALID_MESSAGE",
                        "message": str(e)
                    },
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            # Handle different message types
            message_type = message.type
            
            if message_type == "join_session":
                # User is joining the session
                client_id = message.client_id
                
                # Add participant to session
                try:
                    participant = session_manager.add_participant(
                        session_id=session_id,
                        client_id=client_id,
                        display_name=message.display_name,
                        role=ParticipantRole.PARTICIPANT,
                        connection_id=connection_id
                    )
                    
                    # Send current session state to new user
                    await websocket.send_json({
                        "type": "session_state",
                        "data": {
                            "session_id": session_id,
                            "code": session.current_code,
                            "language": session.current_language,
                            "participant_count": session.participant_count,
                            "participants": [
                                {
                                    "client_id": p.client_id,
                                    "display_name": p.display_name,
                                    "role": p.role.value
                                }
                                for p in session.participants
                                if p.is_connected
                            ]
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Broadcast user joined to others
                    await connection_manager.broadcast_to_session(
                        session_id=session_id,
                        message={
                            "type": "user_joined",
                            "data": {
                                "session_id": session_id,
                                "client_id": client_id,
                                "display_name": message.display_name,
                                "participant_count": session.participant_count,
                                "participants": [
                                    {
                                        "client_id": p.client_id,
                                        "display_name": p.display_name,
                                        "role": p.role.value
                                    }
                                    for p in session.participants
                                    if p.is_connected
                                ]
                            },
                            "timestamp": datetime.now().isoformat()
                        },
                        exclude=websocket
                    )
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": {
                            "code": "JOIN_FAILED",
                            "message": str(e)
                        },
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_type == "code_update":
                # User is updating code
                session_manager.update_session_code(
                    session_id=session_id,
                    code=message.code,
                    language=message.language
                )
                
                # Broadcast to other users
                await connection_manager.broadcast_to_session(
                    session_id=session_id,
                    message={
                        "type": "code_update",
                        "data": {
                            "session_id": session_id,
                            "client_id": message.client_id,
                            "display_name": session.get_participant(message.client_id).display_name
                                if session.get_participant(message.client_id) else "Unknown",
                            "code": message.code,
                            "language": message.language,
                            "cursor_position": message.cursor_position
                        },
                        "timestamp": datetime.now().isoformat()
                    },
                    exclude=websocket
                )
            
            elif message_type == "language_change":
                # User is changing language
                session.current_language = message.language
                session.updated_at = datetime.now()
                
                # Broadcast to other users
                await connection_manager.broadcast_to_session(
                    session_id=session_id,
                    message={
                        "type": "language_change",
                        "data": {
                            "session_id": session_id,
                            "client_id": message.client_id,
                            "display_name": session.get_participant(message.client_id).display_name
                                if session.get_participant(message.client_id) else "Unknown",
                            "language": message.language
                        },
                        "timestamp": datetime.now().isoformat()
                    },
                    exclude=websocket
                )
            
            elif message_type == "execute_code":
                # User wants to execute code
                # Check rate limit
                if not session_manager.check_rate_limit(session_id):
                    await websocket.send_json({
                        "type": "error",
                        "data": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Rate limit exceeded: {settings.rate_limit_executions_per_minute} executions per minute"
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Execute code
                try:
                    stdout, stderr, exit_code, duration_ms, error = code_executor.execute(
                        code=message.code,
                        language=message.language,
                        stdin="",
                        time_limit_ms=settings.code_execution_timeout * 1000
                    )
                    
                    # Create execution result
                    result = ExecutionResult(
                        session_id=session_id,
                        language=message.language,
                        stdout=stdout,
                        stderr=stderr,
                        exit_code=exit_code,
                        duration_ms=duration_ms,
                        success=(exit_code == 0 and error is None),
                        error=error,
                        executed_by=message.client_id
                    )
                    
                    # Add to session history
                    session_manager.add_execution_result(session_id, result)
                    
                    # Broadcast result to all users
                    await connection_manager.broadcast_to_all(
                        session_id=session_id,
                        message={
                            "type": "execution_result",
                            "data": {
                                "session_id": session_id,
                                "client_id": message.client_id,
                                "result": {
                                    "stdout": stdout,
                                    "stderr": stderr,
                                    "exit_code": exit_code,
                                    "duration": duration_ms,
                                    "success": result.success,
                                    "error": error
                                }
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": {
                            "code": "EXECUTION_FAILED",
                            "message": str(e)
                        },
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_type == "leave_session":
                # User is leaving
                break
    
    except WebSocketDisconnect:
        # Client disconnected
        logger.info(f"WebSocket disconnected for session {session_id}")
    
    except Exception as e:
        # Unexpected error
        logger.error(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "data": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                },
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass
    
    finally:
        # Clean up connection
        session_id_disconnected, client_id_disconnected = connection_manager.disconnect(websocket)
        
        if session_id_disconnected and client_id_disconnected:
            # Remove participant from session
            session_manager.remove_participant(session_id_disconnected, client_id_disconnected)
            
            # Get updated session
            try:
                session = session_manager.get_session(session_id_disconnected)
                
                # Broadcast user left to remaining users
                await connection_manager.broadcast_to_session(
                    session_id=session_id_disconnected,
                    message={
                        "type": "user_left",
                        "data": {
                            "session_id": session_id_disconnected,
                            "client_id": client_id_disconnected,
                            "display_name": "User",
                            "participant_count": session.participant_count
                        },
                        "timestamp": datetime.now().isoformat()
                    },
                    exclude=None
                )
            except:
                pass  # Session might have been deleted
