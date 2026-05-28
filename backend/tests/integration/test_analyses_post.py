import pytest
from fastapi.testclient import TestClient

ENDPOINT = "/api/v1/analyses"
TEST_EMAIL = "analyst@test.com"
TEST_PW = "Password1!"
TEST_NICK = "분석러"


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
