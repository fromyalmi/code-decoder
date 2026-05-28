from sqlmodel import Session

from app.core.exceptions import DailyLimitExceeded
from app.models.user import User
from app.preprocessing.code_cleaner import clean
from app.preprocessing.validator import check_processed_lines, check_raw_size
from app.schemas.analysis import AnalysisCreateRequest


def create(req: AnalysisCreateRequest, user: User, db: Session) -> dict:
    check_raw_size(req.code)
    cleaned = clean(req.code)
    check_processed_lines(cleaned)
    if user.daily_used >= user.daily_limit:
        raise DailyLimitExceeded
    language = req.language or "python"
    return {"language": language, "cache_hit": False}
