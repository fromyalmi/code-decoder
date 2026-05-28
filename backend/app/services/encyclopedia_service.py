import uuid
from collections import defaultdict

from sqlmodel import Session, select

from app.models.key_concept import KeyConcept


def list_for_user(user_id: uuid.UUID, db: Session) -> list[dict]:
    rows = db.exec(
        select(KeyConcept)
        .where(KeyConcept.user_id == user_id)
        .order_by(KeyConcept.created_at.asc())
    ).all()

    # name 기준 집계 (첫 등장 기준 definition/analysis_id, 전체 count)
    first: dict[str, dict] = {}
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row.name] += 1
        if row.name not in first:
            first[row.name] = {
                "name": row.name,
                "definition": row.definition,
                "first_seen_analysis_id": str(row.analysis_id),
                "first_seen_at": row.created_at,
            }

    items = [
        {
            "name": v["name"],
            "definition": v["definition"],
            "appearance_count": counts[v["name"]],
            "first_seen_analysis_id": v["first_seen_analysis_id"],
        }
        for v in first.values()
    ]
    # 최근 등장순 정렬 (first_seen_at 내림차순)
    items.sort(key=lambda x: first[x["name"]]["first_seen_at"], reverse=True)
    return items
