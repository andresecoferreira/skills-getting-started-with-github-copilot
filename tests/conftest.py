"""
Shared fixtures for FastAPI tests

This module provides fixtures used across all test files, following the
Arrange-Act-Assert (AAA) testing pattern:
- Arrange: Setup test data and state (fixtures provide this)
- Act: Execute the code being tested (in individual test functions)
- Assert: Verify the expected outcomes (in individual test functions)
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities for reset
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice drills and compete in inter-school basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu", "lucas@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Develop swimming techniques and participate in swim meets",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media art techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "charlotte@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting, improvisation, and theater production performances",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 24,
        "participants": ["ethan@mergington.edu", "amelia@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Team-based science competitions covering biology, chemistry, and physics",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["william@mergington.edu", "harper@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking through competitive debates",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["benjamin@mergington.edu", "evelyn@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient for making API requests in tests.
    
    This fixture is used in the Arrange phase of AAA pattern to setup
    the test client before making requests.
    
    Returns:
        TestClient: A client for testing FastAPI endpoints
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Automatically resets the activities database after each test.
    
    This fixture uses autouse=True to run after every test, ensuring test isolation.
    It prevents test pollution by restoring the initial state of the activities database.
    
    Critical for maintaining test independence in the AAA pattern:
    - Each test Arranges data with a clean slate
    - Acts on the endpoint
    - Asserts results without interference from previous tests
    
    Yields:
        None: Control to the test, then resets activities after test completes
    """
    yield
    # Reset activities to initial state after each test (teardown phase)
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def sample_email():
    """
    Provides a consistent test email address for signup tests.
    
    Returns:
        str: A test email address
    """
    return "test.student@mergington.edu"


@pytest.fixture
def sample_activity():
    """
    Provides a consistent test activity name.
    
    Returns:
        str: A valid activity name from the database
    """
    return "Chess Club"


@pytest.fixture
def full_activity_name():
    """
    Provides an activity name for testing max_participants scenarios.
    Creates a scenario where we can test the activity becoming full.
    
    Returns:
        str: Activity name with fewer initial participants
    """
    return "Debate Team"  # Has max_participants: 14
