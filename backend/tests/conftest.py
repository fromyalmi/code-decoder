import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app

_SIGNUP_URL = "/api/v1/auth/signup"
_LOGIN_URL = "/api/v1/auth/login"


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app, base_url="https://testserver") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def rollback_db():
    yield
