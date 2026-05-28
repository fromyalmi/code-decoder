import hashlib
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db import get_session
from app.main import app as _app
from app.models.user import User
from app.preprocessing.code_cleaner import clean

ENDPOINT = "/api/v1/analyses"
TEST_EMAIL = "analyst@test.com"
TEST_PW = "Password1!"
TEST_NICK = "분석러"
EXHAUSTED_EMAIL = "exhausted@test.com"


@pytest.fixture
def logged_in_client(client: TestClient) -> TestClient:
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PW,
            "nickname": TEST_NICK,
            "agreed_terms": True,
            "agreed_privacy": True,
        },
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PW},
    )
    return client


@pytest.fixture
def daily_exhausted_client() -> TestClient:
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
                "email": EXHAUSTED_EMAIL,
                "password": TEST_PW,
                "nickname": "한도초과",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post(
            "/api/v1/auth/login", json={"email": EXHAUSTED_EMAIL, "password": TEST_PW}
        )

        with Session(engine) as db:
            user = db.exec(select(User).where(User.email == EXHAUSTED_EMAIL)).one()
            user.daily_used = user.daily_limit
            db.add(user)
            db.commit()

        yield c

    _app.dependency_overrides.clear()


class TestAnalysesPostGate:
    def test_returns_401_when_unauthenticated(self, client: TestClient):
        resp = client.post(ENDPOINT, json={"code": "print('hi')"})
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "NO_SESSION"

    def test_returns_422_when_body_missing_code_field(
        self, logged_in_client: TestClient
    ):
        resp = logged_in_client.post(ENDPOINT, json={})
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_returns_422_when_code_is_empty_string(self, logged_in_client: TestClient):
        resp = logged_in_client.post(ENDPOINT, json={"code": ""})
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


class TestAnalysesPostServiceBoundary:
    def test_valid_request_calls_service_create(self, logged_in_client: TestClient):
        resp = logged_in_client.post(ENDPOINT, json={"code": "print('hi')"})
        assert resp.status_code == 201

    def test_language_defaults_to_python_when_omitted(
        self, logged_in_client: TestClient
    ):
        resp = logged_in_client.post(ENDPOINT, json={"code": "print('hi')"})
        assert resp.status_code == 201
        assert resp.json()["language"] == "python"


class TestAnalysesPostRawSizeValidation:
    def test_returns_400_when_code_exceeds_4000_tokens(
        self, logged_in_client: TestClient
    ):
        resp = logged_in_client.post(ENDPOINT, json={"code": "x = 1\n" * 3000})
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "INPUT_TOO_LARGE"

    def test_passes_when_code_is_within_limit(self, logged_in_client: TestClient):
        resp = logged_in_client.post(ENDPOINT, json={"code": "print('hi')"})
        assert resp.status_code == 201


class TestAnalysesPostDailyLimit:
    def test_returns_429_when_daily_limit_exhausted(
        self, daily_exhausted_client: TestClient
    ):
        resp = daily_exhausted_client.post(ENDPOINT, json={"code": "print('hi')"})
        assert resp.status_code == 429
        assert resp.json()["error"]["code"] == "DAILY_LIMIT_EXCEEDED"

    def test_passes_when_daily_limit_not_exhausted(self, logged_in_client: TestClient):
        resp = logged_in_client.post(ENDPOINT, json={"code": "print('hi')"})
        assert resp.status_code == 201


class TestAnalysesPostProcessedSizeValidation:
    def test_returns_400_when_processed_lines_exceed_200(
        self, logged_in_client: TestClient
    ):
        resp = logged_in_client.post(ENDPOINT, json={"code": "x = 1\n" * 201})
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "INPUT_TOO_LARGE"

    def test_passes_when_processed_lines_within_limit(
        self, logged_in_client: TestClient
    ):
        resp = logged_in_client.post(ENDPOINT, json={"code": "x = 1\n" * 10})
        assert resp.status_code == 201


