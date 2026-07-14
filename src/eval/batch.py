"""Batch evaluation helpers for DEMO_MODE agent-loop metrics."""

from __future__ import annotations

import platform
import statistics
import time
from typing import Any

from src.agent.loop import run_planning_loop
from src.config.config import DEMO_MODE, MAX_REVISIONS

REQUIRED_SECTIONS = ("**Morning**", "**Afternoon**", "**Evening**", "### Agent checks")

DEFAULT_REQUESTS: list[dict[str, Any]] = [
    {"city": "Paris", "interests": ["art", "food"], "budget_usd": 150},
    {"city": "Tokyo", "interests": ["food", "culture"], "budget_usd": 180},
    {"city": "Rome", "interests": ["history"], "budget_usd": 120},
    {"city": "Seattle", "interests": ["outdoors", "museums"], "budget_usd": 200},
    {"city": "London", "interests": ["museums", "food"], "budget_usd": 160},
    {"city": "Berlin", "interests": ["history", "art"], "budget_usd": 100},
    {"city": "Barcelona", "interests": ["outdoors", "food"], "budget_usd": 140},
    {"city": "New York", "interests": ["museums", "shopping"], "budget_usd": 220},
    {"city": "Lisbon", "interests": ["food", "history"], "budget_usd": 90},
    {"city": "Amsterdam", "interests": ["art", "museums"], "budget_usd": 130},
    {"city": "Vancouver", "interests": ["outdoors", "coffee"], "budget_usd": 150},
    {"city": "Manchester", "interests": ["museums", "food"], "budget_usd": 80},
    {"city": "Glasgow", "interests": ["outdoors", "history"], "budget_usd": 70},
    {"city": "Bergen", "interests": ["outdoors", "hiking"], "budget_usd": 100},
    {"city": "Paris", "interests": ["art", "food"], "budget_usd": 25},
    {"city": "Tokyo", "interests": ["shopping"], "budget_usd": 40},
    {"city": "Rome", "interests": ["food", "outdoors"], "budget_usd": 200},
    {"city": "London", "interests": ["history"], "budget_usd": 30},
    {"city": "Seattle", "interests": ["coffee"], "budget_usd": 120},
    {"city": "Prague", "interests": ["history", "art"], "budget_usd": 110},
    {"city": "Vienna", "interests": ["museums", "food"], "budget_usd": 160},
    {"city": "Dublin", "interests": ["history", "food"], "budget_usd": 95},
    {"city": "Madrid", "interests": ["art", "museums"], "budget_usd": 125},
    {"city": "Sydney", "interests": ["outdoors", "food"], "budget_usd": 170},
    {"city": "Singapore", "interests": ["food", "shopping"], "budget_usd": 150},
    {"city": "Seoul", "interests": ["culture", "food"], "budget_usd": 140},
    {"city": "Cairo", "interests": ["history"], "budget_usd": 80},
    {"city": "Montreal", "interests": ["food", "museums"], "budget_usd": 100},
    {"city": "Austin", "interests": ["food", "outdoors"], "budget_usd": 90},
    {"city": "Chicago", "interests": ["museums", "art"], "budget_usd": 130},
    {"city": "Oslo", "interests": ["outdoors", "museums"], "budget_usd": 150},
    {"city": "Edinburgh", "interests": ["history", "outdoors"], "budget_usd": 85},
    {"city": "Portland", "interests": ["coffee", "outdoors"], "budget_usd": 75},
    {"city": "Mexico City", "interests": ["food", "art"], "budget_usd": 70},
    {"city": "Bangkok", "interests": ["food", "culture"], "budget_usd": 60},
    {"city": "Istanbul", "interests": ["history", "food"], "budget_usd": 90},
    {"city": "Athens", "interests": ["history"], "budget_usd": 100},
    {"city": "Budapest", "interests": ["museums", "food"], "budget_usd": 85},
    {"city": "Paris", "interests": ["museums"], "budget_usd": 200},
    {"city": "Tokyo", "interests": ["outdoors", "food"], "budget_usd": 200},
]


def is_valid_itinerary(text: str) -> bool:
    if not text or not text.strip():
        return False
    return all(section in text for section in REQUIRED_SECTIONS)


def run_batch(requests: list[dict[str, Any]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    latencies: list[float] = []
    successes = 0
    revisions = 0
    errors = 0

    for i, req in enumerate(requests):
        t0 = time.perf_counter()
        row: dict[str, Any] = {"index": i, **req}
        try:
            outcome = run_planning_loop(
                req["city"],
                req["interests"],
                budget_usd=req.get("budget_usd"),
            )
            elapsed = time.perf_counter() - t0
            latencies.append(elapsed)
            valid = is_valid_itinerary(outcome.itinerary)
            revised = bool(outcome.state.revised)
            if valid:
                successes += 1
            if revised:
                revisions += 1
            row.update(
                {
                    "ok": valid,
                    "status": outcome.status,
                    "revised": revised,
                    "revision_reason": outcome.state.revision_reason,
                    "latency_s": round(elapsed, 4),
                    "tool_calls": len(outcome.state.observations),
                    "itinerary_chars": len(outcome.itinerary),
                }
            )
        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - t0
            latencies.append(elapsed)
            errors += 1
            row.update(
                {
                    "ok": False,
                    "status": "error",
                    "revised": False,
                    "error": str(exc),
                    "latency_s": round(elapsed, 4),
                }
            )
        results.append(row)

    n = len(requests)
    mean_latency = statistics.mean(latencies) if latencies else 0.0
    if len(latencies) >= 20:
        p95_latency = statistics.quantiles(latencies, n=20)[18]
    else:
        p95_latency = max(latencies or [0.0])

    return {
        "mode": "DEMO_MODE" if DEMO_MODE else "LIVE",
        "max_revisions": MAX_REVISIONS,
        "n": n,
        "success_count": successes,
        "success_rate_pct": round(100.0 * successes / n, 2) if n else 0.0,
        "revision_count": revisions,
        "revision_rate_pct": round(100.0 * revisions / n, 2) if n else 0.0,
        "error_count": errors,
        "avg_latency_s": round(mean_latency, 4),
        "p95_latency_s": round(p95_latency, 4),
        "hardware": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "results": results,
    }
