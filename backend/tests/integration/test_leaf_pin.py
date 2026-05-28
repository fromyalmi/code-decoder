import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db import get_session
from app.main import app as _app

PIN_URL = "/api/v1/analyses/{}/leaves/{}/pin"
TEST_EMAIL = "pin@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"
DEEP_TEXT = "이 라인은 정수 1을 변수 x에 바인딩하는 할당문이야."


@pytest.fixture
def pin_client_db():
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
                "nickname": "핀유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PW})
        resp = c.post("/api/v1/analyses", json={"code": TEST_CODE})
        analysis_id = resp.json()["id"]
        yield c, engine, analysis_id
    _app.dependency_overrides.clear()


class TestLeafPinAuth:
    def test_401_no_session(self, client: TestClient):
        fake_id = str(uuid.uuid4())
        resp = client.patch(PIN_URL.format(fake_id, 1), json={"deep_text": DEEP_TEXT})
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "NO_SESSION"


class TestLeafPinNotFound:
    def test_404_wrong_analysis_id(self, pin_client_db):
        c, engine, _ = pin_client_db
        fake_id = str(uuid.uuid4())
        resp = c.patch(PIN_URL.format(fake_id, 1), json={"deep_text": DEEP_TEXT})
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"


class TestLeafPinSave:
    def test_pin_returns_204(self, pin_client_db):
        c, engine, analysis_id = pin_client_db
        resp = c.patch(PIN_URL.format(analysis_id, 1), json={"deep_text": DEEP_TEXT})
        assert resp.status_code == 204

    def test_pin_creates_deep_pinned_line_explanation(self, pin_client_db):
        from app.models.line_explanation import LineExplanation

        c, engine, analysis_id = pin_client_db
        c.patch(PIN_URL.format(analysis_id, 1), json={"deep_text": DEEP_TEXT})
        with Session(engine) as s:
            rows = s.exec(select(LineExplanation)).all()
        pinned = [r for r in rows if r.tier == "deep_pinned"]
        assert len(pinned) == 1
        assert pinned[0].line_no == 1
        assert pinned[0].deep == DEEP_TEXT
        assert pinned[0].is_pinned is True

    def test_pin_idempotent(self, pin_client_db):
        from app.models.line_explanation import LineExplanation

        c, engine, analysis_id = pin_client_db
        c.patch(PIN_URL.format(analysis_id, 1), json={"deep_text": DEEP_TEXT})
        resp2 = c.patch(PIN_URL.format(analysis_id, 1), json={"deep_text": DEEP_TEXT})
        assert resp2.status_code == 204
        with Session(engine) as s:
            rows = s.exec(select(LineExplanation)).all()
        pinned = [r for r in rows if r.tier == "deep_pinned"]
        assert len(pinned) == 2
