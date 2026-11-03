import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    # Bound request time and SDK retries so one slow API call cannot stall
    # the continuous monitoring loop for too long.
    return Groq(
        api_key=api_key,
        timeout=30.0,
        max_retries=1,
    )
