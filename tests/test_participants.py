"""
Tests for participant management endpoints (signup and delete)

Following the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Setup test data and state
- Act: Execute API request
- Assert: Verify expected outcomes
"""

import pytest
from urllib.parse import quote


# ============================================================================
# SIGNUP ENDPOINT TESTS - POST /activities/{activity_name}/signup
# ============================================================================

def test_signup_successful_with_valid_data(client, sample_activity, sample_email):
    """
    Test successful signup with valid activity and email
    
    AAA Pattern:
    - Arrange: Valid activity name and email
    - Act: POST signup request
    - Assert: 200 status, success message, participant added
    """
    # Arrange
    activity_name = sample_activity
    email = sample_email
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"]
    initial_count = len(initial_participants)
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify participant was added
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    assert len(updated_participants) == initial_count + 1
    assert email in updated_participants


def test_signup_participant_added_to_list(client, sample_activity):
    """
    Test that participant is actually added to the participants list
    
    AAA Pattern:
    - Arrange: Activity and new email
    - Act: Signup for activity
    - Assert: Email appears in participants list
    """
    # Arrange
    activity_name = sample_activity
    new_email = "new.student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(new_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert new_email in participants


def test_signup_returns_404_for_nonexistent_activity(client, sample_email):
    """
    Test that signup returns 404 when activity doesn't exist
    
    AAA Pattern:
    - Arrange: Invalid activity name
    - Act: Attempt signup
    - Assert: 404 error with appropriate message
    """
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = sample_email
    
    # Act
    response = client.post(
        f"/activities/{quote(invalid_activity)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_signup(client, sample_activity):
    """
    Test that signing up twice returns 400 error
    
    AAA Pattern:
    - Arrange: Signup once successfully
    - Act: Attempt duplicate signup
    - Assert: 400 error with duplicate message
    """
    # Arrange
    activity_name = sample_activity
    email = "duplicate.test@mergington.edu"
    
    # First signup (successful)
    first_response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    assert first_response.status_code == 200
    
    # Act - Second signup (should fail)
    second_response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_400_when_activity_is_full(client, full_activity_name):
    """
    Test that signup returns 400 when activity reaches max_participants
    
    AAA Pattern:
    - Arrange: Fill activity to max capacity
    - Act: Attempt one more signup
    - Assert: 400 error with "Activity is full" message
    """
    # Arrange
    activity_name = full_activity_name
    
    # Get current state
    activities_response = client.get("/activities")
    activity_data = activities_response.json()[activity_name]
    max_participants = activity_data["max_participants"]
    current_participants = len(activity_data["participants"])
    spots_remaining = max_participants - current_participants
    
    # Fill remaining spots
    for i in range(spots_remaining):
        email = f"filler{i}@mergington.edu"
        response = client.post(
            f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
        )
        assert response.status_code == 200
    
    # Act - Try to add one more (should fail)
    overflow_email = "overflow@mergington.edu"
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(overflow_email)}"
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_with_special_characters_in_email(client, sample_activity):
    """
    Test signup with special characters in email address
    
    AAA Pattern:
    - Arrange: Email with dots, hyphens, underscores
    - Act: Signup with special char email
    - Assert: Successful signup
    """
    # Arrange
    activity_name = sample_activity
    special_email = "first.last-test_123@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(special_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert special_email in response.json()["message"]


def test_signup_with_spaces_in_activity_name(client):
    """
    Test signup with URL-encoded spaces in activity name
    
    AAA Pattern:
    - Arrange: Activity name with spaces (normal case)
    - Act: Signup with URL encoding
    - Assert: Successful signup
    """
    # Arrange
    activity_name = "Chess Club"  # Has space
    email = "space.test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()["message"]


def test_signup_case_sensitive_activity_name(client, sample_email):
    """
    Test that activity names are case-sensitive
    
    AAA Pattern:
    - Arrange: Activity name with wrong case
    - Act: Attempt signup with wrong case
    - Assert: 404 error (case doesn't match)
    """
    # Arrange
    wrong_case_activity = "chess club"  # Should be "Chess Club"
    email = sample_email
    
    # Act
    response = client.post(
        f"/activities/{quote(wrong_case_activity)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_multiple_students_same_activity(client, sample_activity):
    """
    Test that multiple different students can signup for same activity
    
    AAA Pattern:
    - Arrange: Multiple unique email addresses
    - Act: Signup each student
    - Assert: All successfully added
    """
    # Arrange
    activity_name = sample_activity
    emails = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])
    
    # Act
    for email in emails:
        response = client.post(
            f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
        )
        # Assert each signup succeeds
        assert response.status_code == 200
    
    # Assert
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    assert len(final_participants) == initial_count + len(emails)
    for email in emails:
        assert email in final_participants


