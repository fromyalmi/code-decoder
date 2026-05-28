"""Cycle 27 RED — FR-SEARCH-002: GET /api/v1/search?q="""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app as _app

SEARCH_URL = "/api/v1/search"
SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
ANALYSES_URL = "/api/v1/analyses"

TEST_EMAIL = "search@test.com"
OTHER_EMAIL = "other_search@test.com"
TEST_PW = "Password1!"
TEST_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def search_client():
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
                "nickname": "검색유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post(LOGIN_URL, json={"email": TEST_EMAIL, "password": TEST_PW})
        c.post(ANALYSES_URL, json={"code": TEST_CODE})

        # 타인 유저
        c.post(
            SIGNUP_URL,
            json={
                "email": OTHER_EMAIL,
                "password": TEST_PW,
                "nickname": "타인유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        yield c
    _app.dependency_overrides.clear()


def test_search_empty_query_returns_400(search_client):
    resp = search_client.get(SEARCH_URL, params={"q": ""})
    assert resp.status_code == 400


def test_search_no_results_returns_empty_list(search_client):
    resp = search_client.get(SEARCH_URL, params={"q": "절대없는쿼리xyz987"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_requires_auth(search_client):
    # 쿠키 없이 요청
    from fastapi.testclient import TestClient

    engine_inner = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine_inner)

    def _override():
        with Session(engine_inner) as s:
            yield s

    _app.dependency_overrides[get_session] = _override
    with TestClient(_app, base_url="https://testserver") as anon:
        resp = anon.get(SEARCH_URL, params={"q": "x"})
        assert resp.status_code == 401
    _app.dependency_overrides.clear()

    # 원래 fixture의 override 복구
    def _restore():
        with Session(
            create_engine(
                "sqlite://",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        ) as s:
            yield s

    _app.dependency_overrides[get_session] = _restore


def test_search_returns_list(search_client):
    resp = search_client.get(SEARCH_URL, params={"q": "x"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_search_result_has_required_fields(search_client):
    resp = search_client.get(SEARCH_URL, params={"q": "x"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    item = items[0]
    assert "id" in item
    assert "created_at" in item
    assert "language" in item
    assert "code_preview" in item
    assert "tags" in item
    assert "matched_field" in item


def test_search_code_original_match(search_client):
    # "x + y" (공백 있음)은 code_original에만 있고 tree stub("x=1 → y=2 → print(x+y)")에는 없음
    resp = search_client.get(SEARCH_URL, params={"q": "x + y"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    fields = [item["matched_field"] for item in items]
    assert "code_original" in fields


def test_search_forest_match(search_client):
    # conftest의 LLM stub에서 forest = "두 수를 더해 출력하는 프로그램입니다."
    resp = search_client.get(SEARCH_URL, params={"q": "더해"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert any(item["matched_field"] == "forest" for item in items)


def test_search_only_own_analyses(search_client):
    # 타인 유저로 전환 후 검색 → 결과 없어야 함 (타인 분석 노출 금지)
    search_client.post(LOGIN_URL, json={"email": OTHER_EMAIL, "password": TEST_PW})
    resp = search_client.get(SEARCH_URL, params={"q": "print"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_code_preview_max_40chars(search_client):
    resp = search_client.get(SEARCH_URL, params={"q": "x"})
    items = resp.json()
    assert len(items) >= 1
    assert len(items[0]["code_preview"]) <= 40
