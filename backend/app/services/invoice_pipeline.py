"""Background pipeline: load cert → sign TEIF → submit to TTN → update status.

Invoked by FastAPI BackgroundTasks after POST /invoices stores the queued row.
Owns its own DB session because the request session is closed by the time the
background task runs.
"""

import logging
import uuid

from app.core.database import SessionLocal
from app.repositories.audit_repo import AuditRepo
from app.repositories.cert_repo import CertRepo
from app.repositories.invoice_repo import InvoiceRepo
from app.services.storage import StorageError, download_cert
from app.services.ttn_client import TTNError, TTNTimeout, get_ttn_client
from app.services.xades_signer import SigningError, sign_xml

log = logging.getLogger(__name__)


async def run_pipeline(invoice_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Drive a queued invoice through sign + submit. Always terminates the row
    in a final state (accepted / rejected / error) or leaves it queued only if
    the very first DB read fails."""

    async with SessionLocal() as session:
        invoice_repo = InvoiceRepo(session)
        cert_repo = CertRepo(session)
        audit = AuditRepo(session)

        invoice = await invoice_repo.get_by_id(invoice_id)
        if invoice is None:
            log.error("pipeline: invoice %s not found", invoice_id)
            return

        cert = await cert_repo.get_by_user(user_id)
        if cert is None:
            await invoice_repo.update_status(invoice_id, "error")
            await audit.log(
                user_id=user_id,
                action="pipeline.error",
                invoice_id=invoice_id,
                detail={"reason": "no_cert_on_file"},
            )
            return

        try:
            cert_bytes = download_cert(cert.storage_path)
        except StorageError as exc:
            await invoice_repo.update_status(invoice_id, "error")
            await audit.log(
                user_id=user_id,
                action="pipeline.error",
                invoice_id=invoice_id,
                detail={"reason": "cert_download_failed", "error": str(exc)},
            )
            return

        try:
            signed = sign_xml(invoice.teif_xml, cert_bytes)
        except SigningError as exc:
            await invoice_repo.update_status(invoice_id, "error")
            await audit.log(
                user_id=user_id,
                action="pipeline.error",
                invoice_id=invoice_id,
                detail={"reason": "signing_failed", "error": str(exc)},
            )
            return

        await invoice_repo.update_status(
            invoice_id, "submitted", signed_xml=signed
        )
        await audit.log(
            user_id=user_id,
            action="pipeline.signed",
            invoice_id=invoice_id,
        )

        client = get_ttn_client()
        try:
            result = await client.submit(signed)
        except TTNTimeout as exc:
            await invoice_repo.update_status(invoice_id, "error")
            await audit.log(
                user_id=user_id,
                action="pipeline.error",
                invoice_id=invoice_id,
                detail={"reason": "ttn_timeout", "error": str(exc)},
            )
            return
        except (TTNError, NotImplementedError) as exc:
            await invoice_repo.update_status(invoice_id, "error")
            await audit.log(
                user_id=user_id,
                action="pipeline.error",
                invoice_id=invoice_id,
                detail={"reason": "ttn_error", "error": str(exc)},
            )
            return

        await invoice_repo.update_status(
            invoice_id, result.status, ttn_reference=result.reference
        )
        await audit.log(
            user_id=user_id,
            action=f"pipeline.{result.status}",
            invoice_id=invoice_id,
            detail={"reference": result.reference, "message": result.message},
        )
