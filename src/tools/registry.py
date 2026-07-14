"""
Tool registry for the travel planning agent.

Tools are deterministic stubs suitable for offline DEMO_MODE.
attractions_lookup may optionally hit a live Nominatim-free city catalogue;
no network is required for tests.
"""

from __future__ import annotations

from typing import Any, Callable

ToolFn = Callable[..., Any]

# Cities known for frequent rain / grey weather (outdoor_ok=False).
_RAINY_CITIES = {
    "seattle",
    "london",
    "vancouver",
    "manchester",
    "bergen",
    "glasgow",
}

# Curated attraction catalogues keyed by normalized city name.
_ATTRACTION_CATALOGUE: dict[str, dict[str, list[dict[str, Any]]]] = {
    "paris": {
        "art": [
            {"name": "Louvre Museum", "cost_usd": 22, "outdoor": False},
            {"name": "Musée d'Orsay", "cost_usd": 16, "outdoor": False},
        ],
        "food": [
            {"name": "Le Marais food walk", "cost_usd": 35, "outdoor": True},
            {"name": "Café de Flore", "cost_usd": 28, "outdoor": False},
        ],
        "history": [
            {"name": "Notre-Dame exterior & Île de la Cité", "cost_usd": 0, "outdoor": True},
            {"name": "Sainte-Chapelle", "cost_usd": 13, "outdoor": False},
        ],
        "museums": [
            {"name": "Centre Pompidou", "cost_usd": 15, "outdoor": False},
        ],
        "outdoors": [
            {"name": "Jardin du Luxembourg", "cost_usd": 0, "outdoor": True},
            {"name": "Seine river walk", "cost_usd": 0, "outdoor": True},
        ],
    },
    "tokyo": {
        "food": [
            {"name": "Tsukiji Outer Market", "cost_usd": 25, "outdoor": True},
            {"name": "Ramen alley (Shinjuku)", "cost_usd": 18, "outdoor": False},
        ],
        "culture": [
            {"name": "Meiji Shrine", "cost_usd": 0, "outdoor": True},
            {"name": "TeamLab Planets", "cost_usd": 32, "outdoor": False},
        ],
        "shopping": [
            {"name": "Shimokitazawa thrift row", "cost_usd": 40, "outdoor": True},
        ],
        "outdoors": [
            {"name": "Yoyogi Park", "cost_usd": 0, "outdoor": True},
        ],
    },
    "rome": {
        "history": [
            {"name": "Colosseum", "cost_usd": 24, "outdoor": True},
            {"name": "Pantheon", "cost_usd": 5, "outdoor": False},
        ],
        "food": [
            {"name": "Trastevere trattoria crawl", "cost_usd": 40, "outdoor": True},
            {"name": "Gelateria Della Palma", "cost_usd": 8, "outdoor": False},
        ],
        "art": [
            {"name": "Vatican Museums", "cost_usd": 25, "outdoor": False},
        ],
        "outdoors": [
            {"name": "Villa Borghese gardens", "cost_usd": 0, "outdoor": True},
        ],
    },
    "seattle": {
        "coffee": [
            {"name": "Pike Place Market cafés", "cost_usd": 15, "outdoor": False},
        ],
        "outdoors": [
            {"name": "Kerry Park viewpoint", "cost_usd": 0, "outdoor": True},
            {"name": "Olympic Sculpture Park", "cost_usd": 0, "outdoor": True},
        ],
        "museums": [
            {"name": "Museum of Pop Culture", "cost_usd": 30, "outdoor": False},
            {"name": "Chihuly Garden and Glass", "cost_usd": 32, "outdoor": False},
        ],
        "food": [
            {"name": "Pike Place Market lunch", "cost_usd": 22, "outdoor": False},
        ],
    },
    "london": {
        "museums": [
            {"name": "British Museum", "cost_usd": 0, "outdoor": False},
            {"name": "Tate Modern", "cost_usd": 0, "outdoor": False},
        ],
        "history": [
            {"name": "Tower of London", "cost_usd": 35, "outdoor": True},
            {"name": "Westminster Abbey", "cost_usd": 30, "outdoor": False},
        ],
        "food": [
            {"name": "Borough Market", "cost_usd": 25, "outdoor": True},
            {"name": "Dishoom Covent Garden", "cost_usd": 30, "outdoor": False},
        ],
        "outdoors": [
            {"name": "Hyde Park stroll", "cost_usd": 0, "outdoor": True},
        ],
    },
}

