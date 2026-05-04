from pydantic import BaseModel, Field, field_validator
from datetime import date, time
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


class TaxCategory(str, Enum):
    standard = "S"
    zero = "Z"
    exempt = "E"


class Address(BaseModel):
    street_name: str
    city_name: str
    postal_zone: str
    country_subentity: str
    country_code: str = "TN"


class Party(BaseModel):
    name: str
    matricule: str  # TN_MF — Tunisian tax registration number
    address: Address


class InvoiceLineItem(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    tva_rate: Decimal  # 19, 13, 7, or 0
    tax_category: Optional[TaxCategory] = None  # auto-derived from rate if omitted
    item_code: Optional[str] = None  # SellersItemIdentification

    @field_validator("tax_category", mode="before")
    @classmethod
    def derive_category(cls, v, info):
        if v is not None:
            return v
        rate = info.data.get("tva_rate")
        if rate is None:
            return None
        return TaxCategory.zero if rate == 0 else TaxCategory.standard


class InvoiceCreate(BaseModel):
    supplier: Party
    customer: Party
    invoice_date: date
    issue_time: Optional[time] = None  # defaults to now() at generation
    due_date: Optional[date] = None
    invoice_type_code: str = "380"  # 380=invoice, 381=credit note
    items: list[InvoiceLineItem] = Field(min_length=1)
    currency: str = "TND"
    note: Optional[str] = None


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
