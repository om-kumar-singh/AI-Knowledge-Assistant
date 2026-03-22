"""Document upload / ingestion routes."""

import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.session import get_db
from models.document import Document
from models.schemas import UploadSuccessResponse
from rag.ingest import ingest_document
from services import chat_service, file_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


def _ingest_uploaded_file(relative_path: str, document_id: str) -> None:
    try:
        ingest_document(_BACKEND_ROOT / relative_path, document_id)
    except Exception:
        logger.exception("RAG ingestion failed for document_id=%s path=%s", document_id, relative_path)

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

    user_id = chat_service.get_or_create_default_user_id(db)
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
