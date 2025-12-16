"""
Tests for Language Endpoints

Tests for fetching supported programming languages.
"""

import pytest


@pytest.mark.unit
def test_list_languages(client, api_base_url):
    """
    Test listing supported languages.
    
    Should return array of language configurations.
    """
    response = client.get(f"{api_base_url}/languages")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "languages" in data
    assert len(data["languages"]) > 0
    
    # Check first language has required fields
    first_lang = data["languages"][0]
    assert "id" in first_lang
    assert "name" in first_lang
    assert "version" in first_lang
    assert "file_extension" in first_lang
    assert "monaco_language" in first_lang
    assert "can_run_in_browser" in first_lang
    assert "default_code" in first_lang
    
    # Should include at least JavaScript and Python
    language_ids = [lang["id"] for lang in data["languages"]]
    assert "javascript" in language_ids
    assert "python" in language_ids


@pytest.mark.unit
def test_get_language_template(client, api_base_url):
    """
    Test fetching template for a specific language.
    
    Should return default code template.
    """
    response = client.get(f"{api_base_url}/languages/python/template")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "language_id" in data
    assert data["language_id"] == "python"
    assert "template" in data
    assert "print" in data["template"]  # Python template should have print


@pytest.mark.unit
def test_get_invalid_language_template(client, api_base_url):
    """
    Test fetching template for unsupported language.
    
    Should return 404 error.
    """
    response = client.get(f"{api_base_url}/languages/cobol/template")
    
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
