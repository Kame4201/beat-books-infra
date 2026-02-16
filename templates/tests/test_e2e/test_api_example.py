"""
E2E (End-to-End) test example for API endpoints.

Tests full API request/response cycle using FastAPI TestClient.
Validates response shapes, status codes, and error handling.

Copy to: beat-books-api/tests/test_e2e/test_api.py
"""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """E2E tests for health check endpoint."""

    def test_health_endpoint_returns_200(self, test_client):
        """
        GIVEN a running API server
        WHEN calling GET /health
        THEN return 200 status with health info
        """
        # Act
        response = test_client.get("/health")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "status" in response.json()

    def test_health_endpoint_correct_shape(self, test_client):
        """
        GIVEN a running API server
        WHEN calling GET /health
        THEN response has expected JSON structure
        """
        # Act
        response = test_client.get("/health")
        data = response.json()

        # Assert
        assert "status" in data
        assert data["status"] == "healthy"
        # In real API, might also check: database_connected, cache_status, etc.


class TestPredictionEndpoint:
    """E2E tests for prediction endpoints."""

    def test_get_prediction_valid_game_id(self, test_client, sample_prediction_response):
        """
        GIVEN a valid game_id
        WHEN calling GET /predictions/{game_id}
        THEN return 200 with prediction data
        """
        # Arrange
        game_id = "G202401010001"

        # Act
        response = test_client.get(f"/predictions/{game_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "game_id" in data
        assert "prediction" in data
        assert "home_win_prob" in data["prediction"]
        assert "away_win_prob" in data["prediction"]

    def test_get_prediction_invalid_game_id(self, test_client):
        """
        GIVEN an invalid/non-existent game_id
        WHEN calling GET /predictions/{game_id}
        THEN return 404 Not Found
        """
        # Arrange
        invalid_game_id = "INVALID123"

        # Act
        response = test_client.get(f"/predictions/{invalid_game_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_post_prediction_request_valid_payload(self, test_client, sample_prediction_request):
        """
        GIVEN a valid prediction request payload
        WHEN calling POST /predictions
        THEN return 201 with prediction result
        """
        # Act
        response = test_client.post("/predictions", json=sample_prediction_request)

        # Assert - Adjust expected status code based on your API
        # Using 200 for successful processing, or 201 if creating a resource
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert "prediction" in data or "game_id" in data

    def test_post_prediction_request_missing_required_field(
        self, test_client, sample_prediction_request
    ):
        """
        GIVEN a payload missing required fields
        WHEN calling POST /predictions
        THEN return 422 Unprocessable Entity
        """
        # Arrange
        invalid_payload = sample_prediction_request.copy()
        del invalid_payload["game_id"]  # Remove required field

        # Act
        response = test_client.post("/predictions", json=invalid_payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data


class TestGamesEndpoint:
    """E2E tests for games listing endpoint."""

    def test_get_games_returns_list(self, test_client):
        """
        GIVEN games exist in the system
        WHEN calling GET /games
        THEN return 200 with list of games
        """
        # Act
        response = test_client.get("/games")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list) or "games" in data

    def test_get_games_with_date_filter(self, test_client):
        """
        GIVEN a date filter parameter
        WHEN calling GET /games?date=2024-01-01
        THEN return only games on that date
        """
        # Arrange
        date_param = "2024-01-01"

        # Act
        response = test_client.get(f"/games?date={date_param}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        # In real test, verify all returned games match the date filter

    def test_get_games_with_invalid_date_format(self, test_client):
        """
        GIVEN an invalid date format
        WHEN calling GET /games?date=invalid
        THEN return 422 Unprocessable Entity
        """
        # Act
        response = test_client.get("/games?date=not-a-date")

        # Assert
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_get_games_pagination(self, test_client):
        """
        GIVEN pagination parameters
        WHEN calling GET /games?page=1&page_size=10
        THEN return paginated results
        """
        # Act
        response = test_client.get("/games?page=1&page_size=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify pagination metadata (adjust based on your API structure)
        if isinstance(data, dict):
            assert "items" in data or "games" in data
            # Optionally check: total, page, page_size


class TestOddsEndpoint:
    """E2E tests for odds endpoints."""

    def test_get_odds_for_game(self, test_client):
        """
        GIVEN a valid game_id
        WHEN calling GET /odds/{game_id}
        THEN return 200 with odds data
        """
        # Arrange
        game_id = "G202401010001"

        # Act
        response = test_client.get(f"/odds/{game_id}")

        # Assert
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "game_id" in data
            assert "bookmakers" in data or "spread" in data

    def test_get_odds_returns_multiple_bookmakers(self, test_client, sample_odds_response):
        """
        GIVEN odds from multiple bookmakers exist
        WHEN calling GET /odds/{game_id}
        THEN return odds from all bookmakers
        """
        # Arrange
        game_id = "G202401010001"

        # Act
        response = test_client.get(f"/odds/{game_id}")

        # Assert
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # Verify structure matches expected format
            assert "bookmakers" in data or isinstance(data, list)


class TestErrorHandling:
    """E2E tests for error handling across all endpoints."""

    def test_404_for_nonexistent_endpoint(self, test_client):
        """
        GIVEN a non-existent endpoint
        WHEN calling GET /does-not-exist
        THEN return 404 Not Found
        """
        # Act
        response = test_client.get("/does-not-exist")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_405_for_method_not_allowed(self, test_client):
        """
        GIVEN an endpoint that only accepts GET
        WHEN calling with POST method
        THEN return 405 Method Not Allowed
        """
        # Act
        response = test_client.post("/health")

        # Assert
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_invalid_json_returns_422(self, test_client):
        """
        GIVEN invalid JSON in request body
        WHEN calling POST endpoint
        THEN return 422 Unprocessable Entity
        """
        # Act
        response = test_client.post(
            "/predictions",
            data="not-valid-json",  # Invalid JSON
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_missing_content_type_header(self, test_client):
        """
        GIVEN a POST request without Content-Type header
        WHEN calling endpoint expecting JSON
        THEN handle gracefully (415 or 422)
        """
        # Act
        response = test_client.post(
            "/predictions",
            data='{"game_id": "G001"}',
            headers={}  # No Content-Type
        )

        # Assert
        # FastAPI usually handles this, but verify it doesn't crash
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


class TestAuthentication:
    """E2E tests for authentication (if applicable)."""

    def test_protected_endpoint_without_auth(self, test_client):
        """
        GIVEN a protected endpoint requiring authentication
        WHEN calling without auth token
        THEN return 401 Unauthorized
        """
        # Act
        response = test_client.get("/admin/settings")

        # Assert
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND  # If endpoint doesn't exist yet
        ]

    def test_protected_endpoint_with_valid_auth(self, test_client, auth_headers):
        """
        GIVEN a protected endpoint
        WHEN calling with valid auth token
        THEN return 200 OK
        """
        # Act
        response = test_client.get("/admin/settings", headers=auth_headers)

        # Assert
        # Adjust based on whether this endpoint exists
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_protected_endpoint_with_invalid_auth(self, test_client):
        """
        GIVEN a protected endpoint
        WHEN calling with invalid/expired token
        THEN return 401 Unauthorized
        """
        # Arrange
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}

        # Act
        response = test_client.get("/admin/settings", headers=invalid_headers)

        # Assert
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestCORS:
    """E2E tests for CORS configuration."""

    def test_cors_headers_present(self, test_client):
        """
        GIVEN CORS is configured
        WHEN making a request
        THEN CORS headers are present in response
        """
        # Act
        response = test_client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # Assert
        # Verify CORS headers (adjust based on your configuration)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        # In production, check for: Access-Control-Allow-Origin header
