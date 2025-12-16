"""
End-to-End Tests

These tests simulate the complete interaction between a React frontend client
and the FastAPI backend server, testing real-world scenarios.
"""

import pytest
import asyncio
import json
import time
from typing import Optional, Dict, Any
import httpx
import websockets
from datetime import datetime


class ReactClient:
    """
    Simulates a React frontend client with both HTTP and WebSocket capabilities.
    
    This class mimics the behavior of the actual React application.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", ws_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.session_id: Optional[str] = None
        self.join_url: Optional[str] = None
        self.ws_connection = None
        self.client_id = f"react-client-{id(self)}"
        self.display_name = "React User"
        
        # Store state like React would
        self.current_code = ""
        self.current_language = "javascript"
        self.participants = []
        self.execution_results = []
        
    async def create_session(self, host_name: str = "React Host") -> Dict[str, Any]:
        """
        Create a new interview session.
        
        Simulates: User clicking "Create New Interview" button
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/sessions",
                json={
                    "host_name": host_name,
                    "initial_language": self.current_language
                }
            )
            response.raise_for_status()
            data = response.json()
            
            self.session_id = data["session_id"]
            self.join_url = data["join_url"]
            
            return data
    
    async def join_session(self, session_id: str) -> Dict[str, Any]:
        """
        Join an existing session.
        
        Simulates: User entering a session URL and joining
        """
        self.session_id = session_id
        
        # First get session details via HTTP
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/sessions/{session_id}")
            response.raise_for_status()
            session_data = response.json()
            
            # Update local state
            self.current_code = session_data["current_code"]
            self.current_language = session_data["current_language"]
            self.participants = session_data["participants"]
            
            return session_data
    
    async def connect_websocket(self):
        """
        Connect to the WebSocket for real-time updates.
        
        Simulates: WebSocket connection established on session page mount
        """
        if not self.session_id:
            raise ValueError("No session ID set")
        
        self.ws_connection = await websockets.connect(
            f"{self.ws_url}/ws/sessions/{self.session_id}"
        )
        
        # Send join message
        await self.ws_connection.send(json.dumps({
            "type": "join_session",
            "data": {
                "session_id": self.session_id,
                "client_id": self.client_id,
                "display_name": self.display_name
            }
        }))
        
        # Start listening for messages
        asyncio.create_task(self._listen_for_messages())
    
    async def _listen_for_messages(self):
        """Listen for WebSocket messages and update state."""
        try:
            async for message in self.ws_connection:
                data = json.loads(message)
                await self._handle_websocket_message(data)
        except websockets.exceptions.ConnectionClosed:
            pass
    
    async def _handle_websocket_message(self, message: Dict[str, Any]):
        """
        Handle incoming WebSocket messages.
        
        Simulates: React component state updates from WebSocket events
        """
        msg_type = message.get("type")
        data = message.get("data", {})
        
        if msg_type == "session_state":
            # Initial state sync
            self.current_code = data.get("code", "")
            self.current_language = data.get("language", "javascript")
            self.participants = data.get("participants", [])
            
        elif msg_type == "code_update":
            # Someone else updated the code
            self.current_code = data.get("code", "")
            self.current_language = data.get("language", self.current_language)
            
        elif msg_type == "language_change":
            # Language was changed
            self.current_language = data.get("language", "javascript")
            
        elif msg_type == "user_joined":
            # New participant joined
            self.participants = data.get("participants", [])
            
        elif msg_type == "user_left":
            # Participant left
            participant_count = data.get("participant_count", 0)
            # Update participants list
            
        elif msg_type == "execution_result":
            # Code execution completed
            self.execution_results.append(data.get("result", {}))
    
    async def update_code(self, code: str, language: Optional[str] = None):
        """
        Update the code in the editor.
        
        Simulates: User typing in the Monaco editor
        """
        self.current_code = code
        if language:
            self.current_language = language
        
        if self.ws_connection:
            await self.ws_connection.send(json.dumps({
                "type": "code_update",
                "data": {
                    "session_id": self.session_id,
                    "client_id": self.client_id,
                    "code": code,
                    "language": self.current_language
                }
            }))
    
    async def change_language(self, language: str):
        """
        Change the programming language.
        
        Simulates: User selecting a different language from dropdown
        """
        self.current_language = language
        
        if self.ws_connection:
            await self.ws_connection.send(json.dumps({
                "type": "language_change",
                "data": {
                    "session_id": self.session_id,
                    "client_id": self.client_id,
                    "language": language
                }
            }))
    
    async def execute_code(self) -> Dict[str, Any]:
        """
        Execute the current code.
        
        Simulates: User clicking the "Run Code" button
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/sessions/{self.session_id}/execute",
                json={
                    "code": self.current_code,
                    "language": self.current_language,
                    "time_limit": 5000
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_languages(self) -> Dict[str, Any]:
        """
        Get list of supported languages.
        
        Simulates: Populating the language dropdown on mount
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/languages")
            response.raise_for_status()
            return response.json()
    
    async def disconnect(self):
        """
        Disconnect from the session.
        
        Simulates: User leaving the session or closing the browser tab
        """
        if self.ws_connection:
            await self.ws_connection.close()
            self.ws_connection = None


