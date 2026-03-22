"""Document upload / ingestion routes."""

import logging
import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.session import get_db
from models.document import Document
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


@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
):
    """
    POST /api/upload — multipart field name must be `file`.
    On failure returns JSON with error + message (still gets CORS headers).
    """
    print("[/api/upload] request received")
    logger.info("/api/upload request received")

    try:
        # Ensure uploads directory exists (matches configured uploads_dir)
        upload_abs = file_service.get_uploads_directory()
        os.makedirs(upload_abs, exist_ok=True)
        file_service.ensure_upload_directory()
        print("[/api/upload] upload dir OK:", upload_abs)

        if file is None:
            print("UPLOAD ERROR: No file provided (missing multipart field)")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "No file provided",
                    "message": "Upload failed",
                },
            )

        if not file.filename or not str(file.filename).strip():
            print("UPLOAD ERROR: empty filename")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "No file provided",
                    "message": "Upload failed",
                },
            )

        print("[/api/upload] filename:", repr(file.filename))

        relative_path, display_filename = await file_service.save_upload_file(file)
        print("[/api/upload] saved as:", relative_path)

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

        body = {
            "message": "File uploaded successfully",
            "file_path": document.file_path,
            "document_id": str(document.id),
        }
        print("[/api/upload] success document_id:", body["document_id"])
        logger.info("/api/upload success document_id=%s", body["document_id"])
        return body

    except ValueError as e:
        print("UPLOAD ERROR:", str(e))
        logger.warning("/api/upload validation error: %s", e)
        return JSONResponse(
            status_code=400,
            content={
                "error": str(e),
                "message": "Upload failed",
            },
        )
    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        logger.exception("/api/upload failed: %s", e)
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Upload failed",
            },
        )
