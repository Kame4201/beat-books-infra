"""
Unit test example for DTO (Data Transfer Object) validation.

Tests Pydantic models or dataclass validation logic.
Ensures data integrity and proper error handling for invalid inputs.

Copy to: beat-books-data/tests/test_unit/test_dto_validation.py
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError


class TestDTOValidation:
    """Unit tests for data validation using DTOs."""

    def test_game_dto_valid_data_passes(self):
        """
        GIVEN valid game data with all required fields
        WHEN creating a GameDTO
        THEN validation passes and object is created successfully
        """
        # Arrange
        valid_game_data = {
            "game_id": "G202401010001",
            "home_team_id": "TEST001",
            "away_team_id": "TEST002",
            "game_date": datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc),
            "season": "2023-24",
            "status": "scheduled"
        }

        # Mock Pydantic model (replace with actual import)
        # from src.models.dtos import GameDTO
        # game = GameDTO(**valid_game_data)

        # Act & Assert
        assert valid_game_data["game_id"] == "G202401010001"
        assert valid_game_data["season"] == "2023-24"
        assert valid_game_data["status"] in ["scheduled", "in_progress", "final"]

    def test_game_dto_invalid_season_rejected(self):
        """
        GIVEN game data with invalid season format
        WHEN creating a GameDTO
        THEN ValidationError is raised
        """
        # Arrange
        invalid_game_data = {
            "game_id": "G202401010001",
            "home_team_id": "TEST001",
            "away_team_id": "TEST002",
            "game_date": datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc),
            "season": "2024",  # Invalid - should be "YYYY-YY" format
            "status": "scheduled"
        }

        # Act & Assert
        # Mock validation (replace with actual DTO validation)
        def validate_season(season: str) -> bool:
            # Valid format: "2023-24"
            if len(season) != 7 or season[4] != "-":
                return False
            year1, year2 = season.split("-")
            return year1.isdigit() and year2.isdigit() and len(year2) == 2

        assert validate_season("2023-24") is True
        assert validate_season("2024") is False
        assert validate_season(invalid_game_data["season"]) is False

    def test_player_stats_dto_negative_stats_rejected(self):
        """
        GIVEN player stats with negative values
        WHEN creating a PlayerStatsDTO
        THEN ValidationError is raised for negative numbers
        """
        # Arrange
        invalid_stats = {
            "stat_id": "STAT001",
            "game_id": "G202401010001",
            "player_id": "P12345",
            "points": -5,  # Invalid - cannot be negative
            "rebounds": 8,
            "assists": 6,
            "minutes_played": 36
        }

        # Act & Assert
        # Mock validation
        def validate_non_negative(value: int, field_name: str) -> None:
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")

        with pytest.raises(ValueError, match="points cannot be negative"):
            validate_non_negative(invalid_stats["points"], "points")

    def test_player_stats_dto_percentage_validation(self):
        """
        GIVEN player stats with field goal attempts
        WHEN calculating shooting percentage
        THEN validate percentage is between 0 and 1
        """
        # Arrange
        stats = {
            "field_goals_made": 9,
            "field_goals_attempted": 18,
            "three_pointers_made": 3,
            "three_pointers_attempted": 7
        }

        # Act
        fg_percentage = stats["field_goals_made"] / stats["field_goals_attempted"]
        three_pt_percentage = stats["three_pointers_made"] / stats["three_pointers_attempted"]

        # Assert
        assert 0 <= fg_percentage <= 1
        assert 0 <= three_pt_percentage <= 1
        assert fg_percentage == pytest.approx(0.5, rel=0.01)
        assert three_pt_percentage == pytest.approx(0.428, rel=0.01)

    def test_odds_dto_valid_american_odds(self):
        """
        GIVEN valid American odds format
        WHEN creating an OddsDTO
        THEN validation passes for both negative and positive odds
        """
        # Arrange
        valid_odds_data = [
            {"bookmaker": "TestBook", "home_moneyline": -220, "away_moneyline": 180},
            {"bookmaker": "TestBook2", "home_moneyline": 150, "away_moneyline": -180},
            {"bookmaker": "TestBook3", "home_moneyline": -110, "away_moneyline": -110}
        ]

        # Act & Assert
        def validate_american_odds(odds: int) -> bool:
            # American odds must be non-zero and typically >= -10000 and <= 10000
            return odds != 0 and -10000 <= odds <= 10000

        for odds_data in valid_odds_data:
            assert validate_american_odds(odds_data["home_moneyline"])
            assert validate_american_odds(odds_data["away_moneyline"])

    def test_odds_dto_zero_odds_rejected(self):
        """
        GIVEN odds data with zero values
        WHEN creating an OddsDTO
        THEN ValidationError is raised (odds cannot be zero)
        """
        # Arrange
        invalid_odds = {
            "bookmaker": "TestBook",
            "home_moneyline": 0,  # Invalid
            "away_moneyline": 180
        }

        # Act & Assert
        def validate_american_odds(odds: int) -> None:
            if odds == 0:
                raise ValueError("Odds cannot be zero")

        with pytest.raises(ValueError, match="Odds cannot be zero"):
            validate_american_odds(invalid_odds["home_moneyline"])

    def test_team_dto_missing_required_field(self):
        """
        GIVEN team data missing required fields
        WHEN creating a TeamDTO
        THEN ValidationError is raised
        """
        # Arrange
        incomplete_team = {
            "team_id": "TEST001",
            "name": "Test Warriors",
            # Missing city, abbreviation, conference, division
        }

        required_fields = ["team_id", "name", "city", "abbreviation", "conference", "division"]

        # Act & Assert
        for field in required_fields:
            if field not in incomplete_team:
                # In real Pydantic model, this would raise ValidationError
                assert field not in incomplete_team

    def test_game_dto_future_date_validation(self):
        """
        GIVEN a game with a date in the distant future
        WHEN creating a GameDTO
        THEN validation passes but may trigger a warning
        """
        # Arrange
        future_game = {
            "game_id": "G202601010001",
            "game_date": datetime(2026, 1, 1, 19, 0, tzinfo=timezone.utc),
            "season": "2025-26"
        }

        # Act
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        days_in_future = (future_game["game_date"] - now).days

        # Assert - game is more than 365 days in future (might want to flag)
        assert days_in_future > 365

    def test_player_stats_dto_field_goals_consistency(self):
        """
        GIVEN player stats where made > attempted
        WHEN creating a PlayerStatsDTO
        THEN ValidationError is raised for impossible stats
        """
        # Arrange
        inconsistent_stats = {
            "field_goals_made": 20,
            "field_goals_attempted": 15  # Invalid - made cannot exceed attempted
        }

        # Act & Assert
        def validate_made_vs_attempted(made: int, attempted: int) -> None:
            if made > attempted:
                raise ValueError("Field goals made cannot exceed attempted")

        with pytest.raises(ValueError, match="cannot exceed attempted"):
            validate_made_vs_attempted(
                inconsistent_stats["field_goals_made"],
                inconsistent_stats["field_goals_attempted"]
            )

    def test_game_dto_same_team_validation(self):
        """
        GIVEN a game where home and away teams are the same
        WHEN creating a GameDTO
        THEN ValidationError is raised
        """
        # Arrange
        invalid_game = {
            "game_id": "G202401010001",
            "home_team_id": "TEST001",
            "away_team_id": "TEST001",  # Same as home team
            "game_date": datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc)
        }

        # Act & Assert
        def validate_different_teams(home_id: str, away_id: str) -> None:
            if home_id == away_id:
                raise ValueError("Home and away teams must be different")

        with pytest.raises(ValueError, match="must be different"):
            validate_different_teams(
                invalid_game["home_team_id"],
                invalid_game["away_team_id"]
            )
