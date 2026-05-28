import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app as _app

PATCH_URL = "/api/v1/analyses/{}"
TEST_EMAIL = "patch@test.com"
OTHER_EMAIL = "other_patch@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def patch_client_db():
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
                "nickname": "수정유저",
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
                "nickname": "타인수정",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        yield c, engine, analysis_id, TEST_EMAIL, OTHER_EMAIL
    _app.dependency_overrides.clear()


class TestAnalysesPatchAuth:
    def test_401_no_session(self, client: TestClient):
        fake_id = str(uuid.uuid4())
        resp = client.patch(PATCH_URL.format(fake_id), json={"memo": "test"})
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "NO_SESSION"


class TestAnalysesPatchNotFound:
    def test_404_wrong_analysis_id(self, patch_client_db):
        c, engine, _, owner, _ = patch_client_db
        fake_id = str(uuid.uuid4())
        resp = c.patch(PATCH_URL.format(fake_id), json={"memo": "test"})
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"

    def test_404_other_users_analysis(self, patch_client_db):
        c, engine, analysis_id, _, other = patch_client_db
        c.post("/api/v1/auth/login", json={"email": other, "password": TEST_PW})
        resp = c.patch(PATCH_URL.format(analysis_id), json={"memo": "test"})
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"


class TestAnalysesPatchFields:
    def test_tags_update_reflected_in_response(self, patch_client_db):
        c, engine, analysis_id, owner, _ = patch_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        new_tags = ["python", "loop"]
        resp = c.patch(PATCH_URL.format(analysis_id), json={"tags": new_tags})
        assert resp.status_code == 200
        assert resp.json()["tags"] == new_tags

    def test_memo_update_reflected_in_response(self, patch_client_db):
        c, engine, analysis_id, owner, _ = patch_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        resp = c.patch(PATCH_URL.format(analysis_id), json={"memo": "내 첫 메모"})
        assert resp.status_code == 200
        assert resp.json()["memo"] == "내 첫 메모"

    def test_is_favorite_toggle(self, patch_client_db):
        c, engine, analysis_id, owner, _ = patch_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        resp = c.patch(PATCH_URL.format(analysis_id), json={"is_favorite": True})
        assert resp.status_code == 200
        assert resp.json()["is_favorite"] is True

    def test_partial_update_preserves_other_fields(self, patch_client_db):
        from app.models.analysis import Analysis
        from sqlmodel import select

        c, engine, analysis_id, owner, _ = patch_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        c.patch(PATCH_URL.format(analysis_id), json={"tags": ["tag1"]})
        c.patch(PATCH_URL.format(analysis_id), json={"memo": "메모"})
        with Session(engine) as s:
            a = s.exec(select(Analysis)).first()
        assert a.tags == ["tag1"]
        assert a.memo == "메모"
