"""
Core domain object: TravelPlanner.

Orchestrates the itinerary-generation workflow, maintains conversation
state, and wraps all errors in TravelPlannerException for clean
propagation to the UI layer.
"""

from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from src.chains.itinerary_chain import generate_itinerary
from src.utils.logger import get_logger
from src.utils.custom_exception import TravelPlannerException

logger = get_logger(__name__)


@dataclass
class TravelPlanner:
    """
    Stateful planner that holds city, interests, and message history
    for a single planning session.
    """

    city: str = ""
    interests: list[str] = field(default_factory=list)
    itinerary: str = ""
    messages: list[BaseMessage] = field(default_factory=list)

    def __post_init__(self) -> None:
        logger.info("TravelPlanner session initialised.")

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------
    def set_city(self, city: str) -> None:
        """Set and validate the destination city."""
        if not city or not city.strip():
            raise ValueError("City name must not be empty.")
        try:
            self.city = city.strip().title()
            self.messages.append(HumanMessage(content=f"Destination: {self.city}"))
            logger.info(f"City set to '{self.city}'.")
        except Exception as exc:
            logger.error(f"Failed to set city: {exc}")
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
            logger.info(f"Interests set: {self.interests}")
        except Exception as exc:
            logger.error(f"Failed to set interests: {exc}")
            raise TravelPlannerException("Failed to set interests.", exc) from exc

    # ------------------------------------------------------------------
    # Main action
    # ------------------------------------------------------------------
    def create_itinerary(self) -> str:
        """
        Generate and store the day-trip itinerary.

        Returns:
            Markdown-formatted itinerary string.

        Raises:
            TravelPlannerException: If generation fails.
        """
        if not self.city:
            raise TravelPlannerException("City must be set before creating an itinerary.")
        if not self.interests:
            raise TravelPlannerException("Interests must be set before creating an itinerary.")

        try:
            logger.info(
                f"Generating itinerary for city='{self.city}', "
                f"interests={self.interests}."
            )
            result = generate_itinerary(self.city, self.interests)
            self.itinerary = result
            self.messages.append(AIMessage(content=result))
            logger.info("Itinerary generated and stored successfully.")
            return result
        except Exception as exc:
            logger.error(f"Itinerary generation failed: {exc}")
            raise TravelPlannerException(
                f"Failed to generate itinerary for '{self.city}'.", exc
            ) from exc

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Clear session state for reuse."""
        self.city = ""
        self.interests = []
        self.itinerary = ""
        self.messages = []
        logger.info("TravelPlanner session reset.")

    def __repr__(self) -> str:
        return (
            f"TravelPlanner(city={self.city!r}, "
            f"interests={self.interests!r}, "
            f"has_itinerary={bool(self.itinerary)})"
        )
