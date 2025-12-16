"""
Tests for Code Execution

Tests for safely executing code with resource limits.
"""

import pytest


@pytest.mark.unit
def test_execute_simple_code(client, api_base_url):
    """
    Test executing simple code.
    
    Should return output and execution metadata.
    """
    # First create a session
    create_response = client.post(f"{api_base_url}/sessions")
    session_id = create_response.json()["session_id"]
    
    # Execute code
    response = client.post(
        f"{api_base_url}/sessions/{session_id}/execute",
        json={
            "code": "print('Hello, Test!')",
            "language": "python",
            "stdin": "",
            "time_limit": 5000
        }
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["session_id"] == session_id
    assert data["language"] == "python"
    assert "stdout" in data
    assert "stderr" in data
    assert "exit_code" in data
    assert "duration" in data
    assert "success" in data
    assert "timestamp" in data


@pytest.mark.unit
def test_execute_with_invalid_session(client, api_base_url):
    """
    Test executing code with invalid session ID.
    
    Should return 404 error.
    """
    response = client.post(
        f"{api_base_url}/sessions/invalid123/execute",
        json={
            "code": "print('test')",
            "language": "python"
        }
    )
    
    assert response.status_code == 404


@pytest.mark.unit
def test_execute_empty_code(client, api_base_url):
    """
    Test executing empty code.
    
    Should return validation error.
    """
    # Create a session first
    create_response = client.post(f"{api_base_url}/sessions")
    session_id = create_response.json()["session_id"]
    
    # Try to execute empty code
    response = client.post(
        f"{api_base_url}/sessions/{session_id}/execute",
        json={
            "code": "   ",  # Just whitespace
            "language": "python"
        }
    )
    
    assert response.status_code == 422  # Validation error
    
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_rate_limiting(client, api_base_url):
    """
    Test that rate limiting works for code execution.
    
    Should reject requests after limit is exceeded.
    
    Note: This is marked as integration test as it may be slow.
    """
    # Create a session
    create_response = client.post(f"{api_base_url}/sessions")
    session_id = create_response.json()["session_id"]
    
    # Make many execution requests quickly
    # The limit is configured in settings (default 10/minute)
    success_count = 0
    for i in range(15):
        response = client.post(
            f"{api_base_url}/sessions/{session_id}/execute",
            json={
                "code": f"print({i})",
                "language": "python"
            }
        )
        
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            # Rate limit exceeded
            break
    
    # We should hit the rate limit before executing all 15
    assert success_count < 15
