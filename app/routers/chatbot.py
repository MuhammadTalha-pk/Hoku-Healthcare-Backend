from fastapi import APIRouter, HTTPException, status

from app.schemas.chatbot import ChatRequest, ChatResponse
from app.services.chatbot_service import (
    ChatbotConfigurationError,
    ChatbotServiceError,
    generate_chatbot_reply
)


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Chatbot"]
)


DISCLAIMER = (
    "This information is for general guidance only and is not a medical "
    "diagnosis. Please consult a qualified healthcare professional."
)


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK
)
def chat_with_hoku_ai(chat_request: ChatRequest):
    try:
        reply = generate_chatbot_reply(chat_request.message)

        return ChatResponse(
            reply=reply,
            disclaimer=DISCLAIMER
        )

    except ChatbotConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc)
        ) from exc

    except ChatbotServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected chatbot error occurred."
        ) from exc