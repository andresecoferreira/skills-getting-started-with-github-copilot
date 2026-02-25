"""
Tests for GET /activities endpoint

Following the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Setup test client and expected data
- Act: Make GET request to /activities
- Assert: Verify response structure and data
"""

import pytest


def test_get_activities_returns_200(client):
    """
    Test that GET /activities returns 200 OK status
    
    AAA Pattern:
    - Arrange: Client fixture
    - Act: GET /activities
    - Assert: Status code is 200
    """
    # Arrange
    # (client fixture provided)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200


def test_get_activities_returns_all_nine_activities(client):
    """
    Test that response contains all 9 activities
    
    AAA Pattern:
    - Arrange: Client and expected activity count
    - Act: GET /activities
    - Assert: Response has exactly 9 activities
    """
    # Arrange
    expected_count = 9
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert len(data) == expected_count


def test_get_activities_contains_expected_activity_names(client):
    """
    Test that response contains all expected activity names
    
    AAA Pattern:
    - Arrange: List of expected activity names
    - Act: GET /activities
    - Assert: All expected names present
    """
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Swimming Club",
        "Art Studio",
        "Drama Club",
        "Science Olympiad",
        "Debate Team"
    ]
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity_name in expected_activities:
        assert activity_name in data


def test_get_activities_each_has_required_fields(client):
    """
    Test that each activity has all required fields
    
    AAA Pattern:
    - Arrange: Define required fields
    - Act: GET /activities
    - Assert: Each activity has all required fields
    """
    # Arrange
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        for field in required_fields:
            assert field in activity_data, f"{activity_name} missing {field}"


def test_get_activities_participants_is_list(client):
    """
    Test that participants field is a list for all activities
    
    AAA Pattern:
    - Arrange: Client
    - Act: GET /activities
    - Assert: participants is a list type
    """
    # Arrange
    # (client fixture provided)
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        assert isinstance(activity_data["participants"], list), \
            f"{activity_name} participants is not a list"


def test_get_activities_max_participants_is_integer(client):
    """
    Test that max_participants field is an integer for all activities
    
    AAA Pattern:
    - Arrange: Client
    - Act: GET /activities
    - Assert: max_participants is int type
    """
    # Arrange
    # (client fixture provided)
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        assert isinstance(activity_data["max_participants"], int), \
            f"{activity_name} max_participants is not an integer"


def test_get_activities_chess_club_data_integrity(client):
    """
    Test specific activity data integrity using Chess Club
    
    AAA Pattern:
    - Arrange: Expected Chess Club data
    - Act: GET /activities
    - Assert: Chess Club data matches expected values
    """
    # Arrange
    expected_chess_data = {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12
    }
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert "Chess Club" in data
    chess_club = data["Chess Club"]
    assert chess_club["description"] == expected_chess_data["description"]
    assert chess_club["schedule"] == expected_chess_data["schedule"]
    assert chess_club["max_participants"] == expected_chess_data["max_participants"]
    assert len(chess_club["participants"]) == 2  # Initial state has 2 participants


def test_get_activities_returns_json(client):
    """
    Test that response is valid JSON
    
    AAA Pattern:
    - Arrange: Client
    - Act: GET /activities and parse JSON
    - Assert: JSON parsing succeeds and returns dict
    """
    # Arrange
    # (client fixture provided)
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert isinstance(data, dict)
    assert response.headers["content-type"] == "application/json"