_GENERIC_BY_INTEREST: dict[str, list[dict[str, Any]]] = {
    "food": [
        {"name": "Local market food tour", "cost_usd": 30, "outdoor": True},
        {"name": "Neighbourhood café tasting", "cost_usd": 20, "outdoor": False},
    ],
    "art": [
        {"name": "City art museum", "cost_usd": 18, "outdoor": False},
        {"name": "Street art walk", "cost_usd": 0, "outdoor": True},
    ],
    "museums": [
        {"name": "Main city museum", "cost_usd": 15, "outdoor": False},
    ],
    "history": [
        {"name": "Historic old town walk", "cost_usd": 0, "outdoor": True},
        {"name": "City history centre", "cost_usd": 12, "outdoor": False},
    ],
    "outdoors": [
        {"name": "Central park / gardens", "cost_usd": 0, "outdoor": True},
        {"name": "Scenic viewpoint", "cost_usd": 0, "outdoor": True},
    ],
    "hiking": [
        {"name": "City trail hike", "cost_usd": 0, "outdoor": True},
    ],
    "shopping": [
        {"name": "Central shopping district", "cost_usd": 50, "outdoor": True},
    ],
    "coffee": [
        {"name": "Specialty coffee crawl", "cost_usd": 18, "outdoor": False},
    ],
}


def weather_hint(city: str) -> dict[str, Any]:
    """
    Return a weather hint for the destination (stub / demo).

    rainy cities → outdoor_ok=False so the agent can revise outdoor plans.
    """
    key = (city or "").strip().lower()
    rainy = key in _RAINY_CITIES
    if rainy:
        condition = "steady rain"
        temp_c = 11
        outdoor_ok = False
        advice = "Prefer indoor venues; pack a rain jacket."
    else:
        condition = "partly cloudy"
        temp_c = 22
        outdoor_ok = True
        advice = "Good day for mixed indoor/outdoor plans."

    return {
        "city": (city or "").strip().title(),
        "condition": condition,
        "temp_c": temp_c,
        "outdoor_ok": outdoor_ok,
        "advice": advice,
        "source": "stub",
    }


def attractions_lookup(city: str, interests: list[str] | None = None) -> dict[str, Any]:
    """
    Match city + interests to curated attractions (stub catalogue).

    Falls back to generic interest templates when the city is unknown.
    """
    interests = [i.strip().lower() for i in (interests or []) if i and i.strip()]
    city_key = (city or "").strip().lower()
    city_catalog = _ATTRACTION_CATALOGUE.get(city_key, {})

    matched: list[dict[str, Any]] = []
    for interest in interests or ["sightseeing"]:
        pool = city_catalog.get(interest) or _GENERIC_BY_INTEREST.get(
            interest,
            [{"name": f"{interest.title()} highlight in {city}", "cost_usd": 20, "outdoor": False}],
        )
        for item in pool:
            entry = dict(item)
            entry["interest"] = interest
            matched.append(entry)

    # Deduplicate by name while preserving order
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in matched:
        name = item["name"]
        if name not in seen:
            seen.add(name)
            unique.append(item)

    return {
        "city": (city or "").strip().title(),
        "interests": interests,
        "attractions": unique,
        "count": len(unique),
        "source": "catalogue" if city_key in _ATTRACTION_CATALOGUE else "generic",
    }


def budget_check(
    city: str,
    interests: list[str] | None = None,
    budget_usd: float = 150.0,
    itinerary: str = "",
    prefer_cheap: bool = False,
) -> dict[str, Any]:
    """
    Estimate day-trip cost from attractions (and optional itinerary hints)
    and compare against budget_usd.
    """
    lookup = attractions_lookup(city, interests)
    attractions = list(lookup["attractions"])

    if prefer_cheap:
        attractions = sorted(attractions, key=lambda a: float(a.get("cost_usd", 0)))
        attractions = [a for a in attractions if float(a.get("cost_usd", 0)) <= 20] or attractions[:3]

    # Base living cost + selected attractions (cap at 4 stops for a day trip)
    selected = attractions[:4]
    activities_cost = sum(float(a.get("cost_usd", 0)) for a in selected)
    meals = 35.0 if prefer_cheap else 55.0
    transit = 10.0 if prefer_cheap else 18.0

    # Outdoor-heavy itinerary wording can bump cost slightly (cafés / venues)
    text = (itinerary or "").lower()
    if "fine dining" in text or "tasting menu" in text:
        meals += 40.0
    if "river cruise" in text or "hop-on" in text:
        activities_cost += 25.0

    estimated = round(activities_cost + meals + transit, 2)
    ok = estimated <= float(budget_usd)
    shortfall = round(max(0.0, estimated - float(budget_usd)), 2)

    return {
        "city": (city or "").strip().title(),
        "budget_usd": float(budget_usd),
        "estimated_cost_usd": estimated,
        "ok": ok,
        "shortfall_usd": shortfall,
        "selected": selected,
        "prefer_cheap": prefer_cheap,
        "advice": (
            "Within budget."
            if ok
            else f"Over budget by ${shortfall:.0f}; switch to free/cheap indoor stops."
        ),
    }


TOOLS: dict[str, ToolFn] = {
    "weather_hint": weather_hint,
    "attractions_lookup": attractions_lookup,
    "budget_check": budget_check,
}


def call_tool(name: str, **kwargs: Any) -> Any:
    if name not in TOOLS:
        raise KeyError(f"Unknown tool: {name}")
    return TOOLS[name](**kwargs)
