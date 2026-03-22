"""Persist and load chat messages for conversational memory."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.chat import Chat
from models.user import User

# Same placeholder user as document uploads until real auth exists.
_DEFAULT_USER_EMAIL = "dummy-upload@local.internal"


def get_or_create_default_user_id(db: Session) -> uuid.UUID:
    user = db.scalars(select(User).where(User.email == _DEFAULT_USER_EMAIL)).first()
    if user is not None:
        return user.id
    user = User(email=_DEFAULT_USER_EMAIL, password_hash="n/a")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


def save_message(
    db: Session,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    role: str,
    message: str,
    *,
    commit: bool = True,
) -> Chat:
    """Store one chat turn. Use commit=False to batch with db.commit() in the caller."""
    if role not in ("user", "assistant"):
        raise ValueError("role must be 'user' or 'assistant'")

    row = Chat(
        user_id=user_id,
        session_id=session_id,
        role=role,
        message=message,
    )
    db.add(row)
    if commit:
        db.commit()
        db.refresh(row)
    return row


def get_chat_history(
    db: Session,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    limit: int = 10,
) -> list[Chat]:
    """
    Return up to `limit` most recent messages for this session and user, oldest first.
    """
    limit = max(1, min(limit, 50))
    stmt = (
        select(Chat)
        .where(Chat.session_id == session_id, Chat.user_id == user_id)
        .order_by(Chat.created_at.desc())
        .limit(limit)
    )
    rows = list(db.scalars(stmt).all())
    rows.reverse()
    return rows
