import pytest

LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/me"

_TEST_USER = {
    "email": "session_test@example.com",
    "password": "testpass123",
    "nickname": "세션테스터",
    "agreed_terms": True,
    "agreed_privacy": True,
}
_CREDENTIALS = {"email": _TEST_USER["email"], "password": _TEST_USER["password"]}


@pytest.fixture
def registered_client(client):
    client.post("/api/v1/auth/signup", json=_TEST_USER)
    return client


def test_login_success_returns_signed_cookie(registered_client):
    resp = registered_client.post(LOGIN_URL, json=_CREDENTIALS)
    assert resp.status_code == 200
    assert "set-cookie" in resp.headers
    cookie = resp.headers["set-cookie"]
    assert "httponly" in cookie.lower()
    assert "samesite=lax" in cookie.lower()


def test_login_wrong_password_returns_generic_message(registered_client):
    resp = registered_client.post(
        LOGIN_URL, json={**_CREDENTIALS, "password": "wrongpass1"}
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "InvalidCredentials"


def test_login_nonexistent_email_returns_generic_message(registered_client):
    nonexistent = registered_client.post(
        LOGIN_URL, json={"email": "nobody@example.com", "password": "anypass123"}
    )
    wrong_pw = registered_client.post(
        LOGIN_URL, json={**_CREDENTIALS, "password": "wrongpass1"}
    )
    assert nonexistent.status_code == 401
    assert nonexistent.json()["error"]["code"] == "InvalidCredentials"
    # §22.2: 어느 쪽이 틀렸는지 노출 금지 — 두 케이스 메시지 동일해야 함
    assert nonexistent.json()["error"]["message"] == wrong_pw.json()["error"]["message"]


def test_login_locks_after_5_failures(registered_client):
    bad = {**_CREDENTIALS, "password": "wrongpass1"}
    for _ in range(5):
        registered_client.post(LOGIN_URL, json=bad)
    resp = registered_client.post(LOGIN_URL, json=bad)
    assert resp.status_code == 429
    assert resp.json()["error"]["code"] == "AccountLocked"


def test_logout_clears_cookie(registered_client):
    registered_client.post(LOGIN_URL, json=_CREDENTIALS)
    logout_resp = registered_client.post(LOGOUT_URL)
    assert logout_resp.status_code == 200
    set_cookie = logout_resp.headers.get("set-cookie", "")
    assert "max-age=0" in set_cookie.lower() or "expires=" in set_cookie.lower()


def test_protected_me_without_cookie_returns_401(client):
    resp = client.get(ME_URL)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "NO_SESSION"


def test_protected_me_with_valid_cookie_returns_user(registered_client):
    registered_client.post(LOGIN_URL, json=_CREDENTIALS)
    me_resp = registered_client.get(ME_URL)
    assert me_resp.status_code == 200
    body = me_resp.json()
    assert "email" in body
    assert "nickname" in body
    assert "password_hash" not in body


def test_protected_me_after_logout_returns_401(registered_client):
    registered_client.post(LOGIN_URL, json=_CREDENTIALS)
    registered_client.post(LOGOUT_URL)
    me_resp = registered_client.get(ME_URL)
    assert me_resp.status_code == 401
