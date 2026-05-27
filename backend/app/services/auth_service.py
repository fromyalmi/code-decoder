from datetime import datetime, timedelta, timezone

import bcrypt
from sqlmodel import Session, select

from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest


class EmailAlreadyExists(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class AccountLocked(Exception):
    pass


def signup(req: SignupRequest, session: Session) -> User:
    if session.exec(select(User).where(User.email == req.email)).first():
        raise EmailAlreadyExists

    hashed = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    user = User(
        email=req.email, password_hash=hashed.decode("utf-8"), nickname=req.nickname
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login(req: LoginRequest, session: Session) -> User:
    user = session.exec(select(User).where(User.email == req.email)).first()
    if not user:
        raise InvalidCredentials

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if user.login_locked_until and user.login_locked_until > now:
        raise AccountLocked

    if not bcrypt.checkpw(
        req.password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        user.login_failed_count = (user.login_failed_count or 0) + 1
        if user.login_failed_count >= 5:
            user.login_locked_until = now + timedelta(minutes=15)
        session.add(user)
        session.commit()
        raise InvalidCredentials

    user.login_failed_count = 0
    user.login_locked_until = None
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
