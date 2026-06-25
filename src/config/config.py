"""
Configuration management — loads and validates environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    """Return the value of an environment variable, raising if absent."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Add it to your .env file or export it in your shell."
        )
    return value


# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = _require("GROQ_API_KEY")

# ── LLM Settings ─────────────────────────────────────────────────────────────
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# ── App Settings ──────────────────────────────────────────────────────────────
APP_NAME: str = "AI Travel Itinerary Planner"
APP_VERSION: str = "1.0.0"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
