"""
Test configuration and fixtures for the FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test."""
    # Store original state
    original_activities = {
        activity_name: {
            "description": details["description"],
            "schedule": details["schedule"], 
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
        for activity_name, details in activities.items()
    }
    
    yield
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return {
        "name": "Test Club",
        "details": {
            "description": "A test club for testing purposes",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        }
    }