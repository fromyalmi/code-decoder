import uuid

from sqlmodel import Session, select

from app.models.analysis import Analysis


def get_by_id_for_user(
    analysis_id: uuid.UUID, user_id: uuid.UUID, db: Session
) -> Analysis | None:
    return db.exec(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user_id)
    ).first()
