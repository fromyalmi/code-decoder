import hashlib
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.core.exceptions import DailyLimitExceeded
from app.models.cache import AnalysisCache
from app.models.user import User
from app.preprocessing.code_cleaner import clean
from app.preprocessing.validator import check_processed_lines, check_raw_size
from app.schemas.analysis import AnalysisCreateRequest


def create(req: AnalysisCreateRequest, user: User, db: Session) -> dict:
    check_raw_size(req.code)
    cleaned = clean(req.code)
    check_processed_lines(cleaned)

    cache_key = hashlib.sha256(cleaned.code.encode()).hexdigest()
    cached = db.exec(
        select(AnalysisCache).where(
            AnalysisCache.user_id == user.id,
            AnalysisCache.code_sha256 == cache_key,
            AnalysisCache.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
        )
    ).first()
    if cached:
        cached.hit_count += 1
        db.commit()
        return {**cached.result, "cache_hit": True}

    if user.daily_used >= user.daily_limit:
        raise DailyLimitExceeded
    language = req.language or "python"

    from app.llm import client as _llm
    from app.llm.parser import parse_analysis_response
    from app.llm.prompt import build_prompt

    messages = build_prompt(cleaned.tagged, user.level)
    raw = _llm.call_analysis(messages)
    parsed = parse_analysis_response(raw)

    db.commit()
    return {
        "language": language,
        "forest": parsed.forest,
        "tree": parsed.tree,
        "cache_hit": False,
    }
