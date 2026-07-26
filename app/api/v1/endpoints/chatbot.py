"""AI chatbot endpoint. Original contributor: Faisal Majeed."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.services.chatbot_service import ChatbotConfigurationError, ChatbotServiceError, generate_chatbot_reply

router = APIRouter()
DISCLAIMER = (
    "This information is for general guidance only and is not a medical diagnosis. "
    "Please consult a qualified healthcare professional."
)


@router.post("/chat", response_model=ChatResponse)
def chat_with_hoku_ai(
    payload: ChatRequest,
    _: User = Depends(get_current_user),
) -> ChatResponse:
    try:
        return ChatResponse(reply=generate_chatbot_reply(payload.message), disclaimer=DISCLAIMER)
    except ChatbotConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ChatbotServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
