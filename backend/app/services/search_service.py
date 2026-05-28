import uuid

from sqlalchemy import String, cast, or_
from sqlmodel import Session, select

from app.models.analysis import Analysis

# 매칭 필드 우선순위
_FIELD_PRIORITY = ["tags", "forest", "tree", "memo", "code_original"]


def _matched_field(analysis: Analysis, q: str) -> str:
    ql = q.lower()
    if ql in str(analysis.tags).lower():
        return "tags"
    if ql in (analysis.forest or "").lower():
        return "forest"
    if ql in (analysis.tree or "").lower():
        return "tree"
    if ql in (analysis.memo or "").lower():
        return "memo"
    return "code_original"


def search(user_id: uuid.UUID, q: str, db: Session) -> list[dict]:
    pattern = f"%{q}%"
    stmt = (
        select(Analysis)
        .where(
            Analysis.user_id == user_id,
            or_(
                Analysis.forest.like(pattern),
                Analysis.tree.like(pattern),
                Analysis.memo.like(pattern),
                Analysis.code_original.like(pattern),
                cast(Analysis.tags, String).like(pattern),
            ),
        )
        .order_by(Analysis.created_at.desc())
    )
    rows = db.exec(stmt).all()
    return [
        {
            "id": str(r.id),
            "created_at": r.created_at.isoformat() + "Z",
            "language": r.language,
            "code_preview": r.code_original[:40],
            "tags": r.tags,
            "matched_field": _matched_field(r, q),
        }
        for r in rows
    ]
