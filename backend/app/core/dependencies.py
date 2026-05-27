import uuid

from fastapi import Cookie, Depends, HTTPException
from sqlmodel import Session, select

from app.core.security import COOKIE_NAME, verify_signed_cookie
from app.db import get_session
from app.models.user import User


def rate_limit_dep() -> None:
    """Stub — Pre-MVP in-memory rate limit placeholder (Closed Beta: Redis)."""


async def get_current_user(
    session: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(get_session),
) -> User:
    if not session:
        raise HTTPException(
            401, {"code": "NO_SESSION", "message": "🦜 로그인이 필요해"}
        )
    try:
        user_id = verify_signed_cookie(session)
    except ValueError:
        raise HTTPException(
            401, {"code": "NO_SESSION", "message": "🦜 로그인이 필요해"}
        )
    user = db.exec(select(User).where(User.id == uuid.UUID(user_id))).first()
    if not user:
        raise HTTPException(
            401, {"code": "NO_SESSION", "message": "🦜 로그인이 필요해"}
        )
    return user
