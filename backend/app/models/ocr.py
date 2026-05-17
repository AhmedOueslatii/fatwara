"""Schema for OCR-extracted invoice data.

Distinct from InvoiceCreate because OCR output is best-effort: matricules may be
missing, addresses may be partial, totals may not reconcile. The frontend
pre-fills the form with this and lets the user fix anything before submitting.
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator


class ExtractedAddress(BaseModel):
    street_name: Optional[str] = None
    city_name: Optional[str] = None
    postal_zone: Optional[str] = None
    country_subentity: Optional[str] = None


class ExtractedParty(BaseModel):
    name: Optional[str] = None
    matricule: Optional[str] = None
    address: ExtractedAddress = ExtractedAddress()

    @field_validator("address", mode="before")
    @classmethod
    def _coerce_null_address(cls, v):
        return ExtractedAddress() if v is None else v


class ExtractedLineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    tva_rate: Optional[Decimal] = None  # 0 / 7 / 13 / 19


class ExtractedInvoice(BaseModel):
    supplier: ExtractedParty = ExtractedParty()
    customer: ExtractedParty = ExtractedParty()
    invoice_date: Optional[str] = None  # ISO YYYY-MM-DD; frontend parses
    items: list[ExtractedLineItem] = []
    currency: Optional[str] = "TND"
    note: Optional[str] = None

    @field_validator("supplier", "customer", mode="before")
    @classmethod
    def _coerce_null_party(cls, v):
        return ExtractedParty() if v is None else v

    @field_validator("items", mode="before")
    @classmethod
    def _coerce_null_items(cls, v):
        return [] if v is None else v


class ExtractResponse(BaseModel):
    extracted: ExtractedInvoice
    provider: str
    confidence: Optional[float] = None  # 0..1, provider-reported when available
    raw_text: Optional[str] = None  # for debugging the demo
