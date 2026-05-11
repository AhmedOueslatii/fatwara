import uuid
from pathlib import Path

import pytest

from app.core.config import settings
from app.services import storage
from app.services.invoice_pipeline import run_pipeline

FIXTURES = Path(__file__).parent / "fixtures"
P12_PATH = FIXTURES / "fatwara-test.p12"


def _minio_available() -> bool:
    try:
        storage.ensure_bucket()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _minio_available(), reason="MinIO not reachable in this environment"
)


async def _upload_cert(auth_client) -> None:
    with P12_PATH.open("rb") as f:
        response = await auth_client.post(
            "/api/v1/onboarding/cert/upload",
            files={"file": ("cert.p12", f, "application/x-pkcs12")},
            data={"password": ""},
        )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_pipeline_accepts_invoice(auth_client, sample_invoice_payload, monkeypatch):
    monkeypatch.setattr(settings, "TTN_MOCK_MODE", "accept")
    await _upload_cert(auth_client)

    response = await auth_client.post("/api/v1/invoices", json=sample_invoice_payload)
    assert response.status_code == 201, response.text
    body = response.json()
    invoice_id = body["invoice_id"]

    # ASGITransport awaits background tasks before returning the response,
    # so by the time we poll status the pipeline has already run.
    status = await auth_client.get(f"/api/v1/invoices/{invoice_id}/status")
    assert status.status_code == 200
    s = status.json()
    assert s["status"] == "accepted"
    assert s["ttn_reference"] is not None
    assert s["ttn_reference"].startswith("TTN-MOCK-")


@pytest.mark.asyncio
async def test_pipeline_rejects_invoice(auth_client, sample_invoice_payload, monkeypatch):
    monkeypatch.setattr(settings, "TTN_MOCK_MODE", "reject")
    await _upload_cert(auth_client)

    response = await auth_client.post("/api/v1/invoices", json=sample_invoice_payload)
    assert response.status_code == 201
    invoice_id = response.json()["invoice_id"]

    status = await auth_client.get(f"/api/v1/invoices/{invoice_id}/status")
    s = status.json()
    assert s["status"] == "rejected"
    assert s["ttn_reference"] is not None  # reference returned even on reject


@pytest.mark.asyncio
async def test_pipeline_handles_ttn_timeout(auth_client, sample_invoice_payload, monkeypatch):
    monkeypatch.setattr(settings, "TTN_MOCK_MODE", "timeout")
    await _upload_cert(auth_client)

    response = await auth_client.post("/api/v1/invoices", json=sample_invoice_payload)
    invoice_id = response.json()["invoice_id"]

    status = await auth_client.get(f"/api/v1/invoices/{invoice_id}/status")
    assert status.json()["status"] == "error"


@pytest.mark.asyncio
async def test_pipeline_errors_without_cert(auth_client, sample_invoice_payload):
    # No cert uploaded — pipeline should mark invoice as error
    response = await auth_client.post("/api/v1/invoices", json=sample_invoice_payload)
    assert response.status_code == 201
    invoice_id = response.json()["invoice_id"]

    status = await auth_client.get(f"/api/v1/invoices/{invoice_id}/status")
    assert status.json()["status"] == "error"


@pytest.mark.asyncio
async def test_run_pipeline_missing_invoice():
    # Calling pipeline with a nonexistent invoice_id is a no-op, not a crash
    await run_pipeline(uuid.uuid4(), uuid.uuid4())
