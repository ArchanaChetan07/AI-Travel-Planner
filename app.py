"""
AI Travel Planning Agent — Streamlit entry point.

Runs a tool-loop planner: plan day → weather/attractions/budget tools →
observe → revise once if constraints fail → finalize.
"""

import streamlit as st
from dotenv import load_dotenv

from src.config.config import DEFAULT_BUDGET_USD, DEMO_MODE
from src.core.planner import TravelPlanner
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

st.set_page_config(
    page_title="AI Travel Planning Agent",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background: #0d0d12;
    min-height: 100vh;
}

.hero-eyebrow {
    text-align: center;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #7F77DD;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.75rem;
    font-weight: 400;
    color: #f0eefc;
    text-align: center;
    line-height: 1.15;
    margin-bottom: 0.6rem;
    letter-spacing: -0.5px;
}
.hero-sub {
    text-align: center;
    color: #6b6b7e;
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 2.5rem;
}

.field-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #4a4a5e;
    margin-bottom: 0.35rem;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #0d0d12 !important;
    border: 1px solid #1f1f2e !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1rem !important;
}

.stButton > button {
    width: 100% !important;
    background: #534AB7 !important;
    color: #fff !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.5rem !important;
}

.interest-pills { display: flex; flex-wrap: wrap; gap: 7px; margin: 0.5rem 0 1.5rem; }
.pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 999px;
    border: 1px solid #2e2b5a;
    background: #1a1830;
    color: #AFA9EC;
    font-size: 0.78rem;
    font-weight: 500;
}

.itin-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.25rem;
}
.itin-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 13px;
    background: #0e2e1f;
    border: 1px solid #1D9E75;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #5DCAA5;
}
.itin-note { font-size: 0.75rem; color: #3a3a4e; margin-left: auto; }

.stDownloadButton > button {
    width: 100% !important;
    background: transparent !important;
    color: #4a4a5e !important;
    border: 1px solid #1f1f2e !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    padding: 0.55rem !important;
    margin-top: 0.75rem !important;
}

.tp-footer {
    text-align: center;
    color: #2a2a38;
    font-size: 0.72rem;
    margin-top: 2.5rem;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-eyebrow">Planning Agent · Tools · Observe · Revise</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="hero-title">Plan your perfect day</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">City + interests → weather, attractions &amp; budget tools → '
    "revised itinerary</div>",
    unsafe_allow_html=True,
)

if DEMO_MODE:
    st.info(
        "Running in **DEMO_MODE** (no Groq key or DEMO_MODE=1). "
        "Uses template itineraries plus stub tools — fully offline."
    )

# ── Form ──────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="medium")
with col1:
    st.markdown('<div class="field-label">📍 Destination</div>', unsafe_allow_html=True)
    city = st.text_input("city", placeholder="Tokyo, Rome, Kyoto…", label_visibility="collapsed")
with col2:
    st.markdown('<div class="field-label">✦ Interests</div>', unsafe_allow_html=True)
    interests = st.text_input(
        "interests", placeholder="food, museums, hiking…", label_visibility="collapsed"
    )

st.markdown('<div class="field-label">💵 Day budget (USD)</div>', unsafe_allow_html=True)
budget = st.number_input(
    "budget",
    min_value=10.0,
    max_value=2000.0,
    value=float(DEFAULT_BUDGET_USD),
    step=10.0,
    label_visibility="collapsed",
)

generate = st.button("✦  Generate itinerary")

# ── Output ────────────────────────────────────────────────────────────────────
if generate:
    if not city.strip():
        st.warning("Please enter a destination city.")
    elif not interests.strip():
        st.warning("Please enter at least one interest.")
    else:
        tags = [t.strip() for t in interests.split(",") if t.strip()]
        pills = "".join(f'<span class="pill">✦ {t}</span>' for t in tags)
        st.markdown(f'<div class="interest-pills">{pills}</div>', unsafe_allow_html=True)

        with st.spinner("Planning with tools…"):
            try:
                planner = TravelPlanner()
                planner.set_city(city.strip())
                planner.set_interests(interests.strip())
                planner.set_budget(budget)
                itinerary = planner.create_itinerary()
                logger.info("Itinerary generated for '%s'", city)
            except Exception as exc:
                logger.error("Generation failed: %s", exc)
                st.error(
                    "Failed to generate itinerary. "
                    "In live mode check GROQ_API_KEY, or set DEMO_MODE=1."
                )
                st.stop()

        badge_extra = ""
        if planner.last_result and planner.last_result.state.revised:
            badge_extra = " · revised"

        st.markdown(
            f"""
<div class="itin-header">
  <span class="itin-badge">📍 {city.title()}{badge_extra}</span>
  <span class="itin-note">{' · '.join(tags)} · ${float(budget):.0f}</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(itinerary)

        st.download_button(
            label="⬇  Download itinerary",
            data=f"Day Trip to {city.title()}\n{'─'*40}\n\n{itinerary}",
            file_name=f"itinerary_{city.lower().replace(' ', '_')}.txt",
            mime="text/plain",
        )

st.markdown(
    '<div class="tp-footer">Tool-loop agent · weather · attractions · budget · Streamlit</div>',
    unsafe_allow_html=True,
)
