from sqlmodel import Session

from app.models.user import User
from app.preprocessing.validator import check_raw_size
from app.schemas.analysis import AnalysisCreateRequest


def create(req: AnalysisCreateRequest, user: User, db: Session) -> dict:
    check_raw_size(req.code)
    language = req.language or "python"
    return {"language": language, "cache_hit": False}
