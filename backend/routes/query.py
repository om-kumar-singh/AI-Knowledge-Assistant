"""RAG query with persisted conversational memory."""

import logging
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.config import get_settings
from db.session import get_db
from models.schemas import QueryRequest
from rag.retriever import retrieve
from services import chat_service
from services.llm_service import generate_answer

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rag"])


@router.post("/query")
async def rag_query(body: QueryRequest, db: Session = Depends(get_db)):
    """
    POST /api/query — always returns JSON; uses HTTP status for client errors / failures.
    Success body: { session_id, answer, sources }
    """
    try:
        query_text = (body.query or "").strip()
        if not query_text:
            print("[/api/query] validation failed: empty query")
            logger.warning("/api/query rejected: empty query")
            return JSONResponse(
                status_code=400,
                content={"error": "Query cannot be empty"},
            )

        print("[/api/query] incoming query:", repr(query_text))
        logger.info("/api/query incoming query: %s", query_text[:500])

        session_raw = body.session_id
        if session_raw and str(session_raw).strip():
            try:
                session_uuid = uuid.UUID(str(session_raw).strip())
            except ValueError:
                print("[/api/query] invalid session_id:", repr(session_raw))
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid session_id; use a UUID string."},
                )
        else:
            session_uuid = uuid.uuid4()

        settings = get_settings()
        history_pairs: list[tuple[str, str]] = []
        user_id: uuid.UUID | None = None

        try:
            user_id = chat_service.get_or_create_default_user_id(db)
            prior = chat_service.get_chat_history(
                db,
                session_uuid,
                user_id,
                limit=settings.chat_history_limit,
            )
            history_pairs = [(m.role, m.message) for m in prior]
        except SQLAlchemyError as e:
            logger.warning("Chat history / user lookup skipped (database error): %s", e)
        except Exception as e:
            logger.warning("Chat history / user lookup skipped: %s", e)

        try:
            chunks = retrieve(query_text)
        except Exception as e:
            logger.exception("Retriever failed: %s", e)
            chunks = []

        if chunks is None:
            chunks = []

        print("[/api/query] retrieved chunks count:", len(chunks))
        logger.info("/api/query retrieved %d chunk(s)", len(chunks))
        for i, ch in enumerate(chunks[:5]):
            preview = (ch or "")[:160].replace("\n", " ")
            print(f"[/api/query] chunk[{i}] preview:", repr(preview + ("…" if len(ch or "") > 160 else "")))
            logger.debug("/api/query chunk[%d] preview: %s", i, preview)

        if not chunks or len(chunks) == 0:
            answer = "No relevant information found in documents."
            print("[/api/query] empty retrieval — short-circuit, answer:", repr(answer))
            if user_id is not None:
                try:
                    chat_service.save_message(
                        db, user_id, session_uuid, "user", query_text, commit=False
                    )
                    chat_service.save_message(
                        db, user_id, session_uuid, "assistant", answer, commit=False
                    )
                    db.commit()
                except Exception as persist_e:
                    logger.warning("Could not persist chat (empty retrieval): %s", persist_e)
                    db.rollback()
            return {
                "session_id": str(session_uuid),
                "answer": answer,
                "sources": [],
            }

        # Safe LLM context: top 3 chunks, space-joined (never None)
        safe_parts = [
            str(c).strip()
            for c in chunks[:3]
            if c is not None and str(c).strip()
        ]
        joined_context = " ".join(safe_parts)
        llm_chunks = [joined_context] if joined_context else []

        try:
            answer = generate_answer(
                query_text,
                llm_chunks,
                chat_history=history_pairs,
            )
        except Exception as e:
            print("ERROR in /api/query (LLM):", str(e))
            logger.exception("LLM generation failed: %s", e)
            answer = (
                "The local language model could not generate a response right now. "
                "Try again after the model finishes loading."
            )

        if not (answer and str(answer).strip()):
            answer = "No relevant information found in documents."

        print("[/api/query] final answer preview:", repr(str(answer)[:300]))
        logger.info("/api/query final answer length=%d", len(str(answer)))

        if user_id is not None:
            try:
                chat_service.save_message(
                    db, user_id, session_uuid, "user", query_text, commit=False
                )
                chat_service.save_message(
                    db, user_id, session_uuid, "assistant", str(answer), commit=False
                )
                db.commit()
            except SQLAlchemyError as e:
                logger.warning("Could not persist chat messages: %s", e)
                db.rollback()
            except Exception as e:
                logger.warning("Could not persist chat messages: %s", e)
                db.rollback()

        return {
            "session_id": str(session_uuid),
            "answer": answer,
            "sources": chunks,
        }

    except Exception as e:
        print("ERROR in /api/query:", str(e))
        logger.exception("Unhandled error in /api/query: %s", e)
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Internal server error",
            },
        )
