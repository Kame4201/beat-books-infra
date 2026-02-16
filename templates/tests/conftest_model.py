"""
Shared test fixtures for beat-books-model repo.

This conftest provides fixtures for feature data, game outcomes, model inputs,
and common test utilities for the ML prediction service.

Copy this file to `tests/conftest.py` in beat-books-model and customize as needed.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone


@pytest.fixture
def sample_game_features():
    """Sample feature vector for a single game prediction."""
    return {
        "home_team_win_pct": 0.650,
        "away_team_win_pct": 0.550,
        "home_avg_points": 112.5,
        "away_avg_points": 108.3,
        "home_avg_points_allowed": 105.2,
        "away_avg_points_allowed": 110.8,
        "home_rest_days": 2,
        "away_rest_days": 1,
        "home_injuries": 0,
        "away_injuries": 1,
        "is_home": 1,
        "days_since_last_game": 2
    }


@pytest.fixture
def sample_feature_matrix():
    """Sample feature matrix for batch predictions (5 games)."""
    return np.array([
        [0.650, 0.550, 112.5, 108.3, 105.2, 110.8, 2, 1, 0, 1, 1, 2],
        [0.580, 0.620, 110.2, 115.0, 108.5, 106.3, 1, 2, 1, 0, 0, 1],
        [0.700, 0.450, 118.3, 102.5, 103.8, 112.5, 3, 0, 0, 2, 1, 3],
        [0.520, 0.530, 106.8, 109.2, 110.1, 108.9, 1, 1, 1, 1, 1, 1],
        [0.490, 0.600, 104.5, 112.8, 111.3, 107.2, 2, 2, 2, 0, 0, 2]
    ])


@pytest.fixture
def sample_game_outcome():
    """Sample game outcome for testing predictions."""
    return {
        "game_id": "G202401010001",
        "home_team_id": "TEST001",
        "away_team_id": "TEST002",
        "home_score": 110,
        "away_score": 105,
        "home_won": True,
        "total_score": 215,
        "margin": 5,
        "game_date": datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc)
    }


@pytest.fixture
def sample_training_data():
    """Sample training dataset (features + labels)."""
    X = np.array([
        [0.650, 0.550, 112.5, 108.3, 1],
        [0.580, 0.620, 110.2, 115.0, 0],
        [0.700, 0.450, 118.3, 102.5, 1],
        [0.520, 0.530, 106.8, 109.2, 1],
        [0.490, 0.600, 104.5, 112.8, 0]
    ])
    y = np.array([1, 0, 1, 1, 0])  # 1 = home win, 0 = away win
    return X, y


@pytest.fixture
def sample_odds_data():
    """Sample odds data for Kelly criterion calculations."""
    return {
        "game_id": "G202401010001",
        "bookmaker": "TestBook",
        "home_spread": -5.5,
        "home_spread_odds": -110,
        "away_spread": 5.5,
        "away_spread_odds": -110,
        "home_moneyline": -220,
        "away_moneyline": 180,
        "over_under": 225.5,
        "over_odds": -110,
        "under_odds": -110
    }


@pytest.fixture
def sample_prediction_result():
    """Sample model prediction output."""
    return {
        "game_id": "G202401010001",
        "home_win_prob": 0.65,
        "away_win_prob": 0.35,
        "predicted_home_score": 110.5,
        "predicted_away_score": 105.2,
        "predicted_total": 215.7,
        "predicted_margin": 5.3,
        "confidence": 0.72,
        "model_version": "v1.0.0"
    }


@pytest.fixture
def sample_kelly_input():
    """Sample input for Kelly criterion calculation."""
    return {
        "win_probability": 0.55,  # Model's predicted probability
        "decimal_odds": 2.20,      # Bookmaker odds (American +120 = 2.20 decimal)
        "bankroll": 1000.0,
        "max_bet_fraction": 0.05   # Never bet more than 5% of bankroll
    }


@pytest.fixture
def mock_trained_model():
    """Mock trained model for testing predictions."""
    class MockModel:
        def predict(self, X):
            """Returns dummy predictions."""
            return np.array([1, 0, 1])  # Home win, away win, home win

        def predict_proba(self, X):
            """Returns dummy probabilities."""
            return np.array([
                [0.35, 0.65],  # [away_win_prob, home_win_prob]
                [0.60, 0.40],
                [0.30, 0.70]
            ])

        def score(self, X, y):
            """Returns dummy accuracy."""
            return 0.72

    return MockModel()


@pytest.fixture
def sample_dataframe():
    """Sample pandas DataFrame for feature engineering tests."""
    return pd.DataFrame({
        "game_id": ["G001", "G002", "G003"],
        "home_team": ["TEST001", "TEST002", "TEST001"],
        "away_team": ["TEST002", "TEST003", "TEST003"],
        "home_score": [110, 105, 112],
        "away_score": [105, 108, 107],
        "home_win": [True, False, True],
        "game_date": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-03"
        ])
    })
