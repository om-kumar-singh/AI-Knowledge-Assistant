"""Authentication routes."""

from fastapi import APIRouter

from models.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    """Placeholder: returns a mock token (no real authentication)."""
    _ = body.email, body.password
    return LoginResponse(access_token="mock-token-placeholder", token_type="bearer")
