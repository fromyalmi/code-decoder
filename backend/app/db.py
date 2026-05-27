import os

from sqlmodel import Session, create_engine

_url = os.getenv("DATABASE_URL", "sqlite://")
_kwargs = {"check_same_thread": False} if _url.startswith("sqlite") else {}
engine = create_engine(_url, connect_args=_kwargs)


def get_session():
    with Session(engine) as session:
        yield session
