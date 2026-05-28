import uuid

from sqlmodel import Session, select

from app.models.reward import Reward


def get_or_create(user_id: uuid.UUID, db: Session) -> Reward:
    reward = db.exec(select(Reward).where(Reward.user_id == user_id)).first()
    if reward is None:
        reward = Reward(user_id=user_id)
        db.add(reward)
        db.flush()
    return reward


def grant_on_analysis(user_id: uuid.UUID, db: Session) -> Reward:
    reward = get_or_create(user_id, db)
    reward.caterpillar_balance += 1
    reward.caterpillar_total_earned += 1
    reward.analysis_count_total += 1
    db.add(reward)
    return reward
