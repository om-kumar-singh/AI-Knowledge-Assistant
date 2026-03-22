"""Document upload / ingestion routes."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import get_db
from models.document import Document
from models.schemas import UploadSuccessResponse
from models.user import User
from services import file_service

router = APIRouter(tags=["documents"])

_DUMMY_UPLOAD_EMAIL = "dummy-upload@local.internal"


def _get_or_create_dummy_user_id(db: Session) -> uuid.UUID:
    user = db.scalars(select(User).where(User.email == _DUMMY_UPLOAD_EMAIL)).first()
    if user is not None:
        return user.id
    user = User(email=_DUMMY_UPLOAD_EMAIL, password_hash="n/a")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


@router.post("/upload", response_model=UploadSuccessResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadSuccessResponse:
    """Accept a PDF or TXT file, store it under `uploads/`, and persist metadata."""
    try:
        relative_path, display_filename = await file_service.save_upload_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user_id = _get_or_create_dummy_user_id(db)
    document = Document(
        user_id=user_id,
        filename=display_filename,
        file_path=relative_path,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return UploadSuccessResponse(
        message="File uploaded successfully",
        file_path=document.file_path,
        document_id=str(document.id),
    )
