import uuid
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.core.database import get_session
from app.models.db.user import User
from app.models.invoice import InvoiceCreate, InvoiceResponse, InvoiceStatus
from app.repositories.invoice_repo import IdempotencyConflict, InvoiceRepo
from app.services.invoice_pipeline import run_pipeline
from app.services.teif_generator import generate_teif_xml, validate_against_xsd

router = APIRouter()


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: InvoiceCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    invoice_id = uuid.uuid4()
    idempotency_key = f"inv_{invoice_id}"

    xml_bytes = generate_teif_xml(invoice, str(invoice_id))
    valid, errors = validate_against_xsd(xml_bytes)
    if not valid and any("not bundled" not in e.lower() for e in errors):
        # Genuine schema violations block; "XSD not bundled" is a known POC gap.
        raise HTTPException(status_code=422, detail={"xsd_errors": errors})

    total_ht = sum((i.quantity * i.unit_price for i in invoice.items), Decimal("0"))
    total_tva = sum(
        (i.quantity * i.unit_price * (i.tva_rate / Decimal("100")) for i in invoice.items),
        Decimal("0"),
    )
    total_ttc = total_ht + total_tva

    repo = InvoiceRepo(session)
    try:
        row = await repo.create(
            invoice_id=invoice_id,
            user_id=user.id,
            idempotency_key=idempotency_key,
            invoice_date=invoice.invoice_date,
            currency=invoice.currency,
            supplier_name=invoice.supplier.name,
            supplier_matricule=invoice.supplier.matricule,
            customer_name=invoice.customer.name,
            customer_matricule=invoice.customer.matricule,
            total_ht=total_ht.quantize(Decimal("0.001")),
            total_tva=total_tva.quantize(Decimal("0.001")),
            total_ttc=total_ttc.quantize(Decimal("0.001")),
            teif_xml=xml_bytes,
            status=InvoiceStatus.queued.value,
        )
    except IdempotencyConflict:
        raise HTTPException(status_code=409, detail="Idempotency key conflict")

    background_tasks.add_task(run_pipeline, invoice_id, user.id)

    return InvoiceResponse(
        invoice_id=str(row.id),
        idempotency_key=row.idempotency_key,
        status=InvoiceStatus(row.status),
        ttn_reference=row.ttn_reference,
        total_ht=row.total_ht,
        total_tva=row.total_tva,
        total_ttc=row.total_ttc,
        created_at=row.created_at.isoformat(),
    )


@router.get("/{invoice_id}/status")
async def invoice_status(
    invoice_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = InvoiceRepo(session)
    row = await repo.get_by_id(invoice_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"status": row.status, "ttn_reference": row.ttn_reference}