def test_signup_does_not_affect_other_activities(client, sample_activity):
    """
    Test that signing up for one activity doesn't affect others
    
    AAA Pattern:
    - Arrange: Get initial state of all activities
    - Act: Signup for one specific activity
    - Assert: Only that activity's participants changed
    """
    # Arrange
    activity_name = sample_activity
    email = "isolation.test@mergington.edu"
    
    initial_response = client.get("/activities")
    initial_activities = initial_response.json()
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    final_response = client.get("/activities")
    final_activities = final_response.json()
    
    # Check that only the target activity changed
    for name, activity_data in final_activities.items():
        if name == activity_name:
            # This one should have one more participant
            assert len(activity_data["participants"]) == \
                   len(initial_activities[name]["participants"]) + 1
        else:
            # All others should be unchanged
            assert activity_data["participants"] == initial_activities[name]["participants"]


def test_signup_participant_count_increases(client, sample_activity):
    """
    Test that participant count increases after signup
    
    AAA Pattern:
    - Arrange: Get initial participant count
    - Act: Signup new participant
    - Assert: Count increased by exactly 1
    """
    # Arrange
    activity_name = sample_activity
    email = "count.test@mergington.edu"
    
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity_name]["participants"])
    assert final_count == initial_count + 1


def test_signup_with_plus_sign_in_email(client, sample_activity):
    """
    Test signup with plus sign in email (common email alias pattern)
    
    AAA Pattern:
    - Arrange: Email with plus sign
    - Act: Signup
    - Assert: Successful signup with proper encoding
    """
    # Arrange
    activity_name = sample_activity
    email_with_plus = "student+test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email_with_plus)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    # Verify it was added correctly
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email_with_plus in participants


def test_signup_with_long_email_address(client, sample_activity):
    """
    Test signup with very long but valid email address
    
    AAA Pattern:
    - Arrange: Long email address
    - Act: Signup
    - Assert: Successful signup
    """
    # Arrange
    activity_name = sample_activity
    long_email = "a.very.long.email.address.with.multiple.dots@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(long_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert long_email in response.json()["message"]


# ============================================================================
# DELETE PARTICIPANT ENDPOINT TESTS - DELETE /activities/{activity_name}/participants/{email}
# ============================================================================

def test_delete_participant_successful(client, sample_activity):
    """
    Test successful removal of an existing participant
    
    AAA Pattern:
    - Arrange: Add a participant first
    - Act: Delete that participant
    - Assert: 200 status, success message, participant removed
    """
    # Arrange
    activity_name = sample_activity
    email = "to.be.removed@mergington.edu"
    
    # Add participant first
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    
    # Verify participant was added
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"]
    assert email in initial_participants
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    
    # Verify participant was removed
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    assert email not in final_participants


def test_delete_participant_actually_removed_from_list(client, sample_activity):
    """
    Test that participant is actually removed from the participants list
    
    AAA Pattern:
    - Arrange: Add participant
    - Act: Delete participant
    - Assert: Participant no longer in list
    """
    # Arrange
    activity_name = sample_activity
    email = "remove.me@mergington.edu"
    
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_delete_returns_404_for_nonexistent_activity(client, sample_email):
    """
    Test that delete returns 404 when activity doesn't exist
    
    AAA Pattern:
    - Arrange: Invalid activity name
    - Act: Attempt to delete participant
    - Assert: 404 error
    """
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = sample_email
    
    # Act
    response = client.delete(
        f"/activities/{quote(invalid_activity)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_returns_404_for_nonexistent_participant(client, sample_activity):
    """
    Test that delete returns 404 when participant not in activity
    
    AAA Pattern:
    - Arrange: Valid activity, non-existent participant email
    - Act: Attempt to delete
    - Assert: 404 error with appropriate message
    """
    # Arrange
    activity_name = sample_activity
    nonexistent_email = "not.signed.up@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(nonexistent_email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_delete_with_special_characters_in_email(client, sample_activity):
    """
    Test delete with special characters in email address
    
    AAA Pattern:
    - Arrange: Signup with special char email
    - Act: Delete that email
    - Assert: Successful deletion
    """
    # Arrange
    activity_name = sample_activity
    special_email = "special.char-test_123@mergington.edu"
    
    # Add participant
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(special_email)}")
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(special_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert special_email in response.json()["message"]


def test_delete_with_spaces_in_activity_name(client):
    """
    Test delete with URL-encoded spaces in activity name
    
    AAA Pattern:
    - Arrange: Activity with spaces, add participant
    - Act: Delete with proper URL encoding
    - Assert: Successful deletion
    """
    # Arrange
    activity_name = "Programming Class"  # Has space
    email = "space.delete.test@mergington.edu"
    
    # Add participant
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert activity_name in response.json()["message"]


def test_delete_case_sensitive_activity_name(client, sample_email):
    """
    Test that activity names are case-sensitive for delete
    
    AAA Pattern:
    - Arrange: Activity name with wrong case
    - Act: Attempt delete with wrong case
    - Assert: 404 error
    """
    # Arrange
    wrong_case_activity = "chess club"  # Should be "Chess Club"
    email = sample_email
    
    # Act
    response = client.delete(
        f"/activities/{quote(wrong_case_activity)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_count_decreases(client, sample_activity):
    """
    Test that participant count decreases after deletion
    
    AAA Pattern:
    - Arrange: Add participant, get initial count
    - Act: Delete participant
    - Assert: Count decreased by exactly 1
    """
    # Arrange
    activity_name = sample_activity
    email = "count.decrease@mergington.edu"
    
    # Add participant
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    
    after_signup_response = client.get("/activities")
    count_after_signup = len(after_signup_response.json()[activity_name]["participants"])
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity_name]["participants"])
    assert final_count == count_after_signup - 1


