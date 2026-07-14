import os

from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")


SYSTEM_INSTRUCTIONS = """
You are Hoku AI, a friendly and professional healthcare assistant.

Your responsibilities:
- Answer general health and wellness questions.
- Explain symptoms in simple language.
- Suggest the appropriate type of doctor when useful.
- Give safe, general self-care guidance.
- Remind users that you cannot provide a confirmed diagnosis.
- Encourage emergency help for dangerous symptoms.

Safety rules:
- Never claim to diagnose a disease.
- Never guarantee that a medicine or treatment will cure the user.
- Do not prescribe prescription medication.
- Do not tell users to stop prescribed medicine.
- For chest pain, breathing difficulty, unconsciousness, severe bleeding,
  stroke symptoms, suicidal thoughts, or another emergency, advise the user
  to contact local emergency services immediately.
- Keep responses clear, empathetic, and concise.
- Always recommend consulting a qualified healthcare professional for
  proper diagnosis and treatment.
"""


class ChatbotConfigurationError(Exception):
    """Raised when chatbot configuration is missing."""


class ChatbotServiceError(Exception):
    """Raised when the AI provider request fails."""


def generate_chatbot_reply(message: str) -> str:
    if not OPENAI_API_KEY:
        raise ChatbotConfigurationError(
            "OPENAI_API_KEY is missing from the .env file."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=message,
            max_output_tokens=500
        )

        reply = response.output_text

        if not reply:
            raise ChatbotServiceError(
                "The AI service returned an empty response."
            )

        return reply.strip()

    except AuthenticationError as exc:
        raise ChatbotConfigurationError(
            "OpenAI API key is invalid or inactive."
        ) from exc

    except RateLimitError as exc:
        raise ChatbotServiceError(
            "AI request limit reached. Please try again later."
        ) from exc

    except APIError as exc:
        raise ChatbotServiceError(
            "The AI service is temporarily unavailable."
        ) from exc