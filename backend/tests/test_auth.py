import pytest


pytestmark = pytest.mark.asyncio


REGISTER_PATH = "/api/v1/auth/register"
LOGIN_PATH = "/api/v1/auth/login"
LOGOUT_PATH = "/api/v1/auth/logout"
ME_PATH = "/api/v1/auth/me"

GOOD_PAYLOAD = {"email": "alice@example.com", "password": "hunter2hunter2"}


async def test_register_returns_user_and_sets_cookie(client):
    response = await client.post(REGISTER_PATH, json=GOOD_PAYLOAD)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["is_active"] is True
    assert body["is_verified"] is False
    assert "access_token" in response.cookies


async def test_register_duplicate_email_conflicts(client):
    first = await client.post(REGISTER_PATH, json=GOOD_PAYLOAD)
    assert first.status_code == 201

    dup = await client.post(REGISTER_PATH, json=GOOD_PAYLOAD)
    assert dup.status_code == 409


async def test_register_rejects_short_password(client):
    response = await client.post(
        REGISTER_PATH,
        json={"email": "bob@example.com", "password": "short"},
    )
    assert response.status_code == 422


async def test_register_rejects_invalid_email(client):
    response = await client.post(
        REGISTER_PATH,
        json={"email": "not-an-email", "password": "hunter2hunter2"},
    )
    assert response.status_code == 422


async def test_login_with_valid_credentials_sets_cookie(client):
    register = await client.post(REGISTER_PATH, json=GOOD_PAYLOAD)
    assert register.status_code == 201
    # Drop cookies set by register so login is the only source of the cookie.
    client.cookies.clear()

    response = await client.post(LOGIN_PATH, json=GOOD_PAYLOAD)
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert response.json()["email"] == "alice@example.com"


async def test_login_with_wrong_password_is_401(client):
    await client.post(REGISTER_PATH, json=GOOD_PAYLOAD)
    response = await client.post(
        LOGIN_PATH,
        json={"email": GOOD_PAYLOAD["email"], "password": "wrongwrongwrong"},
    )
    assert response.status_code == 401


async def test_login_with_unknown_email_is_401(client):
    response = await client.post(
        LOGIN_PATH,
        json={"email": "nobody@example.com", "password": "hunter2hunter2"},
    )
    assert response.status_code == 401


async def test_me_without_cookie_is_401(client):
    response = await client.get(ME_PATH)
    assert response.status_code == 401


async def test_me_with_cookie_returns_current_user(auth_client):
    response = await auth_client.get(ME_PATH)
    assert response.status_code == 200
    assert response.json()["email"] == "tester@example.com"


async def test_logout_clears_cookie_and_blocks_me(auth_client):
    logout = await auth_client.post(LOGOUT_PATH)
    assert logout.status_code == 204

    me = await auth_client.get(ME_PATH)
    assert me.status_code == 401


async def test_invoices_require_auth(client, sample_invoice_payload):
    response = await client.post("/api/v1/invoices", json=sample_invoice_payload)
    assert response.status_code == 401


async def test_users_cannot_read_each_others_invoices(client, sample_invoice_payload):
    # User A creates an invoice.
    a_register = await client.post(
        REGISTER_PATH,
        json={"email": "a@example.com", "password": "hunter2hunter2"},
    )
    assert a_register.status_code == 201
    create = await client.post("/api/v1/invoices", json=sample_invoice_payload)
    assert create.status_code == 201
    invoice_id = create.json()["invoice_id"]

    # User B logs in (replaces A's cookie) and tries to read it.
    client.cookies.clear()
    b_register = await client.post(
        REGISTER_PATH,
        json={"email": "b@example.com", "password": "hunter2hunter2"},
    )
    assert b_register.status_code == 201

    leak = await client.get(f"/api/v1/invoices/{invoice_id}/status")
    assert leak.status_code == 404
