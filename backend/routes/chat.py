"""Chat API routes."""

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """Placeholder: returns a fixed dummy reply."""
    _ = body.message
    return ChatResponse(
        reply="This is a placeholder response. Wire LLMService here.",
        model="placeholder",
    )
