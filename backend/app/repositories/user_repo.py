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


def try_increment_leaf_counter_or_charge(user_id: uuid.UUID, db: Session) -> str:
    # 시도 1: 5번째 확장 — counter==4 AND 한도 남음 → 결제
    r = db.execute(
        update(User)
        .where(
            User.id == user_id,
            User.leaf_counter == 4,
            User.daily_used < User.daily_limit,
        )
        .values(leaf_counter=0, daily_used=User.daily_used + 1)
    )
    if r.rowcount:
        return "charged"
    # 시도 2: 단순 증가 — counter < 4
    r = db.execute(
        update(User)
        .where(User.id == user_id, User.leaf_counter < 4)
        .values(leaf_counter=User.leaf_counter + 1)
    )
    if r.rowcount:
        return "incremented"
    # 시도 3: counter==4 AND 한도 없음 → 차단
    return "limit_exceeded"
