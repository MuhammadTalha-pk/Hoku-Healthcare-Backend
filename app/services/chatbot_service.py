"""AI chatbot service.

Original contributor: Faisal Majeed.
Integrated into the shared FastAPI architecture by Muhammad Talha.
"""

from app.core.config import settings


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
    if not settings.OPENROUTER_API_KEY:
        raise ChatbotConfigurationError("OPENROUTER_API_KEY is missing from the environment.")

    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": settings.OPENROUTER_SITE_URL,
            "X-OpenRouter-Title": settings.APP_NAME,
        },
    )
    try:
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": cleaned_message},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        reply = response.choices[0].message.content
        if not reply:
            raise ChatbotServiceError("OpenRouter returned an empty response.")
        return reply.strip()
    except AuthenticationError as exc:
        raise ChatbotConfigurationError("OpenRouter API key is invalid or inactive.") from exc
    except RateLimitError as exc:
        raise ChatbotServiceError("OpenRouter rate limit reached. Please try again later.") from exc
    except APIConnectionError as exc:
        raise ChatbotServiceError("Could not connect to OpenRouter.") from exc
    except APIError as exc:
        raise ChatbotServiceError(f"OpenRouter API request failed: {exc}") from exc
