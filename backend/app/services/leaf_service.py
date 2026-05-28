import uuid

from sqlmodel import Session

from app.core.exceptions import AnalysisNotFound, DailyLimitExceeded
from app.llm import client as _llm
from app.models.daily_limit_log import DailyLimitLog
from app.models.line_explanation import LineExplanation
from app.models.user import User
from app.repositories import analysis_repo, user_repo


def expand(analysis_id: uuid.UUID, line_no: int, user: User, db: Session) -> dict:
    analysis = analysis_repo.get_by_id_for_user(analysis_id, user.id, db)
    if analysis is None:
        raise AnalysisNotFound

    raw = _llm.call_leaf_expand(line_no, user.level)
    deep_text = raw["deep_text"]

    outcome = user_repo.try_increment_leaf_counter_or_charge(user.id, db)
    if outcome == "limit_exceeded":
        raise DailyLimitExceeded

    if outcome == "charged":
        db.add(
            DailyLimitLog(
                user_id=user.id,
                reason="leaf_5th",
                before=user.daily_used,
                after=user.daily_used + 1,
            )
        )
    db.commit()
    db.refresh(user)

    return {
        "line_no": line_no,
        "deep_text": deep_text,
        "outcome": outcome,
        "leaf_counter": user.leaf_counter,
        "daily_used": user.daily_used,
    }


def pin(
    analysis_id: uuid.UUID, line_no: int, deep_text: str, user: User, db: Session
) -> None:
    analysis = analysis_repo.get_by_id_for_user(analysis_id, user.id, db)
    if analysis is None:
        raise AnalysisNotFound

    db.add(
        LineExplanation(
            analysis_id=analysis.id,
            line_no=line_no,
            tier="deep_pinned",
            deep=deep_text,
            is_pinned=True,
        )
    )
    db.commit()
