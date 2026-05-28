import uuid

from sqlalchemy import update
from sqlmodel import Session

from app.models.user import User


def try_consume_daily_quota(user_id: uuid.UUID, db: Session) -> bool:
    result = db.execute(
        update(User)
        .where(User.id == user_id, User.daily_used < User.daily_limit)
        .values(daily_used=User.daily_used + 1)
    )
    return result.rowcount > 0
