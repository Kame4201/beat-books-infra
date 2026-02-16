"""
Shared test fixtures for beat-books-api repo.

This conftest provides fixtures for FastAPI TestClient, mock responses,
and common test utilities for the API gateway service.

Copy this file to `tests/conftest.py` in beat-books-api and customize as needed.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone


@pytest.fixture(scope="function")
def test_client():
    """
    Provides a FastAPI TestClient for E2E API testing.

    Usage:
        def test_endpoint(test_client):
            response = test_client.get("/health")
            assert response.status_code == 200
    """
    # Import your FastAPI app here
    # from src.main import app
    # return TestClient(app)

    # Placeholder - replace with actual app import
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    return TestClient(app)


@pytest.fixture
def sample_prediction_request():
    """Sample prediction request payload."""
    return {
        "game_id": "G202401010001",
        "home_team_id": "TEST001",
        "away_team_id": "TEST002",
        "game_date": "2024-01-01T19:00:00Z",
        "use_live_odds": True
    }


@pytest.fixture
def sample_prediction_response():
    """Sample prediction API response."""
    return {
        "game_id": "G202401010001",
        "prediction": {
            "home_win_prob": 0.65,
            "away_win_prob": 0.35,
            "predicted_home_score": 110.5,
            "predicted_away_score": 105.2,
            "confidence": 0.72
        },
        "recommendation": {
            "bet_type": "home_spread",
            "kelly_fraction": 0.03,
            "suggested_bet": 30.0,
            "expected_value": 2.5
        },
        "metadata": {
            "model_version": "v1.0.0",
            "timestamp": "2024-01-01T10:00:00Z"
        }
    }


@pytest.fixture
def sample_games_list():
    """Sample list of games for /games endpoint."""
    return [
        {
            "game_id": "G202401010001",
            "home_team": "Test Warriors",
            "away_team": "Test Lakers",
            "game_date": "2024-01-01T19:00:00Z",
            "status": "scheduled"
        },
        {
            "game_id": "G202401010002",
            "home_team": "Test Celtics",
            "away_team": "Test Heat",
            "game_date": "2024-01-01T20:00:00Z",
            "status": "scheduled"
        }
    ]


@pytest.fixture
def sample_odds_response():
    """Sample odds API response."""
    return {
        "game_id": "G202401010001",
        "bookmakers": [
            {
                "name": "TestBook",
                "markets": {
                    "spread": {
                        "home": -5.5,
                        "away": 5.5,
                        "home_odds": -110,
                        "away_odds": -110
                    },
                    "moneyline": {
                        "home": -220,
                        "away": 180
                    },
                    "totals": {
                        "over_under": 225.5,
                        "over_odds": -110,
                        "under_odds": -110
                    }
                }
            }
        ],
        "last_updated": "2024-01-01T10:00:00Z"
    }


@pytest.fixture
def auth_headers():
    """Sample authentication headers for protected endpoints."""
    return {
        "Authorization": "Bearer test_token_12345",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_db_session():
    """Mock database session for API tests (avoids real DB calls)."""
    class MockSession:
        def query(self, model):
            return self

        def filter(self, *args):
            return self

        def first(self):
            return None

        def all(self):
            return []

        def add(self, obj):
            pass

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    return MockSession()


@pytest.fixture
def mock_prediction_service():
    """Mock prediction service for API tests (avoids calling model service)."""
    class MockPredictionService:
        def predict(self, game_id: str):
            return {
                "home_win_prob": 0.65,
                "away_win_prob": 0.35,
                "confidence": 0.72
            }

        def get_recommendation(self, game_id: str):
            return {
                "bet_type": "home_spread",
                "kelly_fraction": 0.03,
                "suggested_bet": 30.0
            }

    return MockPredictionService()


@pytest.fixture
def invalid_request_payloads():
    """Collection of invalid payloads for validation testing."""
    return {
        "missing_game_id": {
            "home_team_id": "TEST001",
            "away_team_id": "TEST002"
        },
        "invalid_date_format": {
            "game_id": "G202401010001",
            "game_date": "not-a-date"
        },
        "negative_values": {
            "game_id": "G202401010001",
            "bankroll": -1000
        },
        "invalid_team_id": {
            "game_id": "G202401010001",
            "home_team_id": "",
            "away_team_id": "TEST002"
        }
    }


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for API tests."""
    return "http://testserver"
