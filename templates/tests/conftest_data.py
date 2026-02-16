"""
Shared test fixtures for beat-books-data repo.

This conftest provides fixtures for database sessions, sample entities,
and common test utilities for the data ingestion service.

Copy this file to `tests/conftest.py` in beat-books-data and customize as needed.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Provides an in-memory SQLite session for unit tests.
    Automatically rolls back after each test for isolation.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    # Import your models here and create tables
    # Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


@pytest.fixture(scope="function")
def sample_team():
    """Sample team entity for testing."""
    return {
        "team_id": "TEST001",
        "name": "Test Warriors",
        "city": "Test City",
        "abbreviation": "TST",
        "conference": "West",
        "division": "Pacific"
    }


@pytest.fixture(scope="function")
def sample_player():
    """Sample player entity for testing."""
    return {
        "player_id": "P12345",
        "name": "Test Player",
        "team_id": "TEST001",
        "position": "PG",
        "height": "6-3",
        "weight": 190,
        "jersey_number": "23"
    }


@pytest.fixture(scope="function")
def sample_game():
    """Sample game entity for testing."""
    return {
        "game_id": "G202401010001",
        "home_team_id": "TEST001",
        "away_team_id": "TEST002",
        "game_date": datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc),
        "season": "2023-24",
        "status": "scheduled"
    }


@pytest.fixture(scope="function")
def sample_player_stats():
    """Sample player statistics for testing."""
    return {
        "stat_id": "STAT001",
        "game_id": "G202401010001",
        "player_id": "P12345",
        "points": 25,
        "rebounds": 8,
        "assists": 6,
        "steals": 2,
        "blocks": 1,
        "turnovers": 3,
        "minutes_played": 36,
        "field_goals_made": 9,
        "field_goals_attempted": 18,
        "three_pointers_made": 3,
        "three_pointers_attempted": 7,
        "free_throws_made": 4,
        "free_throws_attempted": 5
    }


@pytest.fixture(scope="function")
def sample_odds():
    """Sample betting odds for testing."""
    return {
        "odds_id": "ODDS001",
        "game_id": "G202401010001",
        "bookmaker": "TestBook",
        "home_spread": -5.5,
        "away_spread": 5.5,
        "home_moneyline": -220,
        "away_moneyline": 180,
        "over_under": 225.5,
        "timestamp": datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
    }


@pytest.fixture
def mock_html_response():
    """Sample HTML response for scraping tests."""
    return """
    <html>
        <body>
            <div class="game-row" data-game-id="G202401010001">
                <span class="team-name">Test Warriors</span>
                <span class="score">110</span>
                <span class="team-name">Test Lakers</span>
                <span class="score">105</span>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def mock_api_response():
    """Sample API JSON response for testing."""
    return {
        "game_id": "G202401010001",
        "home_team": {"id": "TEST001", "name": "Test Warriors", "score": 110},
        "away_team": {"id": "TEST002", "name": "Test Lakers", "score": 105},
        "status": "final",
        "date": "2024-01-01T19:00:00Z"
    }
