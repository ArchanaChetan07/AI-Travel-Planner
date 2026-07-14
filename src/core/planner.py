"""
Core domain object: TravelPlanner.

Validates inputs and runs the tool-loop planning agent
(plan → tools → observe → revise once → finalize).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from src.agent.loop import AgentResult, run_planning_loop
from src.config.config import DEFAULT_BUDGET_USD
from src.utils.custom_exception import TravelPlannerException
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TravelPlanner:
    """
    Stateful planner that holds city, interests, budget, and message history
    for a single planning session.
    """

    city: str = ""
    interests: list[str] = field(default_factory=list)
    budget_usd: float = DEFAULT_BUDGET_USD
    itinerary: str = ""
    last_result: AgentResult | None = None
    messages: list[BaseMessage] = field(default_factory=list)

    def __post_init__(self) -> None:
        logger.info("TravelPlanner session initialised.")

    def set_city(self, city: str) -> None:
        """Set and validate the destination city."""
        if not city or not city.strip():
            raise ValueError("City name must not be empty.")
        try:
            self.city = city.strip().title()
            self.messages.append(HumanMessage(content=f"Destination: {self.city}"))
            logger.info("City set to '%s'.", self.city)
        except Exception as exc:
            logger.error("Failed to set city: %s", exc)
            raise TravelPlannerException("Failed to set destination city.", exc) from exc

    def set_interests(self, interests_input: str) -> None:
        """Parse and store a comma-separated interests string."""
        if not interests_input or not interests_input.strip():
            raise ValueError("At least one interest must be provided.")
        try:
            self.interests = [
                tag.strip().lower()
                for tag in interests_input.split(",")
                if tag.strip()
            ]
            self.messages.append(
                HumanMessage(content=f"Interests: {', '.join(self.interests)}")
            )
            logger.info("Interests set: %s", self.interests)
        except Exception as exc:
            logger.error("Failed to set interests: %s", exc)
            raise TravelPlannerException("Failed to set interests.", exc) from exc

    def set_budget(self, budget_usd: float | int | str) -> None:
        """Set day-trip budget in USD."""
        try:
            value = float(budget_usd)
        except (TypeError, ValueError) as exc:
            raise ValueError("Budget must be a number.") from exc
        if value <= 0:
            raise ValueError("Budget must be positive.")
        self.budget_usd = value
        self.messages.append(HumanMessage(content=f"Budget: ${self.budget_usd:.0f}"))
        logger.info("Budget set to $%s.", self.budget_usd)

    def create_itinerary(self) -> str:
        """
        Run the planning agent loop and store the finalized itinerary.

        Returns:
            Markdown-formatted itinerary string.

        Raises:
            TravelPlannerException: If generation fails.
        """
        if not self.city:
            raise TravelPlannerException("City must be set before creating an itinerary.")
        if not self.interests:
            raise TravelPlannerException(
                "Interests must be set before creating an itinerary."
            )

        try:
            logger.info(
                "Running agent loop for city=%r interests=%s budget=%s",
                self.city,
                self.interests,
                self.budget_usd,
            )
            result = run_planning_loop(
                self.city,
                self.interests,
                budget_usd=self.budget_usd,
            )
            self.last_result = result
            self.itinerary = result.itinerary
            self.messages.append(AIMessage(content=self.itinerary))
            logger.info("Itinerary finalized status=%s", result.status)
            return self.itinerary
        except Exception as exc:
            logger.error("Itinerary generation failed: %s", exc)
            raise TravelPlannerException(
                f"Failed to generate itinerary for '{self.city}'.", exc
            ) from exc

    def reset(self) -> None:
        """Clear session state for reuse."""
        self.city = ""
        self.interests = []
        self.budget_usd = DEFAULT_BUDGET_USD
        self.itinerary = ""
        self.last_result = None
        self.messages = []
        logger.info("TravelPlanner session reset.")

    def __repr__(self) -> str:
        return (
            f"TravelPlanner(city={self.city!r}, "
            f"interests={self.interests!r}, "
            f"budget_usd={self.budget_usd!r}, "
            f"has_itinerary={bool(self.itinerary)})"
        )
