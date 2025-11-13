"""
Tests for the FastAPI endpoints of the High School Management System.
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        # Since it's a redirect, we should check the response contains the HTML
        assert "Mergington High School" in response.text


class TestActivitiesEndpoint:
    """Tests for the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have the expected activities
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Basketball Team", "Track and Field", "Art Club",
            "Drama Club", "Debate Team", "Science Olympiad"
        ]
        
        for activity in expected_activities:
            assert activity in data
            
        # Check structure of activity data
        for activity_name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)
            assert isinstance(details["max_participants"], int)
    
    def test_activities_have_valid_structure(self, client):
        """Test that each activity has the required structure."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, details in data.items():
            assert len(details["description"]) > 0
            assert len(details["schedule"]) > 0
            assert details["max_participants"] > 0
            assert len(details["participants"]) <= details["max_participants"]


class TestSignupEndpoint:
    """Tests for the signup endpoint."""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity}"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist."""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that signing up the same participant twice fails."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL encoding for activity names."""
        email = "student@mergington.edu"
        activity = "Track and Field"  # Contains space
        
        # URL encode the activity name
        import urllib.parse
        encoded_activity = urllib.parse.quote(activity)
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK


class TestRemoveParticipantEndpoint:
    """Tests for the remove participant endpoint."""
    
    def test_remove_participant_success(self, client, reset_activities):
        """Test successful removal of a participant."""
        email = "michael@mergington.edu"  # Existing participant in Chess Club
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == f"Removed {email} from {activity}"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_remove_participant_from_nonexistent_activity(self, client):
        """Test removing participant from activity that doesn't exist."""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_nonexistent_participant(self, client):
        """Test removing a participant that isn't registered."""
        email = "nonexistent@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Participant not found in this activity"
    
    def test_remove_participant_with_special_characters(self, client, reset_activities):
        """Test removing participant with URL encoding."""
        email = "david@mergington.edu"  # Existing participant in Track and Field
        activity = "Track and Field"  # Contains space
        
        import urllib.parse
        encoded_activity = urllib.parse.quote(activity)
        encoded_email = urllib.parse.quote(email)
        
        response = client.delete(f"/activities/{encoded_activity}/participants/{encoded_email}")
        assert response.status_code == status.HTTP_200_OK


class TestIntegrationScenarios:
    """Integration tests covering complete workflows."""
    
    def test_signup_and_remove_workflow(self, client, reset_activities):
        """Test complete signup and removal workflow."""
        email = "workflow@mergington.edu"
        activity = "Art Club"
        
        # First, sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Then remove
        remove_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert remove_response.status_code == status.HTTP_200_OK
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_activity_capacity_management(self, client, reset_activities):
        """Test that activity capacity is properly managed."""
        activity = "Chess Club"  # Has max_participants: 12
        
        # Get current participants count
        activities_response = client.get("/activities")
        current_count = len(activities_response.json()[activity]["participants"])
        max_participants = activities_response.json()[activity]["max_participants"]
        
        # Add participants up to capacity
        for i in range(max_participants - current_count):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify we're at capacity
        activities_response = client.get("/activities")
        final_count = len(activities_response.json()[activity]["participants"])
        assert final_count == max_participants