"""RAG query with persisted conversational memory."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.config import get_settings
from db.session import get_db
from models.schemas import QueryRequest, QueryResponse
from rag.retriever import retrieve
from services import chat_service
from services.llm_service import generate_answer

router = APIRouter(tags=["rag"])


def _parse_session_id(raw: str | None) -> uuid.UUID:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return uuid.uuid4()
    try:
        return uuid.UUID(raw.strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid session_id; use a UUID string.") from exc


@router.post("/query", response_model=QueryResponse)
async def rag_query(body: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    settings = get_settings()
    session_uuid = _parse_session_id(body.session_id)
    user_id = chat_service.get_or_create_default_user_id(db)

    prior = chat_service.get_chat_history(
        db,
        session_uuid,
        user_id,
        limit=settings.chat_history_limit,
    )
    history_pairs: list[tuple[str, str]] = [(m.role, m.message) for m in prior]

    sources = retrieve(body.query)
    answer = generate_answer(body.query, sources, chat_history=history_pairs)

    chat_service.save_message(db, user_id, session_uuid, "user", body.query, commit=False)
    chat_service.save_message(db, user_id, session_uuid, "assistant", answer, commit=False)
    db.commit()

    return QueryResponse(
        session_id=str(session_uuid),
        answer=answer,
        sources=sources,
    )
