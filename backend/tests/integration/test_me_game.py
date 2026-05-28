"""Cycle 26 RED — FR-GAME-001~005: GET /me reward/title 필드 + 분석 시 보상 적립"""

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

TEST_EMAIL = "game@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def game_client():
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
                "nickname": "게임유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post(LOGIN_URL, json={"email": TEST_EMAIL, "password": TEST_PW})
        yield c
    _app.dependency_overrides.clear()


# ── reward 필드 ──────────────────────────────────────────────────────────────


def test_me_returns_reward_object(game_client):
    resp = game_client.get(ME_URL)
    assert resp.status_code == 200
    assert "reward" in resp.json()


def test_me_reward_caterpillar_balance_default(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["reward"]["caterpillar_balance"] == 0


def test_me_reward_streak_current_default(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["reward"]["streak_current"] == 0


def test_me_reward_shield_count_default(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["reward"]["shield_count"] == 0


def test_me_reward_analysis_count_total_default(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["reward"]["analysis_count_total"] == 0


# ── title 필드 ───────────────────────────────────────────────────────────────


def test_me_returns_title_object(game_client):
    resp = game_client.get(ME_URL)
    assert resp.status_code == 200
    assert "title" in resp.json()


def test_me_title_stage_1_by_default(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["title"]["stage"] == 1


def test_me_title_emoji_stage_1(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["title"]["emoji"] == "🥚🦜"


def test_me_title_label_stage_1(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["title"]["label"] == "알 속의 코뉴"


def test_me_title_next_threshold_stage_1(game_client):
    resp = game_client.get(ME_URL)
    assert resp.json()["title"]["next_threshold"] == 10


# ── 분석 1회 후 보상 적립 ────────────────────────────────────────────────────


def test_caterpillar_balance_increments_after_analysis(game_client):
    game_client.post(ANALYSES_URL, json={"code": TEST_CODE})
    resp = game_client.get(ME_URL)
    assert resp.json()["reward"]["caterpillar_balance"] == 1


def test_analysis_count_total_increments_after_analysis(game_client):
    game_client.post(ANALYSES_URL, json={"code": TEST_CODE})
    resp = game_client.get(ME_URL)
    assert resp.json()["reward"]["analysis_count_total"] == 1
