"""Request/response models shared across routes."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message text.")


class ChatResponse(BaseModel):
    reply: str
    model: str = "placeholder"


class LoginRequest(BaseModel):
    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UploadSuccessResponse(BaseModel):
    message: str
    file_path: str
    document_id: str