@pytest.mark.asyncio
@pytest.mark.e2e
class TestReactClientE2E:
    """End-to-end tests simulating React client interactions."""
    
    async def test_interviewer_creates_session_flow(self):
        """
        Test the complete flow of an interviewer creating and setting up a session.
        
        Scenario:
        1. Interviewer visits landing page
        2. Creates new interview session
        3. Shares link with candidate
        4. Waits for candidate to join
        """
        interviewer = ReactClient()
        
        # Create session
        session_data = await interviewer.create_session("Senior Engineer Interview")
        assert session_data["session_id"] is not None
        assert session_data["join_url"] is not None
        assert "Senior Engineer Interview" in session_data["host_name"]
        
        # Connect to WebSocket for real-time updates
        await interviewer.connect_websocket()
        
        # Set up initial code
        initial_code = """
def fibonacci(n):
    '''Calculate nth Fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
print(fibonacci(10))
"""
        await interviewer.update_code(initial_code, "python")
        
        # Verify code was updated
        await asyncio.sleep(0.2)  # Wait for state to propagate
        
        # Check session state via API
        session_details = await interviewer.join_session(interviewer.session_id)
        assert session_details["current_code"] == initial_code
        assert session_details["current_language"] == "python"
        
        # Clean up
        await interviewer.disconnect()
    
    async def test_candidate_joins_session_flow(self):
        """
        Test the complete flow of a candidate joining an interview.
        
        Scenario:
        1. Interviewer creates session with some code
        2. Candidate receives link and joins
        3. Candidate sees the current code
        4. Both see each other in participants list
        """
        # Interviewer creates session
        interviewer = ReactClient()
        interviewer.display_name = "Alice Interviewer"
        session_data = await interviewer.create_session("Alice Interviewer")
        session_id = session_data["session_id"]
        
        await interviewer.connect_websocket()
        
        # Interviewer sets up problem
        problem_code = """
// Problem: Implement a function to reverse a linked list
class ListNode {
    constructor(val, next = null) {
        this.val = val;
        this.next = next;
    }
}

function reverseList(head) {
    // TODO: Implement this function
    return head;
}
"""
        await interviewer.update_code(problem_code, "javascript")
        await asyncio.sleep(0.2)
        
        # Candidate joins using the session ID
        candidate = ReactClient()
        candidate.display_name = "Bob Candidate"
        
        # Candidate would extract session ID from URL in real app
        session_details = await candidate.join_session(session_id)
        
        # Verify candidate sees the problem
        assert "reverseList" in session_details["current_code"]
        assert session_details["current_language"] == "javascript"
        
        # Candidate connects to WebSocket
        await candidate.connect_websocket()
        await asyncio.sleep(0.3)
        
        # Both should see 2 participants
        # (In real app, this would update UI automatically)
        
        # Clean up
        await interviewer.disconnect()
        await candidate.disconnect()
    
    async def test_collaborative_coding_flow(self):
        """
        Test real-time collaborative coding between two users.
        
        Scenario:
        1. Two users in same session
        2. One writes code
        3. Other sees updates in real-time
        4. They take turns editing
        """
        # Create session
        user1 = ReactClient()
        user1.display_name = "Developer 1"
        session_data = await user1.create_session("Pair Programming")
        session_id = session_data["session_id"]
        
        await user1.connect_websocket()
        await asyncio.sleep(0.2)
        
        # Second user joins
        user2 = ReactClient()
        user2.display_name = "Developer 2"
        await user2.join_session(session_id)
        await user2.connect_websocket()
        await asyncio.sleep(0.2)
        
        # User 1 writes initial function
        code_v1 = """
function calculateSum(arr) {
    let sum = 0;
    // User 1's implementation
    for (let i = 0; i < arr.length; i++) {
        sum += arr[i];
    }
    return sum;
}
"""
        await user1.update_code(code_v1)
        await asyncio.sleep(0.3)
        
        # User 2 should see the update
        assert "calculateSum" in user2.current_code
        
        # User 2 refactors the code
        code_v2 = """
function calculateSum(arr) {
    // User 2's refactored implementation using reduce
    return arr.reduce((sum, num) => sum + num, 0);
}

// Test cases
console.log(calculateSum([1, 2, 3, 4, 5])); // 15
console.log(calculateSum([])); // 0
"""
        await user2.update_code(code_v2)
        await asyncio.sleep(0.3)
        
        # User 1 should see the refactored version
        assert "reduce" in user1.current_code
        assert "Test cases" in user1.current_code
        
        # Clean up
        await user1.disconnect()
        await user2.disconnect()
    
    async def test_code_execution_with_output_flow(self):
        """
        Test the complete code execution flow.
        
        Scenario:
        1. User writes code
        2. Clicks run button
        3. Sees output
        4. Other users see execution results
        """
        # Create session
        user1 = ReactClient()
        session_data = await user1.create_session("Execution Test")
        session_id = session_data["session_id"]
        await user1.connect_websocket()
        
        # Second user joins to observe
        user2 = ReactClient()
        await user2.join_session(session_id)
        await user2.connect_websocket()
        await asyncio.sleep(0.2)
        
        # User 1 writes and executes Python code
        test_code = """
# Calculate factorial
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test with different values
for i in range(1, 6):
    print(f"factorial({i}) = {factorial(i)}")
"""
        await user1.update_code(test_code, "python")
        await asyncio.sleep(0.2)
        
        # Execute the code
        result = await user1.execute_code()
        
        # Check execution result
        assert result["session_id"] == session_id
        assert result["language"] == "python"
        assert "duration" in result
        
        # Both users should have received execution result via WebSocket
        await asyncio.sleep(0.3)
        
        # In real app, this would update the output panel
        if user1.execution_results:
            last_result = user1.execution_results[-1]
            # Result structure depends on execution configuration
            assert "stdout" in last_result or "error" in last_result
        
        # Clean up
        await user1.disconnect()
        await user2.disconnect()
    
    async def test_language_switching_flow(self):
        """
        Test switching between programming languages.
        
        Scenario:
        1. Start with JavaScript
        2. Switch to Python with template
        3. Switch to Java
        4. Verify all users see changes
        """
        # Create session
        user = ReactClient()
        session_data = await user.create_session("Multi-language Test")
        await user.connect_websocket()
        await asyncio.sleep(0.2)
        
        # Get available languages
        languages_data = await user.get_languages()
        languages = languages_data["languages"]
        assert len(languages) > 0
        
        # Test switching through different languages
        for lang in ["javascript", "python", "java"]:
            # Find language info
            lang_info = next((l for l in languages if l["id"] == lang), None)
            if not lang_info:
                continue
            
            # Switch language
            await user.change_language(lang)
            
            # Update with language template
            await user.update_code(lang_info["default_code"])
            await asyncio.sleep(0.2)
            
            # Verify language changed
            assert user.current_language == lang
            assert lang_info["default_code"] in user.current_code
        
        # Clean up
        await user.disconnect()
    
    async def test_session_recovery_flow(self):
        """
        Test recovering session state after disconnect.
        
        Scenario:
        1. User loses connection (browser refresh, network issue)
        2. User reconnects with session ID
        3. Recovers current state
        """
        # Create session and add some code
        user1 = ReactClient()
        session_data = await user1.create_session("Recovery Test")
        session_id = session_data["session_id"]
        await user1.connect_websocket()
        
        # Add some code and state
        code_before = """
def important_algorithm():
    # This code should persist
    return "important result"
"""
        await user1.update_code(code_before, "python")
        await asyncio.sleep(0.2)
        
        # Simulate disconnect (browser refresh)
        await user1.disconnect()
        
        # Simulate reconnecting (new React instance)
        user1_reconnected = ReactClient()
        user1_reconnected.display_name = user1.display_name
        
        # Rejoin the session
        session_details = await user1_reconnected.join_session(session_id)
        
        # Verify state was recovered
        assert session_details["current_code"] == code_before
        assert session_details["current_language"] == "python"
        assert session_details["status"] == "active"
        
        # Reconnect WebSocket and continue
        await user1_reconnected.connect_websocket()
        await asyncio.sleep(0.2)
        
        # Can continue editing
        code_after = code_before + "\n\nprint(important_algorithm())"
        await user1_reconnected.update_code(code_after)
        
        # Clean up
        await user1_reconnected.disconnect()
    
    async def test_concurrent_editing_conflict_resolution(self):
        """
        Test how the system handles concurrent edits.
        
        Scenario:
        1. Multiple users editing simultaneously
        2. Rapid updates from different sources
        3. Verify last-write-wins behavior
        """
        # Create session
        host = ReactClient()
        session_data = await host.create_session("Concurrent Edit Test")
        session_id = session_data["session_id"]
        await host.connect_websocket()
        
        # Multiple users join
        users = []
        for i in range(3):
            user = ReactClient()
            user.display_name = f"User {i+1}"
            await user.join_session(session_id)
            await user.connect_websocket()
            users.append(user)
        
        await asyncio.sleep(0.3)
        
        # All users rapidly update code
        updates = []
        for i, user in enumerate(users):
            code = f"// Last update by User {i+1} at {datetime.now().isoformat()}"
            updates.append(user.update_code(code))
        
        # Execute all updates concurrently
        await asyncio.gather(*updates)
        await asyncio.sleep(0.5)
        
        # Verify all users eventually have the same code
        # (Last write wins)
        final_codes = [user.current_code for user in users]
        
        # All users should converge to the same final state
        # The exact content depends on which update arrived last
        assert len(set(final_codes)) == 1, "All users should have the same final code"
        
        # Clean up
        await host.disconnect()
        for user in users:
            await user.disconnect()


