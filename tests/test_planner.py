"""
Unit tests for TravelPlanner core class.
Run with: pytest tests/ -v --cov=src
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.planner import TravelPlanner
from src.utils.custom_exception import TravelPlannerException


# ── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture
def planner():
    return TravelPlanner()


MOCK_ITINERARY = """
**Morning**
- Visit the Eiffel Tower at sunrise.

**Afternoon**
- Explore the Louvre Museum.

**Evening**
- Dinner at a Seine-side bistro.
"""


# ── Tests: set_city ───────────────────────────────────────────────────────────
class TestSetCity:
    def test_valid_city_is_stored(self, planner):
        planner.set_city("paris")
        assert planner.city == "Paris"

    def test_city_is_title_cased(self, planner):
        planner.set_city("new york")
        assert planner.city == "New York"

    def test_empty_city_raises(self, planner):
        with pytest.raises((ValueError, TravelPlannerException)):
            planner.set_city("")

    def test_whitespace_city_raises(self, planner):
        with pytest.raises((ValueError, TravelPlannerException)):
            planner.set_city("   ")

    def test_message_appended(self, planner):
        planner.set_city("Tokyo")
        assert len(planner.messages) == 1


# ── Tests: set_interests ──────────────────────────────────────────────────────
class TestSetInterests:
    def test_comma_separated_parsed(self, planner):
        planner.set_interests("food, art, museums")
        assert planner.interests == ["food", "art", "museums"]

    def test_empty_string_raises(self, planner):
        with pytest.raises((ValueError, TravelPlannerException)):
            planner.set_interests("")

    def test_single_interest(self, planner):
        planner.set_interests("hiking")
        assert planner.interests == ["hiking"]

    def test_message_appended(self, planner):
        planner.set_interests("food, art")
        assert len(planner.messages) == 1


# ── Tests: create_itinerary ───────────────────────────────────────────────────
class TestCreateItinerary:
    @patch("src.core.planner.generate_itinerary", return_value=MOCK_ITINERARY)
    def test_returns_itinerary_string(self, mock_gen, planner):
        planner.set_city("Paris")
        planner.set_interests("art, food")
        result = planner.create_itinerary()
        assert result == MOCK_ITINERARY

    @patch("src.core.planner.generate_itinerary", return_value=MOCK_ITINERARY)
    def test_stores_itinerary(self, mock_gen, planner):
        planner.set_city("Paris")
        planner.set_interests("art")
        planner.create_itinerary()
        assert planner.itinerary == MOCK_ITINERARY

    @patch("src.core.planner.generate_itinerary", return_value=MOCK_ITINERARY)
    def test_ai_message_appended(self, mock_gen, planner):
        planner.set_city("Rome")
        planner.set_interests("history")
        planner.create_itinerary()
        # city msg + interests msg + AI response = 3
        assert len(planner.messages) == 3

    def test_raises_without_city(self, planner):
        planner.set_interests("food")
        with pytest.raises(TravelPlannerException):
            planner.create_itinerary()

    def test_raises_without_interests(self, planner):
        planner.set_city("Tokyo")
        with pytest.raises(TravelPlannerException):
            planner.create_itinerary()

    @patch("src.core.planner.generate_itinerary", side_effect=RuntimeError("API error"))
    def test_llm_failure_raises_custom_exception(self, mock_gen, planner):
        planner.set_city("London")
        planner.set_interests("theatre")
        with pytest.raises(TravelPlannerException):
            planner.create_itinerary()


# ── Tests: reset ─────────────────────────────────────────────────────────────
class TestReset:
    @patch("src.core.planner.generate_itinerary", return_value=MOCK_ITINERARY)
    def test_reset_clears_state(self, mock_gen, planner):
        planner.set_city("Berlin")
        planner.set_interests("music")
        planner.create_itinerary()
        planner.reset()
        assert planner.city == ""
        assert planner.interests == []
        assert planner.itinerary == ""
        assert planner.messages == []
