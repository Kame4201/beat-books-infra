"""
Unit test example for web scraping service.

Tests scraping logic with mocked HTTP responses and HTML parsing.
No real network requests - all external dependencies are mocked.

Copy to: beat-books-data/tests/test_unit/test_scrape_service.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup


class TestScrapeService:
    """Unit tests for web scraping functionality."""

    @patch("requests.get")
    def test_scrape_game_data_success(self, mock_get, mock_html_response):
        """
        GIVEN a valid HTML page with game data
        WHEN scraping the page
        THEN correctly extract game information
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html_response
        mock_get.return_value = mock_response

        # Mock your scraping service (replace with actual import)
        # from src.services.scrape_service import ScrapeService
        # scraper = ScrapeService()

        # Act
        soup = BeautifulSoup(mock_html_response, "html.parser")
        game_row = soup.find("div", class_="game-row")
        game_id = game_row.get("data-game-id")
        teams = game_row.find_all("span", class_="team-name")
        scores = game_row.find_all("span", class_="score")

        # Assert
        assert game_id == "G202401010001"
        assert len(teams) == 2
        assert teams[0].text == "Test Warriors"
        assert teams[1].text == "Test Lakers"
        assert scores[0].text == "110"
        assert scores[1].text == "105"

    @patch("requests.get")
    def test_scrape_game_data_403_error_retry(self, mock_get):
        """
        GIVEN a 403 Forbidden response
        WHEN scraping attempts
        THEN retry with different user agent and handle gracefully
        """
        # Arrange - first call returns 403, second call succeeds
        mock_response_403 = Mock()
        mock_response_403.status_code = 403
        mock_response_403.raise_for_status.side_effect = Exception("403 Forbidden")

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.text = "<html><body>Success</body></html>"

        mock_get.side_effect = [mock_response_403, mock_response_200]

        # Act - simulate retry logic
        try:
            response = mock_get("https://example.com")
            response.raise_for_status()
        except Exception:
            # Retry with different headers
            response = mock_get("https://example.com", headers={"User-Agent": "Mozilla/5.0"})

        # Assert
        assert response.status_code == 200
        assert mock_get.call_count == 2

    def test_scrape_game_data_malformed_html(self):
        """
        GIVEN malformed HTML with missing expected elements
        WHEN parsing the page
        THEN handle gracefully without crashing
        """
        # Arrange
        malformed_html = """
        <html>
            <body>
                <div class="game-row">
                    <span class="team-name">Test Warriors</span>
                    <!-- Missing second team and scores -->
                </div>
            </body>
        </html>
        """

        # Act
        soup = BeautifulSoup(malformed_html, "html.parser")
        game_row = soup.find("div", class_="game-row")
        teams = game_row.find_all("span", class_="team-name")
        scores = game_row.find_all("span", class_="score")

        # Assert - verify we can handle missing data
        assert len(teams) == 1  # Only one team found
        assert len(scores) == 0  # No scores found
        # In real code, this should raise a validation error or return None

    @patch("selenium.webdriver.Chrome")
    def test_scrape_with_javascript_rendering(self, mock_chrome):
        """
        GIVEN a page that requires JavaScript rendering
        WHEN using Selenium WebDriver
        THEN correctly extract dynamically loaded content
        """
        # Arrange
        mock_driver = MagicMock()
        mock_driver.page_source = """
        <html>
            <body>
                <div id="game-container">
                    <span class="score">110</span>
                </div>
            </body>
        </html>
        """
        mock_chrome.return_value = mock_driver

        # Act
        driver = mock_chrome()
        driver.get("https://example.com/games")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        score = soup.find("span", class_="score")

        # Assert
        assert score.text == "110"
        driver.quit.assert_not_called()  # Verify cleanup hasn't happened yet

    def test_parse_odds_from_text_valid(self):
        """
        GIVEN valid odds text (e.g., "-110", "+150")
        WHEN parsing to decimal odds
        THEN return correct decimal representation
        """
        # Arrange
        american_odds = ["-110", "+150", "-200", "+100"]

        # Act & Assert
        def american_to_decimal(odds_str: str) -> float:
            odds = int(odds_str)
            if odds > 0:
                return 1 + (odds / 100)
            else:
                return 1 + (100 / abs(odds))

        assert american_to_decimal("-110") == pytest.approx(1.909, rel=0.01)
        assert american_to_decimal("+150") == pytest.approx(2.5, rel=0.01)
        assert american_to_decimal("-200") == pytest.approx(1.5, rel=0.01)
        assert american_to_decimal("+100") == pytest.approx(2.0, rel=0.01)

    def test_parse_odds_from_text_invalid(self):
        """
        GIVEN invalid odds text (non-numeric, empty)
        WHEN parsing
        THEN raise appropriate error
        """
        # Arrange
        invalid_odds = ["not-a-number", "", "+-110", "EVEN"]

        # Act & Assert
        def parse_odds(odds_str: str) -> int:
            if not odds_str or not odds_str.lstrip("+-").isdigit():
                raise ValueError(f"Invalid odds format: {odds_str}")
            return int(odds_str)

        for invalid in invalid_odds:
            with pytest.raises(ValueError):
                parse_odds(invalid)

    @patch("time.sleep")
    def test_scrape_with_rate_limiting(self, mock_sleep):
        """
        GIVEN multiple scraping requests
        WHEN rate limiting is enabled
        THEN add appropriate delays between requests
        """
        # Arrange
        urls = ["https://example.com/game1", "https://example.com/game2"]

        # Act
        for i, url in enumerate(urls):
            if i > 0:
                mock_sleep(2)  # 2 second delay between requests

        # Assert
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(2)
