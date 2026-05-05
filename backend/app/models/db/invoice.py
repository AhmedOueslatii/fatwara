import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    String,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    LargeBinary,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.db.base import Base


VALID_STATUSES = (
    "draft",
    "queued",
    "submitted",
    "accepted",
    "rejected",
    "error",
    "cancelled",
)


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint(
            "status IN ("
            + ", ".join(f"'{s}'" for s in VALID_STATUSES)
            + ")",
            name="invoices_status_valid",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="draft", server_default="draft"
    )

    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="TND")

    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_matricule: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_matricule: Mapped[str] = mapped_column(String(64), nullable=False)

    total_ht: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    total_tva: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    total_ttc: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)

    teif_xml: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    signed_xml: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    ttn_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )
