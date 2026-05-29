from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.dependencies import get_current_user
from app.core.title_table import get_title
from app.db import get_session
from app.models.user import User
from app.repositories import reward_repo
from app.schemas.user import MeResponse, UserUpdateRequest


router = APIRouter()


def _user_response(user: User, db: Session) -> dict:
    reward = reward_repo.get_or_create(user.id, db)
    db.commit()
    db.refresh(reward)
    return {
        "id": str(user.id),
        "email": user.email,
        "nickname": user.nickname,
        "level": user.level,
        "level_auto": user.level_auto,
        "first_login_completed_at": (
            user.first_login_completed_at.isoformat()
            if user.first_login_completed_at
            else None
        ),
        "sound_enabled": user.sound_enabled,
        "daily_used": user.daily_used,
        "daily_limit": user.daily_limit,
        "daily_remaining": user.daily_limit - user.daily_used,
        "leaf_counter": user.leaf_counter,
        "reward": {
            "caterpillar_balance": reward.caterpillar_balance,
            "caterpillar_total_earned": reward.caterpillar_total_earned,
            "caterpillar_total_spent": reward.caterpillar_total_spent,
            "shield_count": reward.shield_count,
            "shield_used_total": reward.shield_used_total,
            "streak_current": reward.streak_current,
            "streak_max": reward.streak_max,
            "streak_last_date": (
                reward.streak_last_date.isoformat() if reward.streak_last_date else None
            ),
            "analysis_count_total": reward.analysis_count_total,
        },
        "title": get_title(reward.analysis_count_total),
    }


@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_session)
):
    return _user_response(current_user, db)


@router.patch("/users/me")
def patch_me(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    if req.level is not None:
        current_user.level = req.level
        current_user.level_auto = req.level == 4
    if (
        req.first_login_completed is True
        and current_user.first_login_completed_at is None
    ):
        current_user.first_login_completed_at = datetime.now(timezone.utc).replace(
            tzinfo=None
        )
    if req.sound_enabled is not None:
        current_user.sound_enabled = req.sound_enabled
    db.commit()
    db.refresh(current_user)
    return _user_response(current_user, db)
