import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.dependencies import get_current_user, rate_limit_dep
from app.db import get_session
from app.models.user import User
from app.schemas.analysis import AnalysisCreateRequest, LeafExpandRequest
from app.services import analysis_service, leaf_service

router = APIRouter()


@router.post("/analyses", status_code=201)
def create_analysis(
    req: AnalysisCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(rate_limit_dep),
    db: Session = Depends(get_session),
):
    return analysis_service.create(req, current_user, db)


@router.post("/analyses/{analysis_id}/leaves/expand")
def expand_leaf(
    analysis_id: uuid.UUID,
    body: LeafExpandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return leaf_service.expand(analysis_id, body.line_no, current_user, db)
