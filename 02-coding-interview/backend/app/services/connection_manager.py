"""
WebSocket Connection Manager

This service manages WebSocket connections for real-time collaboration.
It handles:
- Connection tracking
- Message broadcasting
- Connection lifecycle
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for all sessions.
    
    This class keeps track of which clients are connected to which sessions
    and provides methods for broadcasting messages.
    """
    
    def __init__(self):
        """Initialize the connection manager"""
        # Map session_id -> List of WebSocket connections
        self._connections: Dict[str, List[WebSocket]] = {}
        
        # Map connection_id -> (session_id, client_id) for reverse lookup
        self._connection_info: Dict[str, tuple] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        client_id: str
    ) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection object
            session_id: Session to join
            client_id: Client identifier
            
        Returns:
            Connection ID for this connection
        """
        # Accept the connection
        await websocket.accept()
        
        # Generate connection ID (using object ID for simplicity)
        connection_id = str(id(websocket))
        
        # Add to session connections
        if session_id not in self._connections:
            self._connections[session_id] = []
        self._connections[session_id].append(websocket)
        
        # Store connection info
        self._connection_info[connection_id] = (session_id, client_id)
        
        logger.info(f"Client {client_id} connected to session {session_id}")
        
        return connection_id
    
    def disconnect(self, websocket: WebSocket) -> tuple:
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
            
        Returns:
            Tuple of (session_id, client_id) for the disconnected client
        """
        connection_id = str(id(websocket))
        
        # Get connection info
        info = self._connection_info.get(connection_id)
        if not info:
            return None, None
        
        session_id, client_id = info
        
        # Remove from session connections
        if session_id in self._connections:
            try:
                self._connections[session_id].remove(websocket)
                # Clean up empty session
                if not self._connections[session_id]:
                    del self._connections[session_id]
            except ValueError:
                pass  # Connection was already removed
        
        # Remove connection info
        if connection_id in self._connection_info:
            del self._connection_info[connection_id]
        
        logger.info(f"Client {client_id} disconnected from session {session_id}")
        
        return session_id, client_id
    
    async def send_to_client(
        self,
        websocket: WebSocket,
        message: dict
    ) -> None:
        """
        Send a message to a specific client.
        
        Args:
            websocket: Target WebSocket connection
            message: Message to send (will be JSON encoded)
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
    
    async def broadcast_to_session(
        self,
        session_id: str,
        message: dict,
        exclude: WebSocket = None
    ) -> None:
        """
        Broadcast a message to all clients in a session.
        
        Args:
            session_id: Target session
            message: Message to broadcast
            exclude: Optional WebSocket to exclude (usually the sender)
        """
        if session_id not in self._connections:
            return
        
        # Send to all connections in the session
        disconnected = []
        for connection in self._connections[session_id]:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                # Connection is dead, mark for removal
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up dead connections
        for connection in disconnected:
            try:
                self.disconnect(connection)
            except:
                pass
    
    async def broadcast_to_all(
        self,
        session_id: str,
        message: dict
    ) -> None:
        """
        Broadcast a message to all clients in a session (including sender).
        
        Args:
            session_id: Target session
            message: Message to broadcast
        """
        await self.broadcast_to_session(session_id, message, exclude=None)
    
    def get_session_connections(self, session_id: str) -> int:
        """
        Get the number of active connections in a session.
        
        Args:
            session_id: Session to check
            
        Returns:
            Number of active connections
        """
        return len(self._connections.get(session_id, []))
    
    def get_all_sessions(self) -> Set[str]:
        """
        Get all sessions with active connections.
        
        Returns:
            Set of session IDs
        """
        return set(self._connections.keys())
    
    async def close_session_connections(self, session_id: str) -> None:
        """
        Close all connections in a session.
        
        Args:
            session_id: Session to close
        """
        if session_id not in self._connections:
            return
        
        # Send close message to all connections
        close_message = {
            "type": "session_ended",
            "message": "Session has been ended by the host"
        }
        
        for connection in self._connections[session_id]:
            try:
                await connection.send_json(close_message)
                await connection.close()
            except:
                pass  # Connection might already be closed
        
        # Clean up
        del self._connections[session_id]
        
        # Remove connection info for these connections
        to_remove = [
            cid for cid, (sid, _) in self._connection_info.items()
            if sid == session_id
        ]
        for connection_id in to_remove:
            del self._connection_info[connection_id]


# Create a global instance
connection_manager = ConnectionManager()
