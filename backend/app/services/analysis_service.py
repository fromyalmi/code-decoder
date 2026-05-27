from sqlmodel import Session

from app.models.user import User
from app.schemas.analysis import AnalysisCreateRequest


def create(req: AnalysisCreateRequest, user: User, db: Session) -> dict:
    language = req.language or "python"
    return {"language": language, "cache_hit": False}
