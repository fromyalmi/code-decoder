import pytest

ME_URL = "/api/v1/me"
PATCH_ME_URL = "/api/v1/users/me"

_TEST_USER = {
    "email": "onboarding_test@example.com",
    "password": "onboardpass1",
    "nickname": "온보더",
    "agreed_terms": True,
    "agreed_privacy": True,
}
_CREDENTIALS = {"email": _TEST_USER["email"], "password": _TEST_USER["password"]}


@pytest.fixture
def logged_in_client(client):
    client.post("/api/v1/auth/signup", json=_TEST_USER)
    client.post("/api/v1/auth/login", json=_CREDENTIALS)
    return client


def test_me_first_login_flag_is_null(logged_in_client):
    """FR-AUTH-006: 가입 직후 first_login_completed_at == None (첫 접속 판별)"""
    body = logged_in_client.get(ME_URL).json()
    assert "first_login_completed_at" in body  # 필드 없으면 여기서 FAILED
    assert body["first_login_completed_at"] is None


def test_patch_complete_first_login(logged_in_client):
    """FR-AUTH-006: PATCH {first_login_completed: true} → first_login_completed_at이 datetime"""
    patch_resp = logged_in_client.patch(
        PATCH_ME_URL, json={"first_login_completed": True}
    )
    assert patch_resp.status_code == 200
    body = logged_in_client.get(ME_URL).json()
    assert "first_login_completed_at" in body  # 필드 없으면 여기서 FAILED
    assert body["first_login_completed_at"] is not None


def test_me_sound_default_is_false(logged_in_client):
    """FR-SETTINGS-003: 사운드 기본값 OFF"""
    body = logged_in_client.get(ME_URL).json()
    assert "sound_enabled" in body  # 필드 없으면 여기서 FAILED
    assert body["sound_enabled"] is False


def test_patch_sound_enabled(logged_in_client):
    """FR-SETTINGS-003: sound_enabled 토글 가능"""
    patch_resp = logged_in_client.patch(PATCH_ME_URL, json={"sound_enabled": True})
    assert patch_resp.status_code == 200
    body = logged_in_client.get(ME_URL).json()
    assert "sound_enabled" in body  # 필드 없으면 여기서 FAILED
    assert body["sound_enabled"] is True
