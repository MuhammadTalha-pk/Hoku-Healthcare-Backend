"""AI health tips service.

Original contributor: Faisal Majeed.
Integrated into the shared FastAPI architecture by Muhammad Talha.
"""

import json

from app.core.config import settings
from app.schemas.health_tips import HealthTipsRequest, HealthTipsResponse


class HealthTipsConfigurationError(Exception):
    pass


class HealthTipsServiceError(Exception):
    pass


def generate_health_tips(request: HealthTipsRequest) -> HealthTipsResponse:
    if not settings.OPENROUTER_API_KEY:
        raise HealthTipsConfigurationError("OPENROUTER_API_KEY is missing from the environment.")

    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": settings.OPENROUTER_SITE_URL,
            "X-OpenRouter-Title": settings.APP_NAME,
        },
    )
    prompt = f"""
You are Hoku AI, a healthcare wellness assistant.
Create safe and practical health tips for this user.

Category: {request.category}
Age: {request.age if request.age is not None else 'Not provided'}
Gender: {request.gender or 'Not provided'}
Medical condition: {request.medical_condition or 'Not provided'}

Return valid JSON only with these fields:
category, tips, daily_habits, things_to_avoid, doctor_advice, disclaimer.
Give general wellness guidance only. Do not diagnose disease or prescribe medicine.
Provide 5 tips, 4 daily habits, and 3 things to avoid.
"""
    try:
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON only. Do not use markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        content = response.choices[0].message.content
        if not content:
            raise HealthTipsServiceError("OpenRouter returned an empty response.")
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "", 1).replace("```", "").strip()
        return HealthTipsResponse(**json.loads(cleaned))
    except json.JSONDecodeError as exc:
        raise HealthTipsServiceError("AI returned an invalid JSON response.") from exc
    except AuthenticationError as exc:
        raise HealthTipsConfigurationError("OpenRouter API key is invalid or inactive.") from exc
    except RateLimitError as exc:
        raise HealthTipsServiceError("OpenRouter rate limit reached. Try again later.") from exc
    except APIConnectionError as exc:
        raise HealthTipsServiceError("Could not connect to OpenRouter.") from exc
    except APIError as exc:
        raise HealthTipsServiceError(f"OpenRouter API request failed: {exc}") from exc
