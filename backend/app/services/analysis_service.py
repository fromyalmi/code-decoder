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

    from datetime import timedelta

    from app.llm import client as _llm
    from app.llm.parser import parse_analysis_response
    from app.llm.prompt import build_prompt
    from app.models.analysis import Analysis
    from app.models.daily_limit_log import DailyLimitLog
    from app.models.line_explanation import LineExplanation
    from app.repositories import user_repo

    messages = build_prompt(cleaned.tagged, user.level)
    raw = _llm.call_analysis(messages)
    parsed = parse_analysis_response(raw)

    analysis = Analysis(
        user_id=user.id,
        code_original=req.code,
        code_processed=cleaned.code,
        code_sha256=cache_key,
        language=language,
        line_count_original=len(req.code.splitlines()),
        line_count_processed=len(cleaned.mapping),
        line_mapping={str(k): v for k, v in cleaned.mapping.items()},
        forest=parsed.forest,
        tree=parsed.tree,
        tags=parsed.tags,
    )
    db.add(analysis)
    db.flush()

    for le in parsed.line_explanations:
        db.add(
            LineExplanation(analysis_id=analysis.id, line_no=le.line_no, short=le.short)
        )

    consumed = user_repo.try_consume_daily_quota(user.id, db)
    if not consumed:
        raise DailyLimitExceeded

    db.add(
        DailyLimitLog(
            user_id=user.id,
            reason="analysis",
            before=user.daily_used,
            after=user.daily_used + 1,
        )
    )

    response = {
        "language": language,
        "forest": parsed.forest,
        "tree": parsed.tree,
        "line_explanations": [
            {"line_no": le.line_no, "short": le.short}
            for le in parsed.line_explanations
        ],
        "cache_hit": False,
    }
    db.add(
        AnalysisCache(
            user_id=user.id,
            code_sha256=cache_key,
            result=response,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
    )
    db.commit()
    return response
