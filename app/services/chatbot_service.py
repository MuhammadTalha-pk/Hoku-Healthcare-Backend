import os
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")


SYSTEM_INSTRUCTIONS = """
You are Hoku AI, a friendly and professional healthcare information assistant.

Rules:
- Provide only general health and wellness information.
- Use simple and clear language.
- Do not diagnose diseases.
- Do not prescribe medicines.
- Do not tell users to stop prescribed medicines.
- Encourage consultation with a qualified healthcare professional.
- For severe symptoms such as chest pain, breathing difficulty,
  unconsciousness, stroke symptoms, severe bleeding, or suicidal thoughts,
  advise the user to contact local emergency services immediately.
- Keep the response concise, safe, and empathetic.
"""


class ChatbotConfigurationError(Exception):
    """Raised when chatbot environment configuration is missing."""


class ChatbotServiceError(Exception):
    """Raised when the external AI service cannot return a response."""


def generate_chatbot_reply(message: str) -> str:
    cleaned_message = message.strip()

    if not cleaned_message:
        raise ChatbotServiceError("Message cannot be empty.")

    if not OPENROUTER_API_KEY:
        raise ChatbotConfigurationError(
            "OPENROUTER_API_KEY is missing from the .env file."
        )

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://127.0.0.1:8000",
            "X-OpenRouter-Title": "Hoku Health Care API",
        },
    )

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": cleaned_message,
                },
            ],
            temperature=0.3,
            max_tokens=500,
        )

        reply = response.choices[0].message.content

        if not reply:
            raise ChatbotServiceError(
                "OpenRouter returned an empty response."
            )

        return reply.strip()

    except AuthenticationError as exc:
        raise ChatbotConfigurationError(
            "OpenRouter API key is invalid or inactive."
        ) from exc

    except RateLimitError as exc:
        raise ChatbotServiceError(
            "OpenRouter free-model limit reached. Please try again later."
        ) from exc

    except APIConnectionError as exc:
        raise ChatbotServiceError(
            "Could not connect to OpenRouter. Check your internet connection."
        ) from exc

    except APIError as exc:
        raise ChatbotServiceError(
            f"OpenRouter API request failed: {exc}"
        ) from exc