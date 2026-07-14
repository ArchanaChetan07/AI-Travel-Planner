"""
Itinerary generation — Groq LLM when available, DEMO_MODE templates otherwise.
Supports a one-shot revise path driven by tool observations.
"""

from __future__ import annotations

from typing import Any

from src.config.config import (
    DEMO_MODE,
    GROQ_API_KEY,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

_OUTDOOR_MARKERS = (
    "park",
    "garden",
    "walk",
    "hike",
    "viewpoint",
    "outdoor",
    "seine",
    "river",
    "market stroll",
    "picnic",
    "sculpture park",
    "trail",
)


def itinerary_has_outdoor(text: str) -> bool:
    lowered = (text or "").lower()
    return any(marker in lowered for marker in _OUTDOOR_MARKERS)


def _demo_itinerary(
    city: str,
    interests: list[str],
    *,
    observations: dict[str, Any] | None = None,
    revise: bool = False,
) -> str:
    interests_str = ", ".join(interests) if interests else "sightseeing"
    weather = (observations or {}).get("weather") or {}
    budget = (observations or {}).get("budget") or {}
    outdoor_ok = weather.get("outdoor_ok", True)
    budget_ok = budget.get("ok", True)

    force_indoor = revise and outdoor_ok is False
    force_cheap = revise and budget_ok is False

    if force_indoor and force_cheap:
        morning = (
            f"- Explore the main free indoor museum in {city}\n"
            f"- Coffee at a neighbourhood café (budget pick)"
        )
        afternoon = (
            f"- Browse a covered market or arcade in {city}\n"
            f"- Interest focus ({interests_str}): indoor galleries / archives"
        )
        evening = (
            f"- Affordable local eatery near the centre of {city}\n"
            f"- Evening stroll under covered walkways if rain continues"
        )
        note = (
            f"*DEMO_MODE revise:* indoor + budget-friendly plan "
            f"(weather={weather.get('condition', 'n/a')}, "
            f"est=${budget.get('estimated_cost_usd', '?')}).*"
        )
    elif force_indoor:
        morning = (
            f"- Start at a flagship indoor museum in {city}\n"
            f"- Café stop nearby — skip outdoor plazas while it's wet"
        )
        afternoon = (
            f"- {interests_str.title()} indoors: galleries, workshops, or covered markets\n"
            f"- Optional short transfers between venues (avoid long walks)"
        )
        evening = (
            f"- Dinner at a renowned indoor restaurant in {city}\n"
            f"- Nightcap at a cocktail bar / jazz club"
        )
        note = (
            f"*DEMO_MODE revise:* weather-aware indoor plan "
            f"({weather.get('condition', 'poor weather')}).*"
        )
    elif force_cheap:
        morning = (
            f"- Free overlook / old-town walk in {city}\n"
            f"- Bakery breakfast (~$8)"
        )
        afternoon = (
            f"- Free or donation-based sites matching {interests_str}\n"
            f"- Public park picnic instead of a sit-down lunch"
        )
        evening = (
            f"- Street-food dinner near transit in {city}\n"
            f"- Sunset from a free public viewpoint"
        )
        note = (
            f"*DEMO_MODE revise:* budget plan "
            f"(target under ${budget.get('budget_usd', '?')}).*"
        )
    else:
        morning = (
            f"- Landmark introduction walk through central {city}\n"
            f"- Breakfast spot recommended for {interests_str} travellers"
        )
        afternoon = (
            f"- Hands-on {interests_str} activity (museum, market, or trail)\n"
            f"- Mid-afternoon café with a local specialty"
        )
        evening = (
            f"- Signature evening experience in {city}\n"
            f"- Dinner highlighting regional cuisine"
        )
        note = "*DEMO_MODE template itinerary (no Groq key required).*"

    return f"""**Morning**
{morning}

**Afternoon**
{afternoon}

**Evening**
{evening}

{note}
"""


def _llm_itinerary(
    city: str,
    interests: list[str],
    *,
    observations: dict[str, Any] | None = None,
    revise: bool = False,
) -> str:
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_groq import ChatGroq

    interests_str = ", ".join(interests)
    constraints = ""
    if revise and observations:
        weather = observations.get("weather") or {}
        budget = observations.get("budget") or {}
        failures = observations.get("failures") or []
        constraints = (
            "\nRevision constraints (MUST satisfy):\n"
            f"- Weather: {weather}\n"
            f"- Budget: {budget}\n"
            f"- Failures: {failures}\n"
            "Prefer indoor venues if outdoor_ok is false. "
            "Prefer free/cheap options if over budget."
        )

    system = (
        "You are an expert travel concierge. Craft a realistic day-trip itinerary "
        "for {city} tailored to interests: {interests}.\n"
        "Divide into Morning, Afternoon, Evening with 2–3 specific places each, "
        "local food notes, and clean Markdown bold headings."
        f"{constraints}"
    )
    human = (
        "Create a full-day itinerary for {city} focused on: {interests}."
        + (" Revise to satisfy the constraint list." if revise else "")
    )

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", human),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"city": city, "interests": interests_str})


def generate_itinerary(
    city: str,
    interests: list[str],
    *,
    observations: dict[str, Any] | None = None,
    revise: bool = False,
) -> str:
    """
    Generate (or revise) a Markdown day-trip itinerary.

    Uses DEMO_MODE templates when Groq is unavailable; otherwise calls Groq.
    """
    interests = [i.strip().lower() for i in interests if i and str(i).strip()]
    logger.info(
        "generate_itinerary | city=%r interests=%s revise=%s demo=%s",
        city,
        interests,
        revise,
        DEMO_MODE,
    )

    if DEMO_MODE or not GROQ_API_KEY:
        return _demo_itinerary(
            city, interests, observations=observations, revise=revise
        )

    try:
        return _llm_itinerary(
            city, interests, observations=observations, revise=revise
        )
    except Exception as exc:
        logger.warning("LLM itinerary failed (%s); falling back to DEMO template.", exc)
        return _demo_itinerary(
            city, interests, observations=observations, revise=revise
        )
