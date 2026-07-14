"""Shared types for the travel planning agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolStep:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class Plan:
    steps: list[ToolStep] = field(default_factory=list)
    notes: str = ""


@dataclass
class Observation:
    tool: str
    ok: bool
    data: Any = None
    error: str = ""


@dataclass
class AgentState:
    city: str
    interests: list[str] = field(default_factory=list)
    budget_usd: float = 150.0
    draft_itinerary: str = ""
    itinerary: str = ""
    observations: list[Observation] = field(default_factory=list)
    weather: dict[str, Any] = field(default_factory=dict)
    attractions: dict[str, Any] = field(default_factory=dict)
    budget: dict[str, Any] = field(default_factory=dict)
    revised: bool = False
    revision_reason: str = ""
