"""
AI Travel Itinerary Planner — Main Application Entry Point
"""

import streamlit as st
from dotenv import load_dotenv
from src.core.planner import TravelPlanner
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

st.set_page_config(
    page_title="AI Travel Planner",
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

/* ── Hero ── */
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

/* ── Card ── */
.plan-card {
    background: #13131a;
    border: 1px solid #1f1f2e;
    border-radius: 18px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
}

/* ── Field label ── */
.field-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #4a4a5e;
    margin-bottom: 0.35rem;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: #0d0d12 !important;
    border: 1px solid #1f1f2e !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1rem !important;
    transition: border-color .2s, box-shadow .2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #534AB7 !important;
    box-shadow: 0 0 0 3px rgba(83,74,183,.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #3a3a4e !important; }

/* ── Pills ── */
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
    letter-spacing: 0.2px;
}

/* ── Button ── */
.stButton > button {
    width: 100% !important;
    background: #534AB7 !important;
    color: #fff !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.5rem !important;
    letter-spacing: 0.2px !important;
    transition: background .15s, transform .1s !important;
}
.stButton > button:hover {
    background: #3C3489 !important;
}
.stButton > button:active { transform: scale(.99) !important; }

/* ── Itinerary ── */
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

.time-block {
    background: #0d0d12;
    border: 1px solid #1f1f2e;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 0.75rem;
}
.block-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid #1f1f2e;
}
.block-icon {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
}
.block-icon.morning { background: #231a08; color: #EF9F27; }
.block-icon.afternoon { background: #0a1f14; color: #1D9E75; }
.block-icon.evening { background: #1a1830; color: #7F77DD; }
.block-title { font-size: 0.82rem; font-weight: 500; color: #c8c8d8; }
.block-time { font-size: 0.72rem; color: #3a3a4e; margin-left: auto; }

.block-body { padding: 0.85rem 1rem; color: #9898b0; font-size: 0.84rem; line-height: 1.7; }
.block-body strong { color: #d0d0e0; font-weight: 500; }

.food-note {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 0.5rem;
    padding: 0.45rem 0.75rem;
    background: #13131a;
    border-radius: 8px;
    font-size: 0.78rem;
    color: #6b6b7e;
}
.food-note strong { color: #a0a0b8; font-weight: 500; }

/* ── Warning ── */
.stAlert {
    background: rgba(83,74,183,.08) !important;
    border: 1px solid rgba(83,74,183,.3) !important;
    border-radius: 10px !important;
    color: #AFA9EC !important;
}

/* ── Download button ── */
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
.stDownloadButton > button:hover {
    background: #13131a !important;
    color: #9898b0 !important;
    border-color: #2e2e40 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #534AB7 !important; }

/* ── Footer ── */
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
st.markdown('<div class="hero-eyebrow">AI-Powered · LangChain · Groq</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Plan your perfect day</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Enter a city and your interests — get a full itinerary in seconds</div>',
    unsafe_allow_html=True,
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

generate = st.button("✦  Generate itinerary")

# ── Output ────────────────────────────────────────────────────────────────────
if generate:
    if not city.strip():
        st.warning("Please enter a destination city.")
    elif not interests.strip():
        st.warning("Please enter at least one interest.")
    else:
        # Pill tags
        tags = [t.strip() for t in interests.split(",") if t.strip()]
        pills = "".join(f'<span class="pill">✦ {t}</span>' for t in tags)
        st.markdown(f'<div class="interest-pills">{pills}</div>', unsafe_allow_html=True)

        with st.spinner("Crafting your perfect day…"):
            try:
                planner = TravelPlanner()
                planner.set_city(city.strip())
                planner.set_interests(interests.strip())
                itinerary = planner.create_itinerary()
                logger.info(f"Itinerary generated for '{city}'")
            except Exception as exc:
                logger.error(f"Generation failed: {exc}")
                st.error("Failed to generate itinerary. Check your GROQ_API_KEY and try again.")
                st.stop()

        # ── Itinerary output ──
        st.markdown(f"""
<div class="itin-header">
  <span class="itin-badge">📍 {city.title()}</span>
  <span class="itin-note">{' · '.join(tags)}</span>
</div>
""", unsafe_allow_html=True)

        # Render markdown itinerary content
        st.markdown(itinerary)

        # Download
        st.download_button(
            label="⬇  Download itinerary",
            data=f"Day Trip to {city.title()}\n{'─'*40}\n\n{itinerary}",
            file_name=f"itinerary_{city.lower().replace(' ','_')}.txt",
            mime="text/plain",
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tp-footer">LangChain · Groq · Llama 3.3 70B · Streamlit</div>',
    unsafe_allow_html=True,
)
