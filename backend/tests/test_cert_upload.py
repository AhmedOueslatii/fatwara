from pathlib import Path

import pytest

from app.services import storage

FIXTURES = Path(__file__).parent / "fixtures"
P12_PATH = FIXTURES / "fatwara-test.p12"
PEM_PATH = FIXTURES / "fatwara-test.pem"


def _minio_available() -> bool:
    try:
        storage.ensure_bucket()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _minio_available(), reason="MinIO not reachable in this environment"
)


@pytest.mark.asyncio
async def test_cert_upload_requires_auth(client):
    with P12_PATH.open("rb") as f:
        response = await client.post(
            "/api/v1/onboarding/cert/upload",
            files={"file": ("cert.p12", f, "application/x-pkcs12")},
            data={"password": ""},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cert_upload_persists_pem(auth_client):
    with PEM_PATH.open("rb") as f:
        response = await auth_client.post(
            "/api/v1/onboarding/cert/upload",
            files={"file": ("cert.pem", f, "application/x-pem-file")},
            data={"password": ""},
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["format"] == "pem"
    assert body["cert_id"] != "local-dev"
    assert body["days_until_expiry"] > 0

    status = await auth_client.get("/api/v1/onboarding/status")
    assert status.status_code == 200
    s = status.json()
    assert s["cert_ok"] is True
    assert s["ready_to_invoice"] is True
    assert s["cert_days_remaining"] > 0


@pytest.mark.asyncio
async def test_cert_upload_replaces_existing(auth_client):
    """Second upload for the same user should replace the first cert row, not duplicate."""
    with PEM_PATH.open("rb") as f:
        first = await auth_client.post(
            "/api/v1/onboarding/cert/upload",
            files={"file": ("cert.pem", f, "application/x-pem-file")},
            data={"password": ""},
        )
    assert first.status_code == 200
    first_id = first.json()["cert_id"]

    with PEM_PATH.open("rb") as f:
        second = await auth_client.post(
            "/api/v1/onboarding/cert/upload",
            files={"file": ("cert.pem", f, "application/x-pem-file")},
            data={"password": ""},
        )
    assert second.status_code == 200
    assert second.json()["cert_id"] == first_id


@pytest.mark.asyncio
async def test_cert_upload_rejects_garbage(auth_client):
    response = await auth_client.post(
        "/api/v1/onboarding/cert/upload",
        files={"file": ("bad.pem", b"not a real cert", "application/x-pem-file")},
        data={"password": ""},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_status_without_cert(auth_client):
    response = await auth_client.get("/api/v1/onboarding/status")
    assert response.status_code == 200
    s = response.json()
    assert s["cert_ok"] is False
    assert s["ready_to_invoice"] is False
    assert s.get("cert_expires_at") is None


def test_storage_roundtrip():
    """Smoke test the MinIO client wrapper directly."""
    import uuid as _uuid

    user_id = _uuid.uuid4()
    payload = b"-----BEGIN FAKE-----\nhello\n-----END FAKE-----\n"
    path = storage.upload_cert(user_id, payload, "pem")
    try:
        got = storage.download_cert(path)
        assert got == payload
    finally:
        storage.delete_cert(path)
