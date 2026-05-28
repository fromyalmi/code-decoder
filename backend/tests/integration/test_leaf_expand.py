import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db import get_session
from app.main import app as _app
from app.models.user import User

EXPAND_URL = "/api/v1/analyses/{}/leaves/expand"
TEST_EMAIL = "expand@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def expand_client_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def _override():
        with Session(engine) as s:
            yield s

    _app.dependency_overrides[get_session] = _override
    with TestClient(_app, base_url="https://testserver") as c:
        c.post(
            "/api/v1/auth/signup",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PW,
                "nickname": "확장유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PW})
        resp = c.post("/api/v1/analyses", json={"code": TEST_CODE})
        analysis_id = resp.json()["id"]
        yield c, engine, analysis_id
    _app.dependency_overrides.clear()


def _patch_user(engine, email: str, **kwargs):
    with Session(engine) as s:
        u = s.exec(select(User).where(User.email == email)).one()
        for k, v in kwargs.items():
            setattr(u, k, v)
        s.add(u)
        s.commit()


class TestLeafExpandAuth:
    def test_401_no_session(self, client: TestClient):
        fake_id = str(uuid.uuid4())
        resp = client.post(EXPAND_URL.format(fake_id), json={"line_no": 1})
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "NO_SESSION"


class TestLeafExpandNotFound:
    def test_404_wrong_analysis_id(self, expand_client_db):
        c, engine, _ = expand_client_db
        fake_id = str(uuid.uuid4())
        resp = c.post(EXPAND_URL.format(fake_id), json={"line_no": 1})
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"


class TestLeafExpandIncrement:
    def test_first_expand_increments_leaf_counter(self, expand_client_db):
        c, engine, analysis_id = expand_client_db
        _patch_user(engine, TEST_EMAIL, leaf_counter=0, daily_used=1)
        resp = c.post(EXPAND_URL.format(analysis_id), json={"line_no": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert data["outcome"] == "incremented"
        assert data["leaf_counter"] == 1
        assert data["daily_used"] == 1
        assert "deep_text" in data

    def test_fourth_expand_counter_becomes_4(self, expand_client_db):
        c, engine, analysis_id = expand_client_db
        _patch_user(engine, TEST_EMAIL, leaf_counter=3, daily_used=1)
        resp = c.post(EXPAND_URL.format(analysis_id), json={"line_no": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["outcome"] == "incremented"
        assert data["leaf_counter"] == 4


class TestLeafExpandCharged:
    def test_fifth_expand_charges_daily_used(self, expand_client_db):
        c, engine, analysis_id = expand_client_db
        _patch_user(engine, TEST_EMAIL, leaf_counter=4, daily_used=1, daily_limit=10)
        resp = c.post(EXPAND_URL.format(analysis_id), json={"line_no": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert data["outcome"] == "charged"
        assert data["leaf_counter"] == 0
        assert data["daily_used"] == 2


class TestLeafExpandLimitExceeded:
    def test_fifth_expand_with_zero_daily_remaining_returns_429(self, expand_client_db):
        c, engine, analysis_id = expand_client_db
        _patch_user(engine, TEST_EMAIL, leaf_counter=4, daily_used=10, daily_limit=10)
        resp = c.post(EXPAND_URL.format(analysis_id), json={"line_no": 1})
        assert resp.status_code == 429
        assert resp.json()["error"]["code"] == "DAILY_LIMIT_EXCEEDED"
