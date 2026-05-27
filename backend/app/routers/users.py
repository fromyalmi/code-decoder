from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "nickname": current_user.nickname,
    }
