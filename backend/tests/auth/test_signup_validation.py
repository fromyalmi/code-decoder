import pytest


SIGNUP_URL = "/api/v1/auth/signup"

VALID_BASE = {
    "email": "user@example.com",
    "password": "validpass1",
    "nickname": "코뉴",
    "agreed_terms": True,
    "agreed_privacy": True,
}


def test_signup_rejects_invalid_email_format(client):
    resp = client.post(SIGNUP_URL, json={**VALID_BASE, "email": "not-an-email"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_signup_rejects_password_under_8_chars(client):
    resp = client.post(SIGNUP_URL, json={**VALID_BASE, "password": "1234567"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    "nickname",
    [
        pytest.param("가", id="too_short_1_char"),
        pytest.param("가나다라마바사아자차카타파하", id="too_long_13_chars"),
    ],
)
def test_signup_rejects_nickname_out_of_range(client, nickname):
    resp = client.post(SIGNUP_URL, json={**VALID_BASE, "nickname": nickname})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_signup_rejects_duplicate_email(client):
    payload = {**VALID_BASE, "email": "dupe@example.com"}
    client.post(SIGNUP_URL, json=payload)  # first — ignored
    resp = client.post(SIGNUP_URL, json=payload)  # second — must be 409
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "EmailAlreadyExists"
