import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db import get_session
from app.main import app as _app
from app.models.user import User

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
