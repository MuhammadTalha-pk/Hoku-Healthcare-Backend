from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=2,
        max_length=2000,
        examples=["I have a mild fever. What should I do?"]
    )


class ChatResponse(BaseModel):
    reply: str
    disclaimer: str