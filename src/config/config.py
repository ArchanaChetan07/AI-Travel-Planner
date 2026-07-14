"""
Configuration management — loads environment variables.
GROQ_API_KEY is optional when DEMO_MODE is on (or when the key is absent).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()

# ── Demo / offline mode ───────────────────────────────────────────────────────
# Force with DEMO_MODE=1, or auto-enable when Groq key is missing.
DEMO_MODE: bool = os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"} or not GROQ_API_KEY

# ── LLM Settings ─────────────────────────────────────────────────────────────
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# ── Planner defaults ──────────────────────────────────────────────────────────
DEFAULT_BUDGET_USD: float = float(os.getenv("DEFAULT_BUDGET_USD", "150"))
MAX_REVISIONS: int = 1

# ── App Settings ──────────────────────────────────────────────────────────────
APP_NAME: str = "AI Travel Planning Agent"
APP_VERSION: str = "2.0.0"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


def require_groq_key() -> str:
    """Return Groq API key or raise when live mode needs it."""
    if DEMO_MODE:
        return GROQ_API_KEY
    if not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Add it to .env or enable DEMO_MODE=1."
        )
    return GROQ_API_KEY
