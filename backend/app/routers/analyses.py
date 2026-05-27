from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.dependencies import get_current_user, rate_limit_dep
from app.db import get_session
from app.models.user import User
from app.schemas.analysis import AnalysisCreateRequest
from app.services import analysis_service

router = APIRouter()


@router.post("/analyses", status_code=201)
def create_analysis(
    req: AnalysisCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(rate_limit_dep),
    db: Session = Depends(get_session),
):
    return analysis_service.create(req, current_user, db)
