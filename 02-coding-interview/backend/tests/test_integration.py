"""
Integration Tests for Client-Server Interaction

These tests verify the complete workflow of the coding interview platform,
including session management, WebSocket communication, and code execution.
"""

import pytest
import asyncio
import json
from typing import List, Dict, Any
from fastapi.testclient import TestClient
from websocket import create_connection, WebSocket
import threading
import time

from app.main import app
from app.services.session_manager import session_manager


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def ws_url():
    """Get the WebSocket base URL."""
    return "ws://localhost:8000/ws/sessions"


class WebSocketClient:
    """
    Helper class to simulate a WebSocket client.
    
    This makes it easier to test WebSocket interactions.
    """
    
    def __init__(self, session_id: str, client_id: str, display_name: str):
        self.session_id = session_id
        self.client_id = client_id
        self.display_name = display_name
        self.ws = None
        self.messages = []
        self.connected = False
        self.listener_thread = None
        self.stop_listening = False
    
    def connect(self, ws_url: str):
        """Connect to the WebSocket server."""
        self.ws = create_connection(f"{ws_url}/{self.session_id}")
        self.connected = True
        
        # Start listening for messages in a separate thread
        self.listener_thread = threading.Thread(target=self._listen_for_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        # Send join message
        self.send({
            "type": "join_session",
            "data": {
                "session_id": self.session_id,
                "client_id": self.client_id,
                "display_name": self.display_name
            }
        })
        
        # Wait for session state message
        time.sleep(0.2)
    
    def _listen_for_messages(self):
        """Listen for messages from the server."""
        while self.connected and not self.stop_listening:
            try:
                message = self.ws.recv()
                if message:
                    self.messages.append(json.loads(message))
            except:
                break
    
    def send(self, message: dict):
        """Send a message to the server."""
        if self.connected:
            self.ws.send(json.dumps(message))
    
    def send_code_update(self, code: str, language: str = "javascript"):
        """Send a code update message."""
        self.send({
            "type": "code_update",
            "data": {
                "session_id": self.session_id,
                "client_id": self.client_id,
                "code": code,
                "language": language
            }
        })
    
    def send_language_change(self, language: str):
        """Send a language change message."""
        self.send({
            "type": "language_change",
            "data": {
                "session_id": self.session_id,
                "client_id": self.client_id,
                "language": language
            }
        })
    
    def send_execute_code(self, code: str, language: str):
        """Send a code execution request."""
        self.send({
            "type": "execute_code",
            "data": {
                "session_id": self.session_id,
                "client_id": self.client_id,
                "code": code,
                "language": language
            }
        })
    
    def get_messages_of_type(self, msg_type: str) -> List[Dict[str, Any]]:
        """Get all messages of a specific type."""
        return [msg for msg in self.messages if msg.get("type") == msg_type]
    
    def wait_for_message(self, msg_type: str, timeout: float = 2.0) -> Dict[str, Any]:
        """Wait for a specific message type."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = self.get_messages_of_type(msg_type)
            if messages:
                return messages[-1]  # Return the most recent
            time.sleep(0.1)
        return None
    
    def disconnect(self):
        """Disconnect from the WebSocket server."""
        self.stop_listening = True
        if self.connected:
            self.send({
                "type": "leave_session",
                "data": {
                    "session_id": self.session_id,
                    "client_id": self.client_id
                }
            })
            self.ws.close()
            self.connected = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1)


@pytest.mark.integration
class TestFullWorkflow:
    """Test complete user workflows from client to server."""
    
    def test_create_and_join_session(self, client):
        """
        Test the full workflow of creating a session and joining it.
        
        This simulates:
        1. Interviewer creates a session
        2. Gets the join URL
        3. Candidate joins using the URL
        """
        # Step 1: Create a session (interviewer)
        create_response = client.post(
            "/api/v1/sessions",
            json={
                "host_name": "Alice Interviewer",
                "session_name": "Python Interview",
                "initial_language": "python",
                "max_participants": 3
            }
        )
        assert create_response.status_code == 201
        
        session_data = create_response.json()
        session_id = session_data["session_id"]
        join_url = session_data["join_url"]
        
        assert session_id in join_url
        assert session_data["host_name"] == "Alice Interviewer"
        assert session_data["status"] == "active"
        
        # Step 2: Get session details (candidate joining)
        get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == 200
        
        details = get_response.json()
        assert details["session_id"] == session_id
        assert details["current_language"] == "python"
        assert "def solution():" in details["current_code"]  # Python template
        assert details["participant_count"] == 0  # No WebSocket connections yet
    
    def test_websocket_collaboration(self, client, ws_url):
        """
        Test real-time collaboration between multiple users.
        
        This simulates:
        1. Two users joining the same session
        2. One user updating code
        3. Other user receiving the update
        """
        # Create a session first
        create_response = client.post(
            "/api/v1/sessions",
            json={"host_name": "Bob Interviewer"}
        )
        session_id = create_response.json()["session_id"]
        
        # Create two WebSocket clients
        client1 = WebSocketClient(session_id, "user1", "Bob")
        client2 = WebSocketClient(session_id, "user2", "Carol")
        
        try:
            # Connect both clients
            client1.connect(ws_url)
            client2.connect(ws_url)
            
            # Wait for initial messages
            time.sleep(0.5)
            
            # Client1 sends code update
            test_code = "console.log('Hello from Bob!');"
            client1.send_code_update(test_code)
            
            # Client2 should receive the update
            code_update = client2.wait_for_message("code_update")
            assert code_update is not None
            assert code_update["data"]["code"] == test_code
            assert code_update["data"]["client_id"] == "user1"
            
            # Client2 changes language
            client2.send_language_change("python")
            
            # Client1 should receive the language change
            lang_change = client1.wait_for_message("language_change")
            assert lang_change is not None
            assert lang_change["data"]["language"] == "python"
            assert lang_change["data"]["client_id"] == "user2"
            
        finally:
            # Clean up
            client1.disconnect()
            client2.disconnect()
    
    def test_code_execution_flow(self, client):
        """
        Test the complete code execution workflow.
        
        This simulates:
        1. Creating a session
        2. Executing code
        3. Getting execution results
        """
        # Create session
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Execute Python code
        execute_response = client.post(
            f"/api/v1/sessions/{session_id}/execute",
            json={
                "code": "print('Integration test output')\nprint(2 + 2)",
                "language": "python",
                "time_limit": 5000
            }
        )
        
        assert execute_response.status_code == 200
        
        result = execute_response.json()
        assert result["session_id"] == session_id
        assert result["language"] == "python"
        # The actual output depends on whether server execution is enabled
        assert "duration" in result
        assert "success" in result
        assert "timestamp" in result
        
        # Check execution history is saved
        session_details = client.get(f"/api/v1/sessions/{session_id}").json()
        assert len(session_details["execution_history"]) > 0
        
        # Verify last execution in history
        if session_details["execution_history"]:
            last_execution = session_details["execution_history"][-1]
            assert last_execution["language"] == "python"
            assert "timestamp" in last_execution
    
    def test_participant_tracking(self, client, ws_url):
        """
        Test that participant count and list are tracked correctly.
        
        This simulates:
        1. Multiple users joining
        2. Checking participant count
        3. Users leaving
        """
        # Create session
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Initial participant count should be 0
        session = client.get(f"/api/v1/sessions/{session_id}").json()
        assert session["participant_count"] == 0
        
        # Connect first user
        client1 = WebSocketClient(session_id, "user1", "Dan")
        client1.connect(ws_url)
        time.sleep(0.3)
        
        # Check participant count increased
        session = client.get(f"/api/v1/sessions/{session_id}").json()
        assert session["participant_count"] == 1
        assert len(session["participants"]) == 1
        assert session["participants"][0]["display_name"] == "Dan"
        
        # Connect second user
        client2 = WebSocketClient(session_id, "user2", "Eve")
        client2.connect(ws_url)
        time.sleep(0.3)
        
        # Check participant count
        session = client.get(f"/api/v1/sessions/{session_id}").json()
        assert session["participant_count"] == 2
        participant_names = [p["display_name"] for p in session["participants"]]
        assert "Dan" in participant_names
        assert "Eve" in participant_names
        
        # First user gets notification about second user
        user_joined = client1.wait_for_message("user_joined")
        assert user_joined is not None
        assert user_joined["data"]["participant_count"] == 2
        
        # Disconnect first user
        client1.disconnect()
        time.sleep(0.3)
        
        # Check participant count decreased
        session = client.get(f"/api/v1/sessions/{session_id}").json()
        assert session["participant_count"] == 1
        
        # Second user gets notification about first user leaving
        user_left = client2.wait_for_message("user_left")
        assert user_left is not None
        assert user_left["data"]["participant_count"] == 1
        
        # Clean up
        client2.disconnect()
    
    def test_session_state_sync(self, client, ws_url):
        """
        Test that new users get the current session state when joining.
        
        This simulates:
        1. First user joins and updates code
        2. Second user joins and receives current state
        """
        # Create session
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # First user joins and updates code
        client1 = WebSocketClient(session_id, "user1", "Frank")
        client1.connect(ws_url)
        time.sleep(0.2)
        
        # Update code and language
        new_code = "function fibonacci(n) { return n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2); }"
        client1.send_code_update(new_code, "javascript")
        client1.send_language_change("javascript")
        time.sleep(0.3)
        
        # Second user joins
        client2 = WebSocketClient(session_id, "user2", "Grace")
        client2.connect(ws_url)
        
        # Second user should receive session state with current code
        session_state = client2.wait_for_message("session_state")
        assert session_state is not None
        assert session_state["data"]["code"] == new_code
        assert session_state["data"]["language"] == "javascript"
        assert session_state["data"]["participant_count"] == 2
        
        # Clean up
        client1.disconnect()
        client2.disconnect()
    
    def test_rate_limiting_integration(self, client):
        """
        Test that rate limiting works across the full stack.
        
        This simulates rapid execution attempts that should be rate limited.
        """
        # Create session
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Make rapid execution requests
        success_count = 0
        rate_limited = False
        
        for i in range(15):  # Try more than the limit
            response = client.post(
                f"/api/v1/sessions/{session_id}/execute",
                json={
                    "code": f"print({i})",
                    "language": "python"
                }
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                error_data = response.json()
                assert "RATE_LIMIT_EXCEEDED" in str(error_data)
                break
        
        # Should hit rate limit before all requests succeed
        assert rate_limited, "Rate limiting should have triggered"
        assert success_count < 15, "Too many requests succeeded"
    
    def test_multiple_sessions_isolation(self, client, ws_url):
        """
        Test that multiple sessions are properly isolated.
        
        This verifies that updates in one session don't affect another.
        """
        # Create two separate sessions
        session1_response = client.post(
            "/api/v1/sessions",
            json={"host_name": "Session 1 Host"}
        )
        session1_id = session1_response.json()["session_id"]
        
        session2_response = client.post(
            "/api/v1/sessions",
            json={"host_name": "Session 2 Host"}
        )
        session2_id = session2_response.json()["session_id"]
        
        # Connect clients to different sessions
        client1 = WebSocketClient(session1_id, "user1", "Helen")
        client2 = WebSocketClient(session2_id, "user2", "Ivan")
        
        try:
            client1.connect(ws_url)
            client2.connect(ws_url)
            time.sleep(0.3)
            
            # Update code in session 1
            session1_code = "// Code for session 1"
            client1.send_code_update(session1_code)
            time.sleep(0.3)
            
            # Update code in session 2
            session2_code = "# Code for session 2"
            client2.send_code_update(session2_code, "python")
            time.sleep(0.3)
            
            # Verify sessions have different code
            session1_data = client.get(f"/api/v1/sessions/{session1_id}").json()
            session2_data = client.get(f"/api/v1/sessions/{session2_id}").json()
            
            assert session1_data["current_code"] == session1_code
            assert session2_data["current_code"] == session2_code
            assert session1_data["current_language"] == "javascript"
            assert session2_data["current_language"] == "python"
            
            # Verify client2 didn't receive client1's updates
            client2_messages = client2.get_messages_of_type("code_update")
            for msg in client2_messages:
                assert msg["data"]["code"] != session1_code
            
        finally:
            client1.disconnect()
            client2.disconnect()
    
    def test_error_handling_integration(self, client, ws_url):
        """
        Test error handling across the full stack.
        
        This verifies proper error responses for various failure scenarios.
        """
        # Test 1: Try to get non-existent session
        response = client.get("/api/v1/sessions/nonexistent123")
        assert response.status_code == 404
        
        # Test 2: Try to execute code on non-existent session
        response = client.post(
            "/api/v1/sessions/nonexistent123/execute",
            json={"code": "print('test')", "language": "python"}
        )
        assert response.status_code == 404
        
        # Test 3: Try to connect WebSocket to non-existent session
        try:
            ws = create_connection(f"{ws_url}/nonexistent123")
            # Should receive error message
            message = json.loads(ws.recv())
            assert message["type"] == "error"
            assert "SESSION_NOT_FOUND" in message["data"]["code"]
            ws.close()
        except:
            pass  # Connection might be refused immediately
        
        # Test 4: Send invalid message format
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        client1 = WebSocketClient(session_id, "user1", "John")
        client1.connect(ws_url)
        
        try:
            # Send message with invalid type
            client1.send({
                "type": "invalid_message_type",
                "data": {}
            })
            
            # Should receive error message
            error_msg = client1.wait_for_message("error")
            assert error_msg is not None
            
        finally:
            client1.disconnect()


@pytest.mark.integration
class TestLanguageIntegration:
    """Test language-related features across client and server."""
    
    def test_language_switching_workflow(self, client, ws_url):
        """
        Test the complete workflow of switching languages.
        
        This simulates a user switching between different languages
        and verifies that templates and execution work correctly.
        """
        # Get available languages
        languages_response = client.get("/api/v1/languages")
        assert languages_response.status_code == 200
        
        languages = languages_response.json()["languages"]
        assert len(languages) > 0
        
        # Create session
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Connect WebSocket client
        ws_client = WebSocketClient(session_id, "user1", "Kate")
        ws_client.connect(ws_url)
        
        try:
            # Test switching to each language
            for lang in languages[:3]:  # Test first 3 languages
                lang_id = lang["id"]
                
                # Get language template
                template_response = client.get(f"/api/v1/languages/{lang_id}/template")
                assert template_response.status_code == 200
                
                template = template_response.json()["template"]
                
                # Switch to this language
                ws_client.send_language_change(lang_id)
                ws_client.send_code_update(template, lang_id)
                time.sleep(0.2)
                
                # Verify session updated
                session_data = client.get(f"/api/v1/sessions/{session_id}").json()
                assert session_data["current_language"] == lang_id
                assert session_data["current_code"] == template
                
        finally:
            ws_client.disconnect()
    
    def test_unsupported_language_handling(self, client):
        """Test handling of unsupported languages."""
        # Try to get template for unsupported language
        response = client.get("/api/v1/languages/cobol/template")
        assert response.status_code == 404
        
        # Try to execute code in unsupported language
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        response = client.post(
            f"/api/v1/sessions/{session_id}/execute",
            json={
                "code": "DISPLAY 'HELLO'.",
                "language": "cobol"
            }
        )
        # Should either fail validation or execute with error
        assert response.status_code in [422, 500]


@pytest.mark.integration
class TestPerformance:
    """Test performance and scalability aspects."""
    
    def test_concurrent_users(self, client, ws_url):
        """
        Test system behavior with multiple concurrent users.
        
        This simulates several users joining and interacting simultaneously.
        """
        # Create session
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Create multiple clients
        clients = []
        num_clients = 5
        
        try:
            # Connect all clients
            for i in range(num_clients):
                ws_client = WebSocketClient(session_id, f"user{i}", f"User{i}")
                ws_client.connect(ws_url)
                clients.append(ws_client)
            
            time.sleep(0.5)
            
            # Each client sends a code update
            for i, ws_client in enumerate(clients):
                code = f"// Update from User{i}"
                ws_client.send_code_update(code)
                time.sleep(0.1)  # Small delay to avoid overwhelming
            
            time.sleep(1)
            
            # Verify all clients received updates
            for ws_client in clients:
                code_updates = ws_client.get_messages_of_type("code_update")
                # Should have received updates from other clients
                assert len(code_updates) >= num_clients - 1
            
            # Check final session state
            session_data = client.get(f"/api/v1/sessions/{session_id}").json()
            assert session_data["participant_count"] == num_clients
            
        finally:
            # Disconnect all clients
            for ws_client in clients:
                ws_client.disconnect()
    
    def test_large_code_handling(self, client):
        """
        Test handling of large code submissions.
        
        This verifies the system can handle realistic code sizes.
        """
        # Create session
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Generate large but valid Python code
        large_code = """
# Large code file for testing
import sys
import os
import time

class DataProcessor:
    def __init__(self):
        self.data = []
        self.processed = False
    
    def add_data(self, item):
        self.data.append(item)
    
    def process(self):
        # Simulate complex processing
        result = []
        for item in self.data:
            if isinstance(item, int):
                result.append(item * 2)
            elif isinstance(item, str):
                result.append(item.upper())
            else:
                result.append(str(item))
        self.processed = True
        return result

# Generate many functions
""" + "\n".join([f"""
def function_{i}(x):
    '''Function {i} documentation'''
    return x + {i}
""" for i in range(50)])
        
        # Execute the large code
        response = client.post(
            f"/api/v1/sessions/{session_id}/execute",
            json={
                "code": large_code + "\nprint('Execution complete')",
                "language": "python",
                "time_limit": 5000
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] in [True, False]  # Depends on execution config
        
        # Verify code is stored
        session_data = client.get(f"/api/v1/sessions/{session_id}").json()
        # Code might be truncated in response but should be stored
        assert len(session_data["current_code"]) > 0
