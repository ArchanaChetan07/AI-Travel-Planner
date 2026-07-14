"""
Travel planning agent loop: plan day → call tools → observe → revise once → finalize.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.agent.types import AgentState, Observation, Plan, ToolStep
from src.chains.itinerary_chain import generate_itinerary, itinerary_has_outdoor
from src.config.config import DEFAULT_BUDGET_USD, MAX_REVISIONS
from src.tools.registry import call_tool
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResult:
    state: AgentState
    status: str
    message: str = ""
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def itinerary(self) -> str:
        return self.state.itinerary


def create_tool_plan(state: AgentState, *, prefer_cheap: bool = False) -> Plan:
    """Build the observe-phase tool calls for weather, attractions, and budget."""
    return Plan(
        notes="observe",
        steps=[
            ToolStep(
                tool="weather_hint",
                args={"city": state.city},
                reason="Check outdoor suitability for the day plan.",
            ),
            ToolStep(
                tool="attractions_lookup",
                args={"city": state.city, "interests": state.interests},
                reason="Match interests to city attractions.",
            ),
            ToolStep(
                tool="budget_check",
                args={
                    "city": state.city,
                    "interests": state.interests,
                    "budget_usd": state.budget_usd,
                    "itinerary": state.draft_itinerary,
                    "prefer_cheap": prefer_cheap,
                },
                reason="Validate day-trip spend against budget.",
            ),
        ],
    )


def _apply_observation(state: AgentState, obs: Observation) -> None:
    state.observations.append(obs)
    if not obs.ok or not isinstance(obs.data, dict):
        return
    if obs.tool == "weather_hint":
        state.weather = obs.data
    elif obs.tool == "attractions_lookup":
        state.attractions = obs.data
    elif obs.tool == "budget_check":
        state.budget = obs.data


def _execute_plan(state: AgentState, plan: Plan) -> None:
    for step in plan.steps:
        try:
            result = call_tool(step.tool, **step.args)
            obs = Observation(tool=step.tool, ok=True, data=result)
            logger.info("Tool %s ok", step.tool)
        except Exception as exc:  # noqa: BLE001 — observe failures in-loop
            obs = Observation(tool=step.tool, ok=False, error=str(exc))
            logger.warning("Tool %s failed: %s", step.tool, exc)
        _apply_observation(state, obs)


def constraint_failures(state: AgentState) -> list[str]:
    """Return human-readable constraint failures that warrant a revise."""
    failures: list[str] = []
    weather = state.weather or {}
    budget = state.budget or {}

    outdoor_ok = weather.get("outdoor_ok", True)
    if outdoor_ok is False and itinerary_has_outdoor(state.draft_itinerary):
        failures.append(
            f"Weather not outdoor-friendly ({weather.get('condition', 'poor')}); "
            "replace outdoor stops with indoor alternatives."
        )
    if budget.get("ok") is False:
        shortfall = budget.get("shortfall_usd", 0)
        failures.append(
            f"Over budget by ${shortfall:.0f}; prefer free/cheap venues and simpler meals."
        )
    return failures


def run_planning_loop(
    city: str,
    interests: list[str],
    *,
    budget_usd: float | None = None,
) -> AgentResult:
    """
    Full offline-capable planning loop.

    1. Plan a day-trip itinerary (LLM or DEMO_MODE templates)
    2. Call weather_hint, attractions_lookup, budget_check
    3. Observe constraints
    4. If weather/budget fails, revise the itinerary once
    5. Finalize
    """
    state = AgentState(
        city=city.strip().title(),
        interests=[i.strip().lower() for i in interests if i and i.strip()],
        budget_usd=float(budget_usd if budget_usd is not None else DEFAULT_BUDGET_USD),
    )

    logger.info(
        "Agent loop start | city=%r interests=%s budget=%s",
        state.city,
        state.interests,
        state.budget_usd,
    )

    # ── 1. Plan day ──────────────────────────────────────────────────────────
    state.draft_itinerary = generate_itinerary(state.city, state.interests)

    # ── 2. Call tools ────────────────────────────────────────────────────────
    _execute_plan(state, create_tool_plan(state))

    # ── 3. Observe ───────────────────────────────────────────────────────────
    failures = constraint_failures(state)

    # ── 4. Revise once if needed ─────────────────────────────────────────────
    if failures and MAX_REVISIONS >= 1:
        state.revised = True
        state.revision_reason = " | ".join(failures)
        logger.info("Revising itinerary once: %s", state.revision_reason)
        state.draft_itinerary = generate_itinerary(
            state.city,
            state.interests,
            observations={
                "weather": state.weather,
                "budget": state.budget,
                "attractions": state.attractions,
                "failures": failures,
            },
            revise=True,
        )
        # Re-check budget with prefer_cheap after a budget failure
        prefer_cheap = any("budget" in f.lower() for f in failures)
        _execute_plan(state, create_tool_plan(state, prefer_cheap=prefer_cheap))

    # ── 5. Finalize ──────────────────────────────────────────────────────────
    state.itinerary = _finalize_markdown(state)
    status = "revised" if state.revised else "ok"
    message = (
        f"Itinerary revised once ({state.revision_reason})"
        if state.revised
        else "Itinerary finalized after tool checks."
    )
    return AgentResult(
        state=state,
        status=status,
        message=message,
        extras={
            "tool_calls": len(state.observations),
            "revised": state.revised,
            "weather": state.weather,
            "budget": state.budget,
            "attractions_count": (state.attractions or {}).get("count", 0),
        },
    )


def _finalize_markdown(state: AgentState) -> str:
    """Append a short agent audit trail to the itinerary for transparency."""
    weather = state.weather or {}
    budget = state.budget or {}
    attractions = state.attractions or {}
    lines = [state.draft_itinerary.rstrip(), "", "---", "### Agent checks"]
    lines.append(
        f"- **Weather:** {weather.get('condition', 'n/a')} "
        f"({weather.get('temp_c', '?')}°C) — outdoor_ok={weather.get('outdoor_ok', 'n/a')}"
    )
    lines.append(
        f"- **Attractions matched:** {attractions.get('count', 0)} "
        f"(source={attractions.get('source', 'n/a')})"
    )
    lines.append(
        f"- **Budget:** est. ${budget.get('estimated_cost_usd', '?')} "
        f"/ ${budget.get('budget_usd', state.budget_usd)} — ok={budget.get('ok', 'n/a')}"
    )
    if state.revised:
        lines.append(f"- **Revised once:** {state.revision_reason}")
    else:
        lines.append("- **Revised:** no (constraints satisfied)")
    return "\n".join(lines) + "\n"
