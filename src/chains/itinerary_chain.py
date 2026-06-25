"""
LangChain chain: generates a day-trip itinerary using Groq + Llama 3.3.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config.config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ── LLM ──────────────────────────────────────────────────────────────────────
_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    max_tokens=LLM_MAX_TOKENS,
)

# ── Prompt ────────────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are an expert travel concierge with deep knowledge of cities worldwide.
Your task is to craft a detailed, realistic day-trip itinerary for {city} tailored to the traveller's interests: {interests}.

Guidelines:
- Divide the day into logical time blocks: Morning, Afternoon, and Evening.
- For each block, suggest 2–3 activities or places with a one-sentence description.
- Include a local food or café recommendation for each block.
- Keep the tone warm, informative, and enthusiastic — like advice from a knowledgeable local friend.
- Format the output in clean Markdown with bold headings for each time block.
- Be specific: use real venue names, neighbourhoods, or landmarks where possible.
"""

_HUMAN_PROMPT = (
    "Please create a full-day itinerary for {city} focused on: {interests}."
)

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_PROMPT),
    ]
)

# ── Chain ─────────────────────────────────────────────────────────────────────
_chain = _prompt | _llm | StrOutputParser()


def generate_itinerary(city: str, interests: list[str]) -> str:
    """
    Invoke the LangChain chain and return the itinerary as a Markdown string.

    Args:
        city: The destination city.
        interests: A list of interest tags (e.g. ['food', 'art']).

    Returns:
        Markdown-formatted itinerary string.

    Raises:
        Exception: Propagates any LLM or network error to the caller.
    """
    interests_str = ", ".join(interests)
    logger.info(f"Invoking itinerary chain | city={city!r} | interests={interests_str!r}")

    result: str = _chain.invoke({"city": city, "interests": interests_str})

    logger.info("Itinerary chain completed successfully.")
    return result
