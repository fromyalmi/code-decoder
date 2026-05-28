import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, and_, or_, select

from app.core.exceptions import DailyLimitExceeded
from app.models.analysis import Analysis
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
    from app.models.key_concept import KeyConcept
    from app.models.line_explanation import LineExplanation
    from app.repositories import reward_repo, user_repo

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

    for dl in parsed.deep_leaves:
        db.add(
            LineExplanation(
                analysis_id=analysis.id,
                line_no=dl.line_no,
                tier="deep_core",
                deep=dl.deep,
            )
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

    for kc in parsed.key_concepts:
        db.add(
            KeyConcept(
                user_id=user.id,
                analysis_id=analysis.id,
                name=kc.name,
                definition=kc.definition,
            )
        )

    reward_repo.grant_on_analysis(user.id, db)

    db.commit()
    db.refresh(user)

    response = {
        "id": str(analysis.id),
        "user_id": str(user.id),
        "code_original": req.code,
        "code_processed": cleaned.code,
        "code_sha256": cache_key,
        "language": language,
        "line_count_original": analysis.line_count_original,
        "line_count_processed": analysis.line_count_processed,
        "line_mapping": analysis.line_mapping,
        "forest": parsed.forest,
        "tree": parsed.tree,
        "line_explanations": [
            {"line_no": le.line_no, "short": le.short}
            for le in parsed.line_explanations
        ],
        "deep_leaves": [
            {"line_no": dl.line_no, "deep": dl.deep} for dl in parsed.deep_leaves
        ],
        "tags": parsed.tags,
        "key_concepts": [
            {"name": kc.name, "definition": kc.definition, "is_new": True}
            for kc in parsed.key_concepts
        ],
        "created_at": analysis.created_at.isoformat() + "Z",
        "daily_used": user.daily_used,
        "leaf_counter": user.leaf_counter,
        "is_favorite": analysis.is_favorite,
        "memo": analysis.memo,
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


def list_for_user(
    user: User, db: Session, cursor: Optional[str] = None, limit: int = 20
) -> dict:
    stmt = select(Analysis).where(Analysis.user_id == user.id)

    if cursor:
        try:
            decoded = base64.b64decode(cursor).decode()
            cursor_ts_str, cursor_id_str = decoded.split("|", 1)
            cursor_ts = datetime.fromisoformat(cursor_ts_str)
            stmt = stmt.where(
                or_(
                    Analysis.created_at < cursor_ts,
                    and_(
                        Analysis.created_at == cursor_ts,
                        Analysis.id < uuid.UUID(cursor_id_str),
                    ),
                )
            )
        except Exception:
            pass

    stmt = stmt.order_by(Analysis.created_at.desc(), Analysis.id.desc()).limit(
        limit + 1
    )
    rows = db.exec(stmt).all()

    next_cursor = None
    if len(rows) == limit + 1:
        rows = rows[:limit]
        last = rows[-1]  # last item of current page → cursor for next page
        token = f"{last.created_at.isoformat()}|{last.id}"
        next_cursor = base64.b64encode(token.encode()).decode()

    items = [
        {
            "id": str(r.id),
            "created_at": r.created_at.isoformat() + "Z",
            "language": r.language,
            "code_preview": r.code_original[:40],
            "tags": r.tags,
            "is_favorite": r.is_favorite,
        }
        for r in rows
    ]
    return {"items": items, "next_cursor": next_cursor}


def get_for_user(analysis_id: uuid.UUID, user: User, db: Session) -> dict:
    from app.models.key_concept import KeyConcept
    from app.models.line_explanation import LineExplanation

    analysis = db.exec(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id)
    ).first()
    if analysis is None:
        from app.core.exceptions import AnalysisNotFound

        raise AnalysisNotFound

    les = db.exec(
        select(LineExplanation).where(
            LineExplanation.analysis_id == analysis.id,
            LineExplanation.tier == "short",
        )
    ).all()

    deep = db.exec(
        select(LineExplanation).where(
            LineExplanation.analysis_id == analysis.id,
            LineExplanation.tier.in_(["deep_core", "deep_pinned"]),
        )
    ).all()

    kcs = db.exec(select(KeyConcept).where(KeyConcept.analysis_id == analysis.id)).all()

    return {
        "id": str(analysis.id),
        "user_id": str(analysis.user_id),
        "created_at": analysis.created_at.isoformat() + "Z",
        "language": analysis.language,
        "code_original": analysis.code_original,
        "code_processed": analysis.code_processed,
        "forest": analysis.forest,
        "tree": analysis.tree,
        "tags": analysis.tags,
        "memo": analysis.memo,
        "is_favorite": analysis.is_favorite,
        "line_explanations": [{"line_no": le.line_no, "short": le.short} for le in les],
        "deep_leaves": [{"line_no": dl.line_no, "deep": dl.deep} for dl in deep],
        "key_concepts": [{"name": kc.name, "definition": kc.definition} for kc in kcs],
    }


def update_for_user(
    analysis_id: uuid.UUID,
    user: User,
    db: Session,
    tags: Optional[list] = None,
    memo: Optional[str] = None,
    is_favorite: Optional[bool] = None,
) -> dict:
    analysis = db.exec(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id)
    ).first()
    if analysis is None:
        from app.core.exceptions import AnalysisNotFound

        raise AnalysisNotFound

    if tags is not None:
        analysis.tags = tags
    if memo is not None:
        analysis.memo = memo
    if is_favorite is not None:
        analysis.is_favorite = is_favorite

    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return get_for_user(analysis_id, user, db)


def delete_for_user(analysis_id: uuid.UUID, user: User, db: Session) -> None:
    analysis = db.exec(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id)
    ).first()
    if analysis is None:
        from app.core.exceptions import AnalysisNotFound

        raise AnalysisNotFound

    db.delete(analysis)
    db.commit()
