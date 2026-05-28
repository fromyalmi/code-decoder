from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.dependencies import get_current_user
from app.db import get_session
from app.models.user import User
from app.services import encyclopedia_service

router = APIRouter()


@router.get("/encyclopedia")
def get_encyclopedia(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return encyclopedia_service.list_for_user(current_user.id, db)
