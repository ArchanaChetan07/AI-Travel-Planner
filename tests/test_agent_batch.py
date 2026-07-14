"""Expanded DEMO_MODE harness for the plan→tools→observe→revise→finalize loop."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.agent.loop import create_tool_plan, run_planning_loop
from src.agent.types import AgentState
from src.chains.itinerary_chain import itinerary_has_outdoor
from src.config.config import DEMO_MODE, MAX_REVISIONS
from src.eval.batch import DEFAULT_REQUESTS, is_valid_itinerary, run_batch

REQUIRED = ("**Morning**", "**Afternoon**", "**Evening**", "### Agent checks")

SAMPLE_TRIPS = [
    ("Paris", ["art", "food"], 150),
    ("Tokyo", ["food"], 180),
    ("Rome", ["history"], 120),
    ("Berlin", ["art"], 100),
    ("Barcelona", ["food", "outdoors"], 140),
    ("New York", ["museums"], 200),
    ("Lisbon", ["history", "food"], 90),
    ("Amsterdam", ["museums", "art"], 130),
    ("Prague", ["history"], 110),
    ("Vienna", ["museums"], 160),
    ("Madrid", ["art"], 125),
    ("Sydney", ["outdoors", "food"], 170),
    ("Singapore", ["food"], 150),
    ("Seoul", ["culture", "food"], 140),
    ("Cairo", ["history"], 80),
    ("Montreal", ["food", "museums"], 100),
    ("Austin", ["food"], 90),
    ("Chicago", ["museums", "art"], 130),
    ("Athens", ["history"], 100),
    ("Budapest", ["food", "museums"], 85),
]


@pytest.mark.parametrize("city,interests,budget", SAMPLE_TRIPS)
def test_valid_plan_for_varied_requests(city, interests, budget):
    assert DEMO_MODE is True
    result = run_planning_loop(city, interests, budget_usd=budget)
    text = result.itinerary
    assert is_valid_itinerary(text)
    for section in REQUIRED:
        assert section in text
    assert len(result.state.observations) >= 3


def test_revise_triggers_on_rain_and_respects_budget_cap():
    result = run_planning_loop("Seattle", ["outdoors", "museums"], budget_usd=200)
    assert result.state.revised is True
    assert result.status == "revised"
    assert itinerary_has_outdoor(result.state.draft_itinerary) is False
    assert MAX_REVISIONS == 1
    assert len(result.state.observations) == 6


def test_revise_triggers_on_tight_budget():
    result = run_planning_loop("Paris", ["art", "food"], budget_usd=25)
    assert result.state.revised is True
    assert "budget" in result.state.revision_reason.lower()
    assert is_valid_itinerary(result.itinerary)


def test_finalize_schema_always_well_formed():
    for city, interests, budget in SAMPLE_TRIPS[:5]:
        result = run_planning_loop(city, interests, budget_usd=budget)
        assert is_valid_itinerary(result.itinerary)
        assert result.state.budget.get("estimated_cost_usd") is not None
        assert result.state.weather.get("outdoor_ok") is not None
        assert isinstance(result.extras.get("tool_calls"), int)


def test_create_tool_plan_has_three_tools():
    state = AgentState(city="Paris", interests=["art"], budget_usd=100)
    plan = create_tool_plan(state)
    names = [s.tool for s in plan.steps]
    assert names == ["weather_hint", "attractions_lookup", "budget_check"]


def test_batch_eval_metrics_shape():
    report = run_batch(DEFAULT_REQUESTS[:8])
    assert report["n"] == 8
    assert report["mode"] == "DEMO_MODE"
    assert report["success_rate_pct"] >= 0
    assert report["avg_latency_s"] >= 0
    assert len(report["results"]) == 8


def test_artifacts_batch_metrics_if_present():
    path = Path("artifacts/batch_metrics.json")
    if not path.exists():
        pytest.skip("Run scripts/run_batch_eval.py to generate artifacts/batch_metrics.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["mode"] == "DEMO_MODE"
    assert data["n"] >= 20
    assert 0 <= data["success_rate_pct"] <= 100
    assert data["avg_latency_s"] >= 0