CACHED_CODE = "print('hi')"
CACHED_EMAIL = "cached@test.com"


@pytest.fixture
def cached_client() -> TestClient:
    # ImportError in RED — AnalysisCache model not yet defined
    from app.models.cache import AnalysisCache

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
                "email": CACHED_EMAIL,
                "password": TEST_PW,
                "nickname": "캐시유저",
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post("/api/v1/auth/login", json={"email": CACHED_EMAIL, "password": TEST_PW})

        with Session(engine) as db:
            user = db.exec(select(User).where(User.email == CACHED_EMAIL)).one()
            # daily_limit=1 so a cache miss after a cache hit proves no increment
            user.daily_limit = 1
            code_sha256 = hashlib.sha256(clean(CACHED_CODE).code.encode()).hexdigest()
            db.add(
                AnalysisCache(
                    user_id=user.id,
                    code_sha256=code_sha256,
                    result={"language": "python", "cache_hit": True},
                    expires_at=datetime.utcnow() + timedelta(days=7),
                )
            )
            db.commit()

        yield c

    _app.dependency_overrides.clear()


class TestAnalysesPostCache:
    def test_cache_hit_returns_cache_hit_true(self, cached_client: TestClient):
        resp = cached_client.post(ENDPOINT, json={"code": CACHED_CODE})
        assert resp.status_code == 201
        assert resp.json()["cache_hit"] is True

    def test_cache_hit_does_not_increment_daily_used(self, cached_client: TestClient):
        # user has daily_limit=1; cache hit must not consume it
        cached_client.post(ENDPOINT, json={"code": CACHED_CODE})
        # a cache miss would return 429 if daily_used was incremented
        resp_miss = cached_client.post(ENDPOINT, json={"code": "print('miss')"})
        assert resp_miss.status_code == 201

    def test_cache_miss_proceeds_normally(self, logged_in_client: TestClient):
        resp = logged_in_client.post(ENDPOINT, json={"code": "print('cache miss')"})
        assert resp.status_code == 201
        assert resp.json().get("cache_hit") is False


LLM_CODE = "x = 1\ny = 2\nprint(x + y)"


@pytest.fixture
def llm_client_db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
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
                "nickname": TEST_NICK,
                "agreed_terms": True,
                "agreed_privacy": True,
            },
        )
        c.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PW})
        yield c, engine
    _app.dependency_overrides.clear()


class TestAnalysesPostTransaction:
    def test_analysis_row_persisted(self, llm_client_db):
        from app.models.analysis import Analysis

        client, engine = llm_client_db
        client.post(ENDPOINT, json={"code": LLM_CODE})
        with Session(engine) as s:
            rows = s.exec(select(Analysis)).all()
        assert len(rows) == 1

    def test_daily_used_incremented_atomically(self, llm_client_db):
        client, engine = llm_client_db
        client.post(ENDPOINT, json={"code": LLM_CODE})
        with Session(engine) as s:
            u = s.exec(select(User).where(User.email == TEST_EMAIL)).one()
        assert u.daily_used == 1

    def test_daily_limit_log_persisted(self, llm_client_db):
        from app.models.daily_limit_log import DailyLimitLog

        client, engine = llm_client_db
        client.post(ENDPOINT, json={"code": LLM_CODE})
        with Session(engine) as s:
            rows = s.exec(select(DailyLimitLog)).all()
        assert len(rows) == 1
        assert rows[0].reason == "analysis"


class TestAnalysesPostLLMBoundary:
    def test_response_has_forest_from_llm(self, logged_in_client: TestClient):
        resp = logged_in_client.post(ENDPOINT, json={"code": LLM_CODE})
        assert resp.status_code == 201
        assert "forest" in resp.json()

    def test_response_has_tree_from_llm(self, logged_in_client: TestClient):
        resp = logged_in_client.post(ENDPOINT, json={"code": LLM_CODE})
        assert "tree" in resp.json()
