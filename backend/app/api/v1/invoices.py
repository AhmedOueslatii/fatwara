from fastapi import APIRouter, HTTPException
from app.models.invoice import InvoiceCreate, InvoiceResponse, InvoiceStatus
from app.services.teif_generator import generate_teif_xml, validate_against_xsd
from decimal import Decimal
import uuid, datetime

router = APIRouter()

@router.post("", response_model=InvoiceResponse)
def create_invoice(invoice: InvoiceCreate):
    invoice_id = str(uuid.uuid4())
    idempotency_key = f"inv_{invoice_id}"

    xml_bytes = generate_teif_xml(invoice, invoice_id)
    valid, errors = validate_against_xsd(xml_bytes)

    if not valid:
        raise HTTPException(status_code=422, detail={"xsd_errors": errors})

    total_ht = sum(i.quantity * i.unit_price for i in invoice.items)
    total_tva = sum(
        i.quantity * i.unit_price * (i.tva_rate / Decimal("100"))
        for i in invoice.items
    )
    total_ttc = total_ht + total_tva

    return InvoiceResponse(
        invoice_id=invoice_id,
        idempotency_key=idempotency_key,
        status=InvoiceStatus.queued,
        total_ht=round(total_ht, 3),
        total_tva=round(total_tva, 3),
        total_ttc=round(total_ttc, 3),
        created_at=datetime.datetime.utcnow().isoformat(),
    )

@router.get("/{invoice_id}/status")
def invoice_status(invoice_id: str):
    # TTN polling — wired to real client in phase 2
    return {"status": "queued", "ttn_reference": None}