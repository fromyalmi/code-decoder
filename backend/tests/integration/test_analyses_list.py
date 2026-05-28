import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db import get_session
from app.main import app as _app
from app.models.user import User

LIST_URL = "/api/v1/analyses"
TEST_EMAIL = "list@test.com"
TEST_PW = "Password1!"


@pytest.fixture
def list_client_db():
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
                "nickname": "목록유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PW})
        with Session(engine) as s:
            u = s.exec(select(User).where(User.email == TEST_EMAIL)).one()
            u.daily_limit = 100
            s.add(u)
            s.commit()
        yield c, engine
    _app.dependency_overrides.clear()


def _post_analysis(client: TestClient, code: str = "x = 1") -> str:
    resp = client.post("/api/v1/analyses", json={"code": code})
    return resp.json()["id"]


class TestAnalysesListAuth:
    def test_401_no_session(self, client: TestClient):
        resp = client.get(LIST_URL)
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "NO_SESSION"


class TestAnalysesListEmpty:
    def test_empty_list_when_no_analyses(self, list_client_db):
        c, engine = list_client_db
        resp = c.get(LIST_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["next_cursor"] is None


class TestAnalysesListItems:
    def test_item_has_required_fields(self, list_client_db):
        c, engine = list_client_db
        _post_analysis(c, "x = 1\ny = 2\nprint(x + y)")
        resp = c.get(LIST_URL)
        item = resp.json()["items"][0]
        assert "id" in item
        assert "created_at" in item
        assert "language" in item
        assert "code_preview" in item
        assert "tags" in item
        assert "is_favorite" in item

    def test_code_preview_is_40_chars_max(self, list_client_db):
        c, engine = list_client_db
        long_code = "x" * 100
        _post_analysis(c, long_code)
        resp = c.get(LIST_URL)
        preview = resp.json()["items"][0]["code_preview"]
        assert len(preview) <= 40

    def test_code_preview_matches_code_start(self, list_client_db):
        c, engine = list_client_db
        _post_analysis(c, "print('hello world')")
        resp = c.get(LIST_URL)
        preview = resp.json()["items"][0]["code_preview"]
        assert preview == "print('hello world')"

    def test_next_cursor_null_when_20_or_fewer(self, list_client_db):
        c, engine = list_client_db
        for i in range(3):
            _post_analysis(c, f"x = {i}")
        resp = c.get(LIST_URL)
        assert resp.json()["next_cursor"] is None

    def test_next_cursor_present_when_more_than_20(self, list_client_db):
        c, engine = list_client_db
        for i in range(21):
            _post_analysis(c, f"x = {i}")
        resp = c.get(LIST_URL)
        data = resp.json()
        assert len(data["items"]) == 20
        assert data["next_cursor"] is not None

    def test_cursor_pagination_returns_next_page(self, list_client_db):
        c, engine = list_client_db
        for i in range(21):
            _post_analysis(c, f"x = {i}")
        resp1 = c.get(LIST_URL)
        cursor = resp1.json()["next_cursor"]
        resp2 = c.get(LIST_URL, params={"cursor": cursor})
        assert resp2.status_code == 200
        page2 = resp2.json()["items"]
        assert len(page2) == 1
        assert page2[0]["id"] not in [it["id"] for it in resp1.json()["items"]]
