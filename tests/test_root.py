"""
Tests for root endpoint

Following the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Setup test client (via fixture)
- Act: Make GET request to root endpoint
- Assert: Verify redirect behavior
"""

import pytest


def test_root_redirects_to_static_index(client):
    """
    Test that GET / redirects to /static/index.html
    
    AAA Pattern:
    - Arrange: Client fixture provides TestClient
    - Act: Make GET request to root
    - Assert: Verify redirect response
    """
    # Arrange
    # (client fixture is automatically provided)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_root_redirect_status_code(client):
    """
    Test that root endpoint returns proper redirect status code
    
    AAA Pattern:
    - Arrange: Client fixture
    - Act: Request root endpoint
    - Assert: Status code is 307 (Temporary Redirect)
    """
    # Arrange
    # (client fixture provided)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307


def test_root_redirect_target_is_correct(client):
    """
    Test that redirect target URL is exactly /static/index.html
    
    AAA Pattern:
    - Arrange: Client fixture
    - Act: Request root endpoint
    - Assert: Location header points to correct URL
    """
    # Arrange
    # (client fixture provided)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert "location" in response.headers
    assert response.headers["location"] == "/static/index.html"
