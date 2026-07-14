"""
Unit tests for TravelPlanner, tools, and the agent loop.
Run with: pytest tests/ -v --cov=src
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.agent.loop import constraint_failures, run_planning_loop
from src.core.planner import TravelPlanner
from src.tools.registry import attractions_lookup, budget_check, call_tool, weather_hint
from src.utils.custom_exception import TravelPlannerException


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


# ── Tests: budget ─────────────────────────────────────────────────────────────
class TestSetBudget:
    def test_sets_budget(self, planner):
        planner.set_budget(80)
        assert planner.budget_usd == 80.0

    def test_non_positive_raises(self, planner):
        with pytest.raises(ValueError):
            planner.set_budget(0)


# ── Tests: create_itinerary (agent loop) ──────────────────────────────────────
class TestCreateItinerary:
    def test_returns_itinerary_string(self, planner):
        planner.set_city("Paris")
        planner.set_interests("art, food")
        result = planner.create_itinerary()
        assert "Morning" in result
        assert "Agent checks" in result

    def test_stores_itinerary(self, planner):
        planner.set_city("Paris")
        planner.set_interests("art")
        planner.create_itinerary()
        assert planner.itinerary
        assert planner.last_result is not None

    def test_ai_message_appended(self, planner):
        planner.set_city("Rome")
        planner.set_interests("history")
        planner.create_itinerary()
        assert len(planner.messages) == 3

    def test_raises_without_city(self, planner):
        planner.set_interests("food")
        with pytest.raises(TravelPlannerException):
            planner.create_itinerary()

    def test_raises_without_interests(self, planner):
        planner.set_city("Tokyo")
        with pytest.raises(TravelPlannerException):
            planner.create_itinerary()

    @patch("src.core.planner.run_planning_loop", side_effect=RuntimeError("boom"))
    def test_loop_failure_raises_custom_exception(self, _mock_loop, planner):
        planner.set_city("London")
        planner.set_interests("theatre")
        with pytest.raises(TravelPlannerException):
            planner.create_itinerary()


# ── Tests: reset ─────────────────────────────────────────────────────────────
class TestReset:
    def test_reset_clears_state(self, planner):
        planner.set_city("Berlin")
        planner.set_interests("music")
        planner.set_budget(90)
        planner.create_itinerary()
        planner.reset()
        assert planner.city == ""
        assert planner.interests == []
        assert planner.itinerary == ""
        assert planner.messages == []
        assert planner.last_result is None


# ── Tests: tools ─────────────────────────────────────────────────────────────
class TestTools:
    def test_weather_hint_rainy_city(self):
        result = weather_hint("Seattle")
        assert result["outdoor_ok"] is False
        assert result["source"] == "stub"

    def test_weather_hint_clear_city(self):
        result = weather_hint("Paris")
        assert result["outdoor_ok"] is True

    def test_attractions_lookup_matches_interests(self):
        result = attractions_lookup("Paris", ["art", "food"])
        assert result["count"] >= 2
        names = {a["name"] for a in result["attractions"]}
        assert "Louvre Museum" in names

    def test_budget_check_fails_when_tight(self):
        result = budget_check("Paris", ["art", "food"], budget_usd=20)
        assert result["ok"] is False
        assert result["shortfall_usd"] > 0

    def test_budget_check_ok_generous(self):
        result = budget_check("Paris", ["art"], budget_usd=500, prefer_cheap=True)
        assert result["ok"] is True

    def test_call_tool_unknown_raises(self):
        with pytest.raises(KeyError):
            call_tool("not_a_real_tool")


# ── Tests: agent loop ────────────────────────────────────────────────────────
class TestAgentLoop:
    def test_sunny_city_no_revise_needed(self):
        result = run_planning_loop("Tokyo", ["food"], budget_usd=200)
        assert result.state.itinerary
        assert "Agent checks" in result.itinerary
        # Tokyo weather is fine; generous budget should not force revise
        assert result.state.revised is False
        assert result.status == "ok"

    def test_rainy_city_revises_once(self):
        result = run_planning_loop("Seattle", ["outdoors", "museums"], budget_usd=200)
        assert result.state.revised is True
        assert result.status == "revised"
        assert "revise" in result.itinerary.lower() or "indoor" in result.itinerary.lower()
        assert result.state.weather.get("outdoor_ok") is False

    def test_tight_budget_revises_once(self):
        result = run_planning_loop("Paris", ["art", "food"], budget_usd=25)
        assert result.state.revised is True
        assert "budget" in result.state.revision_reason.lower()

    def test_constraint_failures_detects_weather(self):
        from src.agent.types import AgentState

        state = AgentState(
            city="Seattle",
            interests=["outdoors"],
            draft_itinerary="Morning park walk and viewpoint hike",
            weather={"outdoor_ok": False, "condition": "rain"},
            budget={"ok": True},
        )
        failures = constraint_failures(state)
        assert any("weather" in f.lower() or "outdoor" in f.lower() for f in failures)
