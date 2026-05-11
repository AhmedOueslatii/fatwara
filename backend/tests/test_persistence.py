import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


pytestmark = pytest.mark.asyncio


async def test_create_invoice_persists_row(auth_client, sample_invoice_payload):
    response = await auth_client.post("/api/v1/invoices", json=sample_invoice_payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "queued"
    assert body["total_ht"] == "100.000"
    assert body["total_tva"] == "19.000"
    assert body["total_ttc"] == "119.000"
    assert body["idempotency_key"] == f"inv_{body['invoice_id']}"


async def test_status_endpoint_reads_from_db(auth_client, sample_invoice_payload):
    create = await auth_client.post("/api/v1/invoices", json=sample_invoice_payload)
    invoice_id = create.json()["invoice_id"]

    status = await auth_client.get(f"/api/v1/invoices/{invoice_id}/status")
    assert status.status_code == 200
    # No cert was uploaded, so the background pipeline transitions the invoice
    # to "error". This test only checks the status endpoint can read the row.
    body = status.json()
    assert body["status"] in {"queued", "error"}
    assert body["ttn_reference"] is None


async def test_status_endpoint_404_for_unknown_invoice(auth_client):
    response = await auth_client.get(
        "/api/v1/invoices/00000000-0000-0000-0000-000000000099/status"
    )
    assert response.status_code == 404


async def test_xml_persisted_intact_as_bytes(auth_client, sample_invoice_payload):
    response = await auth_client.post("/api/v1/invoices", json=sample_invoice_payload)
    invoice_id = response.json()["invoice_id"]

    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT teif_xml FROM invoices WHERE id = :id"),
            {"id": invoice_id},
        )
        xml_bytes = result.scalar_one()
    await engine.dispose()

    assert isinstance(xml_bytes, (bytes, memoryview))
    xml = bytes(xml_bytes)
    assert xml.startswith(b"<?xml")
    assert b"urn:tn:gov:dgi:teif:1.8" in xml
    assert b"Cabinet Test" in xml
