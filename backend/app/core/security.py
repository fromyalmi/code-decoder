import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-prod")
_ALGORITHM = "HS256"
COOKIE_NAME = "session"
COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 days


def create_signed_cookie(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=COOKIE_MAX_AGE)
    return jwt.encode(
        {"sub": user_id, "exp": expire}, SESSION_SECRET, algorithm=_ALGORITHM
    )


def verify_signed_cookie(token: str) -> str:
    try:
        payload = jwt.decode(token, SESSION_SECRET, algorithms=[_ALGORITHM])
        return str(payload["sub"])
    except (JWTError, KeyError) as exc:
        raise ValueError("invalid session token") from exc
