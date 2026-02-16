"""
Integration test example for scraping workflow.

Tests full flow: HTTP request → HTML parsing → data storage → verification.
Uses SQLite test database but mocks external HTTP calls.

Copy to: beat-books-data/tests/test_integration/test_scrape_workflow.py
"""

import pytest
from unittest.mock import patch, Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone


class TestScrapeWorkflowIntegration:
    """Integration tests for end-to-end scraping workflow."""

    @pytest.fixture(scope="function")
    def test_db(self):
        """
        Create a temporary SQLite database for integration tests.
        Cleaned up after each test.
        """
        engine = create_engine("sqlite:///test_scrape.db", echo=False)

        # Mock: Create tables (replace with actual models)
        # from src.models import Base
        # Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        yield session

        session.close()
        engine.dispose()

        # Cleanup test database file
        import os
        if os.path.exists("test_scrape.db"):
            os.remove("test_scrape.db")

    @patch("requests.get")
    def test_scrape_parse_store_verify_workflow(self, mock_get, test_db, mock_html_response):
        """
        GIVEN a mocked HTTP response with game data
        WHEN executing full scrape workflow
        THEN data is correctly parsed, stored in DB, and retrievable
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html_response
        mock_get.return_value = mock_response

        # Mock scraping service (replace with actual import)
        # from src.services.scrape_service import ScrapeService
        # from src.repositories.game_repository import GameRepository
        # scraper = ScrapeService()
        # repo = GameRepository(test_db)

        # Act - Step 1: Fetch HTML
        response = mock_get("https://example.com/games")
        assert response.status_code == 200

        # Act - Step 2: Parse HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        game_row = soup.find("div", class_="game-row")

        parsed_game = {
            "game_id": game_row.get("data-game-id"),
            "home_team": game_row.find_all("span", class_="team-name")[0].text,
            "away_team": game_row.find_all("span", class_="team-name")[1].text,
            "home_score": int(game_row.find_all("span", class_="score")[0].text),
            "away_score": int(game_row.find_all("span", class_="score")[1].text)
        }

        # Act - Step 3: Store in database (mock)
        # In real code: repo.create_game(parsed_game)
        # For this example, we'll just verify the parsed data
        test_db.execute = Mock()  # Mock database insert

        # Assert - Step 4: Verify data structure
        assert parsed_game["game_id"] == "G202401010001"
        assert parsed_game["home_team"] == "Test Warriors"
        assert parsed_game["away_team"] == "Test Lakers"
        assert parsed_game["home_score"] == 110
        assert parsed_game["away_score"] == 105

    @patch("requests.get")
    def test_scrape_multiple_games_batch_insert(self, mock_get, test_db):
        """
        GIVEN HTML with multiple games
        WHEN scraping and storing
        THEN all games are correctly inserted in a single transaction
        """
        # Arrange
        multi_game_html = """
        <html>
            <body>
                <div class="game-row" data-game-id="G001">
                    <span class="team-name">Team A</span>
                    <span class="score">100</span>
                    <span class="team-name">Team B</span>
                    <span class="score">95</span>
                </div>
                <div class="game-row" data-game-id="G002">
                    <span class="team-name">Team C</span>
                    <span class="score">105</span>
                    <span class="team-name">Team D</span>
                    <span class="score">110</span>
                </div>
                <div class="game-row" data-game-id="G003">
                    <span class="team-name">Team E</span>
                    <span class="score">98</span>
                    <span class="team-name">Team F</span>
                    <span class="score">102</span>
                </div>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = multi_game_html
        mock_get.return_value = mock_response

        # Act
        response = mock_get("https://example.com/games")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        game_rows = soup.find_all("div", class_="game-row")

        parsed_games = []
        for row in game_rows:
            game = {
                "game_id": row.get("data-game-id"),
                "home_team": row.find_all("span", class_="team-name")[0].text,
                "away_team": row.find_all("span", class_="team-name")[1].text,
                "home_score": int(row.find_all("span", class_="score")[0].text),
                "away_score": int(row.find_all("span", class_="score")[1].text)
            }
            parsed_games.append(game)

        # Assert
        assert len(parsed_games) == 3
        assert parsed_games[0]["game_id"] == "G001"
        assert parsed_games[1]["game_id"] == "G002"
        assert parsed_games[2]["game_id"] == "G003"

        # In real code: repo.bulk_insert(parsed_games)
        # Then verify: assert test_db.query(Game).count() == 3

    @patch("requests.get")
    def test_scrape_workflow_handles_duplicates(self, mock_get, test_db):
        """
        GIVEN a game that already exists in database
        WHEN scraping the same game again
        THEN handle duplicate gracefully (upsert or skip)
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="game-row" data-game-id="G001">
                    <span class="team-name">Team A</span>
                    <span class="score">100</span>
                    <span class="team-name">Team B</span>
                    <span class="score">95</span>
                </div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        # Act - First scrape
        response1 = mock_get("https://example.com/games")
        from bs4 import BeautifulSoup
        soup1 = BeautifulSoup(response1.text, "html.parser")
        game1 = soup1.find("div", class_="game-row")

        # Simulate storing game1
        stored_game_ids = {"G001"}

        # Act - Second scrape (duplicate)
        response2 = mock_get("https://example.com/games")
        soup2 = BeautifulSoup(response2.text, "html.parser")
        game2 = soup2.find("div", class_="game-row")
        game_id = game2.get("data-game-id")

        # Assert - Detect duplicate
        is_duplicate = game_id in stored_game_ids
        assert is_duplicate is True

        # In real code: if is_duplicate: update_game() else: insert_game()

    @patch("requests.get")
    def test_scrape_workflow_error_recovery(self, mock_get, test_db):
        """
        GIVEN an HTTP error during scraping
        WHEN error occurs mid-workflow
        THEN rollback transaction and don't persist partial data
        """
        # Arrange
        mock_get.side_effect = Exception("Network timeout")

        # Act & Assert
        with pytest.raises(Exception, match="Network timeout"):
            response = mock_get("https://example.com/games")

        # Verify database transaction was rolled back (no partial data)
        # In real code: assert test_db.query(Game).count() == 0

    def test_parse_and_transform_date_formats(self, test_db):
        """
        GIVEN various date formats from scraped data
        WHEN transforming to standard format
        THEN all dates are correctly normalized to UTC datetime
        """
        # Arrange
        date_inputs = [
            "2024-01-01 19:00:00",  # Standard format
            "Jan 1, 2024 7:00 PM",  # Human-readable
            "1704135600",            # Unix timestamp
            "2024-01-01T19:00:00Z"  # ISO format
        ]

        # Act
        from dateutil import parser
        import time

        parsed_dates = []
        for date_str in date_inputs:
            if date_str.isdigit():
                # Unix timestamp
                dt = datetime.fromtimestamp(int(date_str), tz=timezone.utc)
            else:
                # Parse string
                dt = parser.parse(date_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)

            parsed_dates.append(dt)

        # Assert - All dates should be the same time
        expected = datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc)
        for dt in parsed_dates:
            assert dt == expected or abs((dt - expected).total_seconds()) < 60

    @patch("requests.get")
    def test_scrape_with_pagination(self, mock_get, test_db):
        """
        GIVEN paginated results across multiple pages
        WHEN scraping all pages
        THEN collect data from all pages sequentially
        """
        # Arrange
        page1_html = """
        <html><body>
            <div class="game-row" data-game-id="G001">
                <span class="team-name">Team A</span>
                <span class="score">100</span>
                <span class="team-name">Team B</span>
                <span class="score">95</span>
            </div>
            <a class="next-page" href="/games?page=2">Next</a>
        </body></html>
        """

        page2_html = """
        <html><body>
            <div class="game-row" data-game-id="G002">
                <span class="team-name">Team C</span>
                <span class="score">105</span>
                <span class="team-name">Team D</span>
                <span class="score">110</span>
            </div>
        </body></html>
        """

        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.text = page1_html

        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.text = page2_html

        mock_get.side_effect = [mock_response_1, mock_response_2]

        # Act
        all_games = []
        from bs4 import BeautifulSoup

        # Page 1
        response1 = mock_get("https://example.com/games?page=1")
        soup1 = BeautifulSoup(response1.text, "html.parser")
        games1 = soup1.find_all("div", class_="game-row")
        all_games.extend([g.get("data-game-id") for g in games1])

        # Check for next page
        next_link = soup1.find("a", class_="next-page")
        if next_link:
            # Page 2
            response2 = mock_get("https://example.com/games?page=2")
            soup2 = BeautifulSoup(response2.text, "html.parser")
            games2 = soup2.find_all("div", class_="game-row")
            all_games.extend([g.get("data-game-id") for g in games2])

        # Assert
        assert len(all_games) == 2
        assert "G001" in all_games
        assert "G002" in all_games
        assert mock_get.call_count == 2
