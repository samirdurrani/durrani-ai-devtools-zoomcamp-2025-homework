"""
Test Fixtures

Shared test fixtures and configuration for all tests.
Fixtures are reusable pieces of test setup that pytest can inject into tests.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Generator

# Import the app and services
from app.main import app
from app.services.session_manager import SessionManager


@pytest.fixture
def client() -> Generator:
    """
    Create a test client for the FastAPI app.
    
    This fixture provides a client that can make HTTP requests
    to the API without running an actual server.
    
    Yields:
        TestClient: Client for making test requests
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def session_manager() -> SessionManager:
    """
    Get a fresh session manager for testing.
    
    This resets the session manager state between tests
    to ensure tests don't interfere with each other.
    
    Returns:
        SessionManager: Clean session manager instance
    """
    # Get the singleton instance
    manager = SessionManager()
    
    # Clear any existing sessions
    manager._sessions.clear()
    manager._execution_counts.clear()
    
    return manager


@pytest.fixture
def sample_session(session_manager):
    """
    Create a sample session for testing.
    
    Args:
        session_manager: Session manager fixture
        
    Returns:
        Session: A test session
    """
    session = session_manager.create_session(
        host_name="Test Host",
        session_name="Test Session",
        initial_language="python",
        max_participants=5
    )
    return session


@pytest.fixture
def api_base_url():
    """
    Get the base URL for API endpoints.
    
    Returns:
        str: Base API URL
    """
    return "/api/v1"