def test_delete_does_not_affect_other_participants(client, sample_activity):
    """
    Test that deleting one participant doesn't affect others
    
    AAA Pattern:
    - Arrange: Add multiple participants
    - Act: Delete one participant
    - Assert: Others remain unchanged
    """
    # Arrange
    activity_name = sample_activity
    emails = [
        "keep1@mergington.edu",
        "keep2@mergington.edu",
        "delete.this@mergington.edu"
    ]
    
    # Add all participants
    for email in emails:
        client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    
    email_to_delete = "delete.this@mergington.edu"
    emails_to_keep = ["keep1@mergington.edu", "keep2@mergington.edu"]
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email_to_delete)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    
    assert email_to_delete not in final_participants
    for email in emails_to_keep:
        assert email in final_participants


def test_delete_does_not_affect_other_activities(client, sample_activity):
    """
    Test that deleting from one activity doesn't affect others
    
    AAA Pattern:
    - Arrange: Get initial state of all activities
    - Act: Delete participant from one activity
    - Assert: Other activities unchanged
    """
    # Arrange
    activity_name = sample_activity
    email = "delete.isolation@mergington.edu"
    
    # Add participant
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    
    initial_response = client.get("/activities")
    initial_activities = initial_response.json()
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    final_response = client.get("/activities")
    final_activities = final_response.json()
    
    # Check that other activities are unchanged
    for name, activity_data in final_activities.items():
        if name != activity_name:
            assert activity_data["participants"] == initial_activities[name]["participants"]


def test_delete_and_readd_participant(client, sample_activity):
    """
    Test that a participant can be re-added after deletion
    
    AAA Pattern:
    - Arrange: Add participant, then delete
    - Act: Re-add the same participant
    - Assert: Successful re-addition
    """
    # Arrange
    activity_name = sample_activity
    email = "readd.test@mergington.edu"
    
    # Add participant
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    
    # Delete participant
    delete_response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    assert delete_response.status_code == 200
    
    # Act - Re-add participant
    readd_response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert readd_response.status_code == 200
    
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    assert email in final_participants


def test_delete_last_participant_from_activity(client):
    """
    Test deleting when participant is the last one in activity
    
    AAA Pattern:
    - Arrange: Create activity state with only one participant
    - Act: Delete that participant
    - Assert: Activity has empty participants list
    """
    # Arrange
    # Use an activity and remove all but one participant, then add our test participant
    activity_name = "Chess Club"
    test_email = "last.one@mergington.edu"
    
    # Get current participants
    initial_response = client.get("/activities")
    current_participants = initial_response.json()[activity_name]["participants"].copy()
    
    # Remove all current participants
    for participant in current_participants:
        client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(participant)}"
        )
    
    # Add our test participant (now the only one)
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(test_email)}")
    
    # Verify they're the only one
    check_response = client.get("/activities")
    participants_before = check_response.json()[activity_name]["participants"]
    assert len(participants_before) == 1
    assert test_email in participants_before
    
    # Act - Delete the last participant
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(test_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    assert len(final_participants) == 0
    assert isinstance(final_participants, list)


def test_delete_with_plus_sign_in_email(client, sample_activity):
    """
    Test delete with plus sign in email (URL encoding test)
    
    AAA Pattern:
    - Arrange: Add participant with plus in email
    - Act: Delete with proper encoding
    - Assert: Successful deletion
    """
    # Arrange
    activity_name = sample_activity
    email_with_plus = "student+delete@mergington.edu"
    
    # Add participant
    client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email_with_plus)}")
    
    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email_with_plus)}"
    )
    
    # Assert
    assert response.status_code == 200
    
    # Verify removal
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email_with_plus not in participants
