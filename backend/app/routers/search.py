from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import EmptyQuery
from app.db import get_session
from app.models.user import User
from app.services import search_service

router = APIRouter()


@router.get("/search")
def search_analyses(
    q: str = Query(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    if not q.strip():
        raise EmptyQuery
    return search_service.search(current_user.id, q, db)
