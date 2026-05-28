import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.dependencies import get_current_user, rate_limit_dep
from app.db import get_session
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisPatchRequest,
    LeafExpandRequest,
    LeafPinRequest,
)
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


@router.get("/analyses")
def list_analyses(
    cursor: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return analysis_service.list_for_user(current_user, db, cursor=cursor)


@router.get("/analyses/{analysis_id}")
def get_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return analysis_service.get_for_user(analysis_id, current_user, db)


@router.patch("/analyses/{analysis_id}")
def patch_analysis(
    analysis_id: uuid.UUID,
    body: AnalysisPatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return analysis_service.update_for_user(
        analysis_id,
        current_user,
        db,
        tags=body.tags,
        memo=body.memo,
        is_favorite=body.is_favorite,
    )


@router.delete("/analyses/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    analysis_service.delete_for_user(analysis_id, current_user, db)


@router.patch("/analyses/{analysis_id}/leaves/{line_no}/pin", status_code=204)
def pin_leaf(
    analysis_id: uuid.UUID,
    line_no: int,
    body: LeafPinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    leaf_service.pin(analysis_id, line_no, body.deep_text, current_user, db)
