import { io } from 'socket.io-client';
import { WS_BASE_URL, WS_EVENTS } from '../utils/constants';

// WebSocket service class for managing real-time connections
class WebSocketService {
  constructor() {
    this.socket = null;
    this.sessionId = null;
    this.listeners = new Map(); // Store event listeners for cleanup
  }

  // Connect to WebSocket server for a specific session
  connect(sessionId) {
    if (this.socket && this.socket.connected) {
      this.disconnect();
    }

    this.sessionId = sessionId;
    
    // Connect to the WebSocket server with session ID in the path
    this.socket = io(`${WS_BASE_URL}/sessions/${sessionId}`, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    });

    // Set up connection event handlers
    this.socket.on('connect', () => {
      console.log('WebSocket connected to session:', sessionId);
      // Join the session room
      this.emit(WS_EVENTS.JOIN_SESSION, { sessionId });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error.message);
    });

    return this.socket;
  }

  // Disconnect from WebSocket server
  disconnect() {
    if (this.socket) {
      // Clean up all listeners
      this.listeners.forEach((handler, event) => {
        this.socket.off(event, handler);
      });
      this.listeners.clear();
      
      // Leave session and disconnect
      if (this.sessionId) {
        this.emit(WS_EVENTS.LEAVE_SESSION, { sessionId: this.sessionId });
      }
      
      this.socket.disconnect();
      this.socket = null;
      this.sessionId = null;
    }
  }

  // Send an event to the server
  emit(event, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('Cannot emit event - socket not connected:', event);
    }
  }

  // Listen for events from the server
  on(event, handler) {
    if (this.socket) {
      // Store the handler for cleanup
      this.listeners.set(event, handler);
      this.socket.on(event, handler);
    } else {
      console.warn('Cannot add listener - socket not initialized:', event);
    }
  }

  // Remove event listener
  off(event) {
    if (this.socket) {
      const handler = this.listeners.get(event);
      if (handler) {
        this.socket.off(event, handler);
        this.listeners.delete(event);
      }
    }
  }

  // Check if connected
  isConnected() {
    return this.socket && this.socket.connected;
  }

  // Get current session ID
  getSessionId() {
    return this.sessionId;
  }
}

// Export a singleton instance
export const wsService = new WebSocketService();
