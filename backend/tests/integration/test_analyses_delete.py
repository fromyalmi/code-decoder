import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db import get_session
from app.main import app as _app

DELETE_URL = "/api/v1/analyses/{}"
TEST_EMAIL = "delete@test.com"
OTHER_EMAIL = "other_delete@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def delete_client_db():
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
                "nickname": "삭제유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PW})
        resp = c.post("/api/v1/analyses", json={"code": TEST_CODE})
        analysis_id = resp.json()["id"]
        c.post(
            "/api/v1/auth/signup",
            json={
                "email": OTHER_EMAIL,
                "password": TEST_PW,
                "nickname": "타인삭제",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        yield c, engine, analysis_id, TEST_EMAIL, OTHER_EMAIL
    _app.dependency_overrides.clear()


class TestAnalysesDeleteAuth:
    def test_401_no_session(self, client: TestClient):
        fake_id = str(uuid.uuid4())
        resp = client.delete(DELETE_URL.format(fake_id))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "NO_SESSION"


class TestAnalysesDeleteNotFound:
    def test_404_wrong_analysis_id(self, delete_client_db):
        c, engine, _, owner, _ = delete_client_db
        fake_id = str(uuid.uuid4())
        resp = c.delete(DELETE_URL.format(fake_id))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"

    def test_404_other_users_analysis(self, delete_client_db):
        c, engine, analysis_id, _, other = delete_client_db
        c.post("/api/v1/auth/login", json={"email": other, "password": TEST_PW})
        resp = c.delete(DELETE_URL.format(analysis_id))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"


class TestAnalysesDeleteSuccess:
    def test_delete_returns_204(self, delete_client_db):
        c, engine, analysis_id, owner, _ = delete_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        resp = c.delete(DELETE_URL.format(analysis_id))
        assert resp.status_code == 204

    def test_delete_removes_row_from_db(self, delete_client_db):
        from app.models.analysis import Analysis

        c, engine, analysis_id, owner, _ = delete_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        c.delete(DELETE_URL.format(analysis_id))
        with Session(engine) as s:
            row = s.exec(select(Analysis)).first()
        assert row is None

    def test_delete_then_get_returns_404(self, delete_client_db):
        c, engine, analysis_id, owner, _ = delete_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        c.delete(DELETE_URL.format(analysis_id))
        resp = c.get(f"/api/v1/analyses/{analysis_id}")
        assert resp.status_code == 404