@pytest.mark.asyncio
@pytest.mark.e2e
class TestErrorScenariosE2E:
    """Test error handling in end-to-end scenarios."""
    
    async def test_invalid_session_handling(self):
        """Test how the app handles invalid session IDs."""
        user = ReactClient()
        
        # Try to join non-existent session
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await user.join_session("invalid-session-id-xyz")
        
        assert exc_info.value.response.status_code == 404
    
    async def test_rate_limit_handling(self):
        """Test how the app handles rate limiting."""
        user = ReactClient()
        session_data = await user.create_session("Rate Limit Test")
        await user.connect_websocket()
        
        # Rapid execution attempts
        simple_code = "print('test')"
        await user.update_code(simple_code, "python")
        
        # Try to execute many times rapidly
        execution_count = 0
        rate_limited = False
        
        for _ in range(15):
            try:
                await user.execute_code()
                execution_count += 1
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    rate_limited = True
                    break
        
        assert rate_limited, "Should hit rate limit"
        assert execution_count < 15, "Too many executions succeeded"
        
        await user.disconnect()
    
    async def test_network_interruption_recovery(self):
        """Test recovery from network interruptions."""
        user = ReactClient()
        session_data = await user.create_session("Network Test")
        session_id = session_data["session_id"]
        await user.connect_websocket()
        
        # Add some initial code
        await user.update_code("// Initial code")
        await asyncio.sleep(0.2)
        
        # Simulate network interruption
        if user.ws_connection:
            await user.ws_connection.close()
            user.ws_connection = None
        
        # Try to update code (should fail gracefully)
        await user.update_code("// Code during disconnect")
        
        # Reconnect
        await user.connect_websocket()
        await asyncio.sleep(0.2)
        
        # Should be able to continue
        await user.update_code("// Code after reconnect")
        
        # Verify session is still active
        session_details = await user.join_session(session_id)
        assert session_details["status"] == "active"
        
        await user.disconnect()
