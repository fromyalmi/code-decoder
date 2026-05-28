import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app as _app

DETAIL_URL = "/api/v1/analyses/{}"
TEST_EMAIL = "detail@test.com"
OTHER_EMAIL = "other_detail@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def detail_client_db():
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
                "nickname": "상세유저",
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
                "nickname": "타인유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        yield c, engine, analysis_id, TEST_EMAIL, OTHER_EMAIL
    _app.dependency_overrides.clear()


class TestAnalysesDetailAuth:
    def test_401_no_session(self, client: TestClient):
        fake_id = str(uuid.uuid4())
        resp = client.get(DETAIL_URL.format(fake_id))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "NO_SESSION"


class TestAnalysesDetailNotFound:
    def test_404_wrong_analysis_id(self, detail_client_db):
        c, engine, _, owner, _ = detail_client_db
        fake_id = str(uuid.uuid4())
        resp = c.get(DETAIL_URL.format(fake_id))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"

    def test_404_other_users_analysis(self, detail_client_db):
        c, engine, analysis_id, _, other = detail_client_db
        c.post("/api/v1/auth/login", json={"email": other, "password": TEST_PW})
        resp = c.get(DETAIL_URL.format(analysis_id))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"


class TestAnalysesDetailResponse:
    def _get_owner_analysis(self, detail_client_db):
        c, engine, analysis_id, owner, _ = detail_client_db
        c.post("/api/v1/auth/login", json={"email": owner, "password": TEST_PW})
        return c.get(DETAIL_URL.format(analysis_id))

    def test_200_for_owner(self, detail_client_db):
        resp = self._get_owner_analysis(detail_client_db)
        assert resp.status_code == 200

    def test_response_has_core_fields(self, detail_client_db):
        resp = self._get_owner_analysis(detail_client_db)
        data = resp.json()
        for field in (
            "id",
            "forest",
            "tree",
            "tags",
            "memo",
            "is_favorite",
            "created_at",
        ):
            assert field in data

    def test_response_has_line_explanations_short_only(self, detail_client_db):
        resp = self._get_owner_analysis(detail_client_db)
        les = resp.json()["line_explanations"]
        assert isinstance(les, list)
        assert len(les) == 3  # stub: 3 short explanations
        assert all("short" in le for le in les)

    def test_response_has_deep_leaves_from_deep_core(self, detail_client_db):
        resp = self._get_owner_analysis(detail_client_db)
        deep = resp.json()["deep_leaves"]
        assert isinstance(deep, list)
        assert len(deep) == 5  # stub: 5 deep_core leaves

    def test_response_has_key_concepts(self, detail_client_db):
        resp = self._get_owner_analysis(detail_client_db)
        kcs = resp.json()["key_concepts"]
        assert isinstance(kcs, list)
        assert len(kcs) == 1
        assert "name" in kcs[0] and "definition" in kcs[0]
