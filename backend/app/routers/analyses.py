from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, rate_limit_dep
from app.models.user import User
from app.schemas.analysis import AnalysisCreateRequest

router = APIRouter()


@router.post("/analyses", status_code=201)
def create_analysis(
    req: AnalysisCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(rate_limit_dep),
):
    raise NotImplementedError
