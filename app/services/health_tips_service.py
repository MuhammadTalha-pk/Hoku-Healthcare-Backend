import json
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

from app.schemas.health_tips import (
    HealthTipsRequest,
    HealthTipsResponse,
)


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")


class HealthTipsConfigurationError(Exception):
    pass


class HealthTipsServiceError(Exception):
    pass


def generate_health_tips(
    request: HealthTipsRequest,
) -> HealthTipsResponse:
    if not OPENROUTER_API_KEY:
        raise HealthTipsConfigurationError(
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

    prompt = f"""
You are Hoku AI, a healthcare wellness assistant.

Create safe and practical health tips for this user.

Category: {request.category}
Age: {request.age if request.age is not None else "Not provided"}
Gender: {request.gender or "Not provided"}
Medical condition: {request.medical_condition or "Not provided"}

Return valid JSON only in this exact structure:

{{
  "category": "string",
  "tips": ["string"],
  "daily_habits": ["string"],
  "things_to_avoid": ["string"],
  "doctor_advice": "string",
  "disclaimer": "string"
}}

Rules:
- Give general wellness guidance only.
- Do not diagnose disease.
- Do not prescribe prescription medicine.
- Do not advise stopping prescribed medicine.
- Provide 5 tips.
- Provide 4 daily habits.
- Provide 3 things to avoid.
- Keep language simple and practical.
- Mention consulting a qualified healthcare professional when appropriate.
"""

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return valid JSON only. Do not use markdown "
                        "or code fences."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            max_tokens=800,
        )

        content = response.choices[0].message.content

        if not content:
            raise HealthTipsServiceError(
                "OpenRouter returned an empty response."
            )

        cleaned_content = content.strip()

        if cleaned_content.startswith("```"):
            cleaned_content = cleaned_content.replace(
                "```json",
                "",
                1,
            )
            cleaned_content = cleaned_content.replace(
                "```",
                "",
            ).strip()

        data = json.loads(cleaned_content)

        return HealthTipsResponse(**data)

    except json.JSONDecodeError as exc:
        raise HealthTipsServiceError(
            "AI returned an invalid JSON response."
        ) from exc

    except AuthenticationError as exc:
        raise HealthTipsConfigurationError(
            "OpenRouter API key is invalid or inactive."
        ) from exc

    except RateLimitError as exc:
        raise HealthTipsServiceError(
            "OpenRouter free-model limit reached. Try again later."
        ) from exc

    except APIConnectionError as exc:
        raise HealthTipsServiceError(
            "Could not connect to OpenRouter."
        ) from exc

    except APIError as exc:
        raise HealthTipsServiceError(
            f"OpenRouter API request failed: {exc}"
        ) from exc