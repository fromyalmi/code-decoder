from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.dependencies import get_current_user
from app.db import get_session
from app.models.user import User
from app.schemas.user import UserUpdateRequest

router = APIRouter()


def _user_response(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "nickname": user.nickname,
        "level": user.level,
        "level_auto": user.level_auto,
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return _user_response(current_user)


@router.patch("/users/me")
def patch_me(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    if req.level is not None:
        current_user.level = req.level
        current_user.level_auto = req.level == 4
    db.commit()
    db.refresh(current_user)
    return _user_response(current_user)
