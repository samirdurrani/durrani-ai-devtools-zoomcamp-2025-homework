"""
Tests for Health Check Endpoint

Simple tests to verify the API is running correctly.
"""

import pytest


@pytest.mark.unit
def test_health_check(client, api_base_url):
    """
    Test that the health check endpoint returns correct status.
    
    This is a basic test to ensure the API is responsive.
    """
    response = client.get(f"{api_base_url}/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "services" in data


@pytest.mark.unit
def test_root_endpoint(client):
    """
    Test the root endpoint provides API information.
    """
    response = client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "documentation" in data
    assert "endpoints" in data
