"""Document upload / ingestion routes."""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import get_db
from models.document import Document
from models.schemas import UploadSuccessResponse
from models.user import User
from rag.ingest import ingest_document
from services import file_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


def _ingest_uploaded_file(relative_path: str, document_id: str) -> None:
    try:
        ingest_document(_BACKEND_ROOT / relative_path, document_id)
    except Exception:
        logger.exception("RAG ingestion failed for document_id=%s path=%s", document_id, relative_path)

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
    background_tasks: BackgroundTasks,
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

    background_tasks.add_task(_ingest_uploaded_file, document.file_path, str(document.id))

    return UploadSuccessResponse(
        message="File uploaded successfully",
        file_path=document.file_path,
        document_id=str(document.id),
    )
