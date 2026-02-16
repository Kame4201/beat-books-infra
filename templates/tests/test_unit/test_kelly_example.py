"""
Unit test example for Kelly Criterion calculations.

Tests betting strategy calculations with known mathematical inputs/outputs.
Pure function testing with no external dependencies.

Copy to: beat-books-model/tests/test_unit/test_kelly.py
"""

import pytest


class TestKellyCriterion:
    """Unit tests for Kelly Criterion betting calculations."""

    def test_kelly_fraction_known_input_known_output(self):
        """
        GIVEN known probability and odds
        WHEN calculating Kelly fraction
        THEN return mathematically correct Kelly fraction
        """
        # Arrange
        win_prob = 0.55  # 55% chance to win
        decimal_odds = 2.0  # Even money (American +100)

        # Kelly formula: f = (bp - q) / b
        # where b = decimal_odds - 1, p = win_prob, q = 1 - win_prob
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p

        # Act
        kelly_fraction = (b * p - q) / b

        # Assert
        expected = 0.10  # Should bet 10% of bankroll
        assert kelly_fraction == pytest.approx(expected, rel=0.01)

    def test_kelly_fraction_negative_edge_zero_bet(self):
        """
        GIVEN negative expected value (win_prob < implied odds)
        WHEN calculating Kelly fraction
        THEN return zero (no bet recommended)
        """
        # Arrange
        win_prob = 0.45  # 45% chance to win
        decimal_odds = 2.0  # Implies 50% win probability
        # Implied probability = 1 / decimal_odds = 0.50
        # win_prob (0.45) < implied_prob (0.50) = negative edge

        b = decimal_odds - 1
        p = win_prob
        q = 1 - p

        # Act
        raw_kelly = (b * p - q) / b
        kelly_fraction = max(0, raw_kelly)  # Never bet on negative edge

        # Assert
        assert kelly_fraction == 0.0
        assert raw_kelly < 0  # Confirm edge is negative

    def test_kelly_fraction_with_bankroll_calculation(self):
        """
        GIVEN Kelly fraction and bankroll
        WHEN calculating bet amount
        THEN return correct dollar amount
        """
        # Arrange
        kelly_fraction = 0.05  # 5% of bankroll
        bankroll = 1000.0

        # Act
        bet_amount = kelly_fraction * bankroll

        # Assert
        assert bet_amount == 50.0

    def test_kelly_fraction_fractional_kelly(self):
        """
        GIVEN full Kelly fraction
        WHEN using fractional Kelly (e.g., half-Kelly)
        THEN reduce bet size appropriately for risk management
        """
        # Arrange
        win_prob = 0.60
        decimal_odds = 2.5
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p

        full_kelly = (b * p - q) / b

        # Act
        half_kelly = full_kelly * 0.5
        quarter_kelly = full_kelly * 0.25

        # Assert
        assert half_kelly == pytest.approx(0.133, rel=0.01)
        assert quarter_kelly == pytest.approx(0.067, rel=0.01)
        assert half_kelly < full_kelly
        assert quarter_kelly < half_kelly

    def test_kelly_fraction_max_bet_cap(self):
        """
        GIVEN Kelly fraction that exceeds maximum allowed bet
        WHEN applying bet cap
        THEN limit bet to maximum (e.g., 5% of bankroll)
        """
        # Arrange
        win_prob = 0.70  # Very high confidence
        decimal_odds = 2.0
        max_bet_fraction = 0.05  # Never risk more than 5%

        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        kelly_fraction = (b * p - q) / b

        # Act
        capped_kelly = min(kelly_fraction, max_bet_fraction)

        # Assert
        assert kelly_fraction == pytest.approx(0.40, rel=0.01)  # 40% is too aggressive
        assert capped_kelly == max_bet_fraction  # Capped at 5%

    def test_kelly_to_american_odds_conversion(self):
        """
        GIVEN decimal odds
        WHEN converting to American odds
        THEN return correct format
        """
        # Arrange
        decimal_odds_list = [2.0, 1.5, 3.0, 1.909]

        # Act & Assert
        def decimal_to_american(decimal_odds: float) -> int:
            if decimal_odds >= 2.0:
                return int((decimal_odds - 1) * 100)
            else:
                return int(-100 / (decimal_odds - 1))

        assert decimal_to_american(2.0) == 100  # Even money
        assert decimal_to_american(1.5) == -200  # Favorite
        assert decimal_to_american(3.0) == 200  # Underdog
        assert decimal_to_american(1.909) == pytest.approx(-110, abs=5)

    def test_expected_value_positive_edge(self):
        """
        GIVEN positive edge bet
        WHEN calculating expected value
        THEN return positive EV
        """
        # Arrange
        win_prob = 0.55
        decimal_odds = 2.0
        bet_amount = 100.0

        # Act
        profit_if_win = bet_amount * (decimal_odds - 1)
        loss_if_lose = bet_amount
        expected_value = (win_prob * profit_if_win) - ((1 - win_prob) * loss_if_lose)

        # Assert
        assert expected_value == pytest.approx(10.0, rel=0.01)  # $10 expected profit

    def test_expected_value_negative_edge(self):
        """
        GIVEN negative edge bet
        WHEN calculating expected value
        THEN return negative EV
        """
        # Arrange
        win_prob = 0.45
        decimal_odds = 2.0
        bet_amount = 100.0

        # Act
        profit_if_win = bet_amount * (decimal_odds - 1)
        loss_if_lose = bet_amount
        expected_value = (win_prob * profit_if_win) - ((1 - win_prob) * loss_if_lose)

        # Assert
        assert expected_value == pytest.approx(-10.0, rel=0.01)  # -$10 expected loss

    def test_kelly_criterion_edge_case_zero_probability(self):
        """
        GIVEN zero win probability
        WHEN calculating Kelly fraction
        THEN return zero (no bet)
        """
        # Arrange
        win_prob = 0.0
        decimal_odds = 10.0  # High odds but impossible to win

        # Act
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        kelly_fraction = max(0, (b * p - q) / b)

        # Assert
        assert kelly_fraction == 0.0

    def test_kelly_criterion_edge_case_certainty(self):
        """
        GIVEN 100% win probability (hypothetical)
        WHEN calculating Kelly fraction
        THEN return 1.0 (bet entire bankroll)
        """
        # Arrange
        win_prob = 1.0
        decimal_odds = 1.5  # Any odds > 1.0

        # Act
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        kelly_fraction = (b * p - q) / b

        # Assert
        assert kelly_fraction == pytest.approx(1.0, rel=0.01)

    def test_kelly_criterion_multiple_simultaneous_bets(self):
        """
        GIVEN multiple independent betting opportunities
        WHEN calculating Kelly for each
        THEN ensure total allocated doesn't exceed 100% of bankroll
        """
        # Arrange
        opportunities = [
            {"win_prob": 0.55, "decimal_odds": 2.0},  # kelly ~10%
            {"win_prob": 0.60, "decimal_odds": 2.2},  # kelly ~18%
            {"win_prob": 0.52, "decimal_odds": 2.0},  # kelly ~4%
        ]

        # Act
        kelly_fractions = []
        for opp in opportunities:
            b = opp["decimal_odds"] - 1
            p = opp["win_prob"]
            q = 1 - p
            kelly = max(0, (b * p - q) / b)
            kelly_fractions.append(kelly)

        total_allocated = sum(kelly_fractions)

        # Assert
        assert total_allocated == pytest.approx(0.32, rel=0.05)
        # In practice, might want to scale down if total > some threshold
        if total_allocated > 0.25:  # Example: max 25% total exposure
            scale_factor = 0.25 / total_allocated
            scaled_fractions = [k * scale_factor for k in kelly_fractions]
            assert sum(scaled_fractions) <= 0.25
