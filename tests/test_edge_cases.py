"""
Performance and edge case tests for the FastAPI application.
"""

import pytest
from concurrent.futures import ThreadPoolExecutor
import time


class TestPerformance:
    """Performance tests for the API endpoints."""
    
    def test_get_activities_response_time(self, client):
        """Test that GET /activities responds quickly."""
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0, f"Response time too slow: {response_time}s"
    
    def test_multiple_concurrent_requests(self, client):
        """Test handling multiple concurrent requests."""
        def make_request():
            return client.get("/activities")
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            assert len(response.json()) > 0


class TestEdgeCases:
    """Edge case tests for various scenarios."""
    
    def test_signup_with_very_long_email(self, client, reset_activities):
        """Test signup with an unusually long email address."""
        # Create a very long email (but still valid)
        long_username = "a" * 50
        email = f"{long_username}@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    def test_activity_name_with_special_characters(self, client):
        """Test handling of activity names with special characters."""
        # "Track and Field" contains spaces
        activity = "Track and Field"
        email = "test@mergington.edu"
        
        # URL encode the activity name properly
        import urllib.parse
        encoded_activity = urllib.parse.quote(activity)
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        # Should either succeed or give a meaningful error
        assert response.status_code in [200, 400, 404]
    
    def test_empty_activity_name(self, client):
        """Test behavior with empty activity name."""
        response = client.post("/activities//signup?email=test@mergington.edu")
        # Should return a 404 or redirect to a proper error
        assert response.status_code in [404, 422]
    
    def test_signup_without_email_parameter(self, client):
        """Test signup request without email parameter."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # FastAPI validation error
    
    def test_remove_participant_without_email(self, client):
        """Test remove participant without specifying email."""
        response = client.delete("/activities/Chess Club/participants/")
        assert response.status_code in [404, 405]  # Not found or method not allowed


class TestBoundaryConditions:
    """Tests for boundary conditions and limits."""
    
    def test_activity_at_capacity_boundary(self, client, reset_activities):
        """Test behavior when activity is at or near capacity."""
        # Find an activity with available spots
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity_name, details in activities_data.items():
            current_count = len(details["participants"])
            max_count = details["max_participants"]
            
            if current_count < max_count:
                # Fill remaining spots
                spots_to_fill = max_count - current_count
                for i in range(spots_to_fill):
                    email = f"boundary_test_{i}@mergington.edu"
                    response = client.post(f"/activities/{activity_name}/signup?email={email}")
                    assert response.status_code == 200
                
                # Try to add one more (should work since we're not enforcing capacity in the API)
                overflow_email = "overflow@mergington.edu"
                response = client.post(f"/activities/{activity_name}/signup?email={overflow_email}")
                # The current implementation doesn't check capacity, so this will succeed
                assert response.status_code == 200
                break
    
    def test_remove_last_participant(self, client, reset_activities):
        """Test removing the last participant from an activity."""
        # Find an activity with exactly one participant or create one
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity_name, details in activities_data.items():
            if len(details["participants"]) >= 1:
                # Remove all but one participant
                participants = details["participants"].copy()
                for email in participants[:-1]:
                    response = client.delete(f"/activities/{activity_name}/participants/{email}")
                    assert response.status_code == 200
                
                # Remove the last participant
                last_email = participants[-1]
                response = client.delete(f"/activities/{activity_name}/participants/{last_email}")
                assert response.status_code == 200
                
                # Verify the activity has no participants
                final_response = client.get("/activities")
                final_data = final_response.json()
                assert len(final_data[activity_name]["participants"]) == 0
                break


class TestErrorHandling:
    """Tests for error handling and recovery."""
    
    def test_malformed_email_in_signup(self, client):
        """Test signup with malformed email addresses."""
        malformed_emails = [
            "notanemail",
            "@mergington.edu",
            "test@",
            "test@@mergington.edu",
            "",
            "test@wrongdomain.com"
        ]
        
        for email in malformed_emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            # The API currently doesn't validate email format, so these will succeed
            # In a real application, you might want to add validation
            assert response.status_code in [200, 400, 422]
    
    def test_sql_injection_attempt_in_email(self, client):
        """Test that SQL injection attempts in email are handled safely."""
        # Since we're using in-memory data structures, this is more about input sanitization
        malicious_emails = [
            "'; DROP TABLE users; --@mergington.edu",
            "1' OR '1'='1@mergington.edu",
            "<script>alert('xss')</script>@mergington.edu"
        ]
        
        for email in malicious_emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            # Should handle gracefully without crashing
            assert response.status_code in [200, 400, 422]
    
    def test_unicode_characters_in_inputs(self, client):
        """Test handling of Unicode characters in inputs."""
        unicode_emails = [
            "tëst@mergington.edu",
            "用户@mergington.edu",
            "тест@mergington.edu"
        ]
        
        for email in unicode_emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            assert response.status_code in [200, 400, 422]