"""Database connectivity test routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User

router = APIRouter(tags=["database"])


@router.get("/test-db")
def test_db(db: Session = Depends(get_db)) -> dict[str, str]:
    """Insert a dummy user and return it (development / connectivity checks)."""
    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash="dummy-hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": str(user.id),
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }
