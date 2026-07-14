"""Force offline DEMO_MODE for the whole test session."""

import os

os.environ["DEMO_MODE"] = "1"
os.environ.pop("GROQ_API_KEY", None)
