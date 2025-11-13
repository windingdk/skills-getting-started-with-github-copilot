"""
Tests for the data models and business logic of the activities system.
"""

import pytest
from src.app import activities


class TestActivitiesDataStructure:
    """Tests for the activities data structure and validation."""
    
    def test_all_activities_have_required_fields(self):
        """Test that all activities have the required fields."""
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, details in activities.items():
            for field in required_fields:
                assert field in details, f"Activity '{activity_name}' missing field '{field}'"
    
    def test_max_participants_are_positive(self):
        """Test that all max_participants values are positive integers."""
        for activity_name, details in activities.items():
            assert isinstance(details["max_participants"], int), f"Activity '{activity_name}' has non-integer max_participants"
            assert details["max_participants"] > 0, f"Activity '{activity_name}' has non-positive max_participants"
    
    def test_participants_lists_are_valid(self):
        """Test that participants lists are valid and within capacity."""
        for activity_name, details in activities.items():
            participants = details["participants"]
            max_participants = details["max_participants"]
            
            assert isinstance(participants, list), f"Activity '{activity_name}' participants is not a list"
            assert len(participants) <= max_participants, f"Activity '{activity_name}' exceeds capacity"
            
            # Check for duplicate participants
            assert len(participants) == len(set(participants)), f"Activity '{activity_name}' has duplicate participants"
            
            # Check email format (basic validation)
            for email in participants:
                assert "@" in email, f"Invalid email format in '{activity_name}': {email}"
                assert email.endswith("@mergington.edu"), f"Non-school email in '{activity_name}': {email}"
    
    def test_descriptions_are_not_empty(self):
        """Test that all activity descriptions are non-empty strings."""
        for activity_name, details in activities.items():
            description = details["description"]
            assert isinstance(description, str), f"Activity '{activity_name}' description is not a string"
            assert len(description.strip()) > 0, f"Activity '{activity_name}' has empty description"
    
    def test_schedules_are_not_empty(self):
        """Test that all activity schedules are non-empty strings."""
        for activity_name, details in activities.items():
            schedule = details["schedule"]
            assert isinstance(schedule, str), f"Activity '{activity_name}' schedule is not a string"
            assert len(schedule.strip()) > 0, f"Activity '{activity_name}' has empty schedule"


class TestActivityNames:
    """Tests for activity names and their properties."""
    
    def test_activity_names_are_unique(self):
        """Test that all activity names are unique."""
        activity_names = list(activities.keys())
        assert len(activity_names) == len(set(activity_names)), "Duplicate activity names found"
    
    def test_activity_names_are_not_empty(self):
        """Test that activity names are not empty."""
        for activity_name in activities.keys():
            assert isinstance(activity_name, str), f"Activity name is not a string: {activity_name}"
            assert len(activity_name.strip()) > 0, "Empty activity name found"
    
    def test_minimum_number_of_activities(self):
        """Test that we have a reasonable number of activities."""
        assert len(activities) >= 5, "Should have at least 5 activities available"


class TestDataConsistency:
    """Tests for data consistency and integrity."""
    
    def test_no_participant_in_multiple_same_activity(self):
        """Test that no participant is registered multiple times for the same activity."""
        for activity_name, details in activities.items():
            participants = details["participants"]
            unique_participants = set(participants)
            assert len(participants) == len(unique_participants), f"Duplicate participants in '{activity_name}'"
    
    def test_capacity_constraints(self):
        """Test that current enrollment doesn't exceed capacity."""
        for activity_name, details in activities.items():
            current_enrollment = len(details["participants"])
            max_capacity = details["max_participants"]
            assert current_enrollment <= max_capacity, f"Activity '{activity_name}' is over capacity"
    
    def test_realistic_capacity_values(self):
        """Test that capacity values are realistic for a high school."""
        for activity_name, details in activities.items():
            max_participants = details["max_participants"]
            # Reasonable bounds for high school activities
            assert 1 <= max_participants <= 100, f"Unrealistic capacity for '{activity_name}': {max_participants}"


class TestEmailValidation:
    """Tests for email validation logic (implicit in the data)."""
    
    def test_all_emails_have_school_domain(self):
        """Test that all participant emails use the school domain."""
        school_domain = "@mergington.edu"
        
        for activity_name, details in activities.items():
            for email in details["participants"]:
                assert email.endswith(school_domain), f"Non-school email in '{activity_name}': {email}"
    
    def test_email_format_basic_validation(self):
        """Test basic email format validation."""
        for activity_name, details in activities.items():
            for email in details["participants"]:
                assert "@" in email, f"Invalid email format in '{activity_name}': {email}"
                assert not email.startswith("@"), f"Invalid email format in '{activity_name}': {email}"
                assert not email.endswith("@"), f"Invalid email format in '{activity_name}': {email}"
                assert email.count("@") == 1, f"Invalid email format in '{activity_name}': {email}"