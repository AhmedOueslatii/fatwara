from pydantic import BaseModel, UUID4
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

class InvoiceStatus(str, Enum):
    draft = "draft"
    queued = "queued"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"
    error = "error"

class InvoiceLineItem(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    tva_rate: Decimal  # 19.0, 7.0, or 0.0

class InvoiceCreate(BaseModel):
    supplier_name: str
    supplier_matricule: str
    supplier_address: str
    buyer_name: str
    buyer_matricule: str
    invoice_date: date
    items: list[InvoiceLineItem]
    currency: str = "TND"

class InvoiceResponse(BaseModel):
    invoice_id: str
    idempotency_key: str
    status: InvoiceStatus
    ttn_reference: Optional[str] = None
    total_ht: Decimal
    total_tva: Decimal
    total_ttc: Decimal
    created_at: str

class OnboardingStatus(BaseModel):
    cert_ok: bool
    ttn_ok: bool
    ready_to_invoice: bool
    cert_expires_at: Optional[str] = None
    cert_days_remaining: Optional[int] = None