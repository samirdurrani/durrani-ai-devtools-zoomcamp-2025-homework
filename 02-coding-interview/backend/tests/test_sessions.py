"""
Tests for Session Management

Tests for creating, fetching, and managing coding sessions.
"""

import pytest
from datetime import datetime


@pytest.mark.unit
def test_create_session(client, api_base_url):
    """
    Test creating a new coding session.
    
    Should return a session with unique ID and join URL.
    """
    # Create session with custom configuration
    response = client.post(
        f"{api_base_url}/sessions",
        json={
            "host_name": "Test Interviewer",
            "session_name": "Python Interview",
            "initial_language": "python",
            "max_participants": 3
        }
    )
    
    assert response.status_code == 201
    
    data = response.json()
    assert "session_id" in data
    assert "join_url" in data
    assert data["host_name"] == "Test Interviewer"
    assert data["status"] == "active"
    assert data["participant_count"] == 0
    
    # Join URL should contain session ID
    assert data["session_id"] in data["join_url"]


@pytest.mark.unit
def test_create_session_with_defaults(client, api_base_url):
    """
    Test creating a session with default values.
    
    Should work even when no configuration is provided.
    """
    response = client.post(f"{api_base_url}/sessions")
    
    assert response.status_code == 201
    
    data = response.json()
    assert "session_id" in data
    assert data["host_name"] == "Anonymous Host"
    assert data["status"] == "active"


@pytest.mark.unit
def test_get_session(client, api_base_url):
    """
    Test fetching session details.
    
    Should return complete session information.
    """
    # First create a session
    create_response = client.post(
        f"{api_base_url}/sessions",
        json={"host_name": "Test Host"}
    )
    session_id = create_response.json()["session_id"]
    
    # Now fetch its details
    response = client.get(f"{api_base_url}/sessions/{session_id}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["session_id"] == session_id
    assert data["host_name"] == "Test Host"
    assert "current_code" in data
    assert "current_language" in data
    assert "participants" in data
    assert "execution_history" in data


@pytest.mark.unit
def test_get_nonexistent_session(client, api_base_url):
    """
    Test fetching a session that doesn't exist.
    
    Should return 404 error.
    """
    response = client.get(f"{api_base_url}/sessions/nonexistent123")
    
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data


@pytest.mark.unit
def test_list_sessions(client, api_base_url):
    """
    Test listing all sessions.
    
    Should return array of sessions.
    """
    # Create a few sessions
    for i in range(3):
        client.post(
            f"{api_base_url}/sessions",
            json={"host_name": f"Host {i}"}
        )
    
    # List sessions
    response = client.get(f"{api_base_url}/sessions")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "sessions" in data
    assert "total" in data
    assert len(data["sessions"]) >= 3
    
    # Sessions should be sorted by creation time (newest first)
    sessions = data["sessions"]
    if len(sessions) > 1:
        first_time = datetime.fromisoformat(sessions[0]["created_at"].replace('Z', '+00:00'))
        second_time = datetime.fromisoformat(sessions[1]["created_at"].replace('Z', '+00:00'))
        assert first_time >= second_time


@pytest.mark.unit
def test_end_session(client, api_base_url):
    """
    Test ending a session.
    
    Should mark session as completed.
    """
    # Create a session
    create_response = client.post(f"{api_base_url}/sessions")
    session_id = create_response.json()["session_id"]
    
    # End the session
    response = client.delete(f"{api_base_url}/sessions/{session_id}")
    
    assert response.status_code == 204  # No content
    
    # Verify session status changed
    get_response = client.get(f"{api_base_url}/sessions/{session_id}")
    assert get_response.json()["status"] == "completed"
