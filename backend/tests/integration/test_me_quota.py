"""Cycle 25 RED — FR-ANALYSIS-008: GET /me 할당량 필드 (daily_used/daily_limit/daily_remaining/leaf_counter)"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app as _app

ME_URL = "/api/v1/me"
SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
ANALYSES_URL = "/api/v1/analyses"

TEST_EMAIL = "quota@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def me_client():
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
            SIGNUP_URL,
            json={
                "email": TEST_EMAIL,
                "password": TEST_PW,
                "nickname": "할당량유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post(LOGIN_URL, json={"email": TEST_EMAIL, "password": TEST_PW})
        yield c
    _app.dependency_overrides.clear()


def test_me_returns_daily_used(me_client):
    resp = me_client.get(ME_URL)
    assert resp.status_code == 200
    assert resp.json()["daily_used"] == 0


def test_me_returns_daily_limit(me_client):
    resp = me_client.get(ME_URL)
    assert resp.status_code == 200
    assert resp.json()["daily_limit"] == 10


def test_me_returns_daily_remaining(me_client):
    resp = me_client.get(ME_URL)
    assert resp.status_code == 200
    assert resp.json()["daily_remaining"] == 10


def test_me_returns_leaf_counter(me_client):
    resp = me_client.get(ME_URL)
    assert resp.status_code == 200
    assert resp.json()["leaf_counter"] == 0


def test_me_daily_used_increments_after_analysis(me_client):
    me_client.post(ANALYSES_URL, json={"code": TEST_CODE})
    resp = me_client.get(ME_URL)
    assert resp.status_code == 200
    data = resp.json()
    assert data["daily_used"] == 1
    assert data["daily_remaining"] == 9
