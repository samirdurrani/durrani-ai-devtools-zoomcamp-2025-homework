import { useEffect, useState, useCallback, useRef } from 'react';
import { wsService } from '../services/websocket';
import { WS_EVENTS } from '../utils/constants';

// Custom hook for managing WebSocket connections
export const useWebSocket = (sessionId) => {
  const [isConnected, setIsConnected] = useState(false);
  const [participants, setParticipants] = useState(0);
  const [connectionError, setConnectionError] = useState(null);
  const reconnectTimeoutRef = useRef(null);

  // Connect to WebSocket when sessionId changes
  useEffect(() => {
    if (!sessionId) return;

    // Connect to the session
    const socket = wsService.connect(sessionId);
    
    // Handle connection status
    socket.on('connect', () => {
      setIsConnected(true);
      setConnectionError(null);
      console.log('WebSocket connected successfully');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    });

    socket.on('connect_error', (error) => {
      setConnectionError(error.message);
      setIsConnected(false);
    });

    // Handle participant updates
    wsService.on(WS_EVENTS.USER_JOINED, (data) => {
      if (data.participantCount !== undefined) {
        setParticipants(data.participantCount);
      }
    });

    wsService.on(WS_EVENTS.USER_LEFT, (data) => {
      if (data.participantCount !== undefined) {
        setParticipants(data.participantCount);
      }
    });

    // Handle session state updates
    wsService.on(WS_EVENTS.SESSION_STATE, (data) => {
      if (data.participantCount !== undefined) {
        setParticipants(data.participantCount);
      }
    });

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsService.disconnect();
    };
  }, [sessionId]);

  // Send code update
  const sendCodeUpdate = useCallback((code, language) => {
    wsService.emit(WS_EVENTS.CODE_UPDATE, {
      code,
      language,
      timestamp: Date.now(),
    });
  }, []);

  // Send language change
  const sendLanguageChange = useCallback((language) => {
    wsService.emit(WS_EVENTS.LANGUAGE_CHANGE, {
      language,
      timestamp: Date.now(),
    });
  }, []);

  // Send code execution request
  const sendExecuteCode = useCallback((code, language) => {
    wsService.emit(WS_EVENTS.EXECUTE_CODE, {
      code,
      language,
      timestamp: Date.now(),
    });
  }, []);

  // Subscribe to events
  const subscribe = useCallback((event, handler) => {
    wsService.on(event, handler);
    
    // Return cleanup function
    return () => {
      wsService.off(event);
    };
  }, []);

  return {
    isConnected,
    participants,
    connectionError,
    sendCodeUpdate,
    sendLanguageChange,
    sendExecuteCode,
    subscribe,
  };
};
