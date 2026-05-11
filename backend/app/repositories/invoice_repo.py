import uuid
from decimal import Decimal
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.invoice import Invoice


class IdempotencyConflict(Exception):
    pass


class InvoiceRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        invoice_id: uuid.UUID,
        user_id: uuid.UUID,
        idempotency_key: str,
        invoice_date: date,
        currency: str,
        supplier_name: str,
        supplier_matricule: str,
        customer_name: str,
        customer_matricule: str,
        total_ht: Decimal,
        total_tva: Decimal,
        total_ttc: Decimal,
        teif_xml: bytes,
        status: str = "queued",
    ) -> Invoice:
        invoice = Invoice(
            id=invoice_id,
            user_id=user_id,
            idempotency_key=idempotency_key,
            status=status,
            invoice_date=invoice_date,
            currency=currency,
            supplier_name=supplier_name,
            supplier_matricule=supplier_matricule,
            customer_name=customer_name,
            customer_matricule=customer_matricule,
            total_ht=total_ht,
            total_tva=total_tva,
            total_ttc=total_ttc,
            teif_xml=teif_xml,
        )
        self.session.add(invoice)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            if "idempotency_key" in str(exc.orig):
                raise IdempotencyConflict(idempotency_key) from exc
            raise
        await self.session.refresh(invoice)
        return invoice

    async def get_by_id(self, invoice_id: uuid.UUID) -> Invoice | None:
        result = await self.session.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        invoice_id: uuid.UUID,
        status: str,
        *,
        signed_xml: bytes | None = None,
        ttn_reference: str | None = None,
    ) -> Invoice | None:
        row = await self.get_by_id(invoice_id)
        if row is None:
            return None
        row.status = status
        if signed_xml is not None:
            row.signed_xml = signed_xml
        if ttn_reference is not None:
            row.ttn_reference = ttn_reference
        await self.session.commit()
        await self.session.refresh(row)
        return row
