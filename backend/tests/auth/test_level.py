import pytest

ME_URL = "/api/v1/me"
PATCH_ME_URL = "/api/v1/users/me"

_TEST_USER = {
    "email": "level_test@example.com",
    "password": "levelpass123",
    "nickname": "레벨테스터",
    "agreed_terms": True,
    "agreed_privacy": True,
}
_CREDENTIALS = {"email": _TEST_USER["email"], "password": _TEST_USER["password"]}


@pytest.fixture
def logged_in_client(client):
    client.post("/api/v1/auth/signup", json=_TEST_USER)
    client.post("/api/v1/auth/login", json=_CREDENTIALS)
    return client


def test_me_default_level_is_1(logged_in_client):
    """FR-AUTH-005: 건너뛰기(미설정) = 서버 기본값 level=1, level_auto=False"""
    body = logged_in_client.get(ME_URL).json()
    assert "level" in body  # /me에 level 필드 없으면 여기서 FAILED
    assert body["level"] == 1
    assert body.get("level_auto") is False


def test_patch_level_valid_1_to_3(logged_in_client):
    """FR-AUTH-004: level 1~3 정상 저장"""
    patch_resp = logged_in_client.patch(PATCH_ME_URL, json={"level": 2})
    assert patch_resp.status_code == 200
    body = logged_in_client.get(ME_URL).json()
    assert body["level"] == 2


def test_patch_level_4_sets_auto_true(logged_in_client):
    """FR-AUTH-004: level=4 선택 시 level_auto=True"""
    patch_resp = logged_in_client.patch(PATCH_ME_URL, json={"level": 4})
    assert patch_resp.status_code == 200
    body = logged_in_client.get(ME_URL).json()
    assert body["level"] == 4
    assert body.get("level_auto") is True


def test_patch_level_invalid_out_of_range(logged_in_client):
    """범위 초과 level → 422 VALIDATION_ERROR"""
    resp = logged_in_client.patch(PATCH_ME_URL, json={"level": 5})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_level_requires_auth(client):
    """인증 없이 PATCH → 401 NO_SESSION"""
    resp = client.patch(PATCH_ME_URL, json={"level": 2})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "NO_SESSION"
