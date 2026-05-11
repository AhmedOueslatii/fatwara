from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.core.database import get_session
from app.models.db.user import User
from app.models.invoice import OnboardingStatus
from app.repositories.cert_repo import CertRepo
from app.services.cert_parser import parse_cert
from app.services.storage import StorageError, upload_cert

router = APIRouter()


@router.post("/cert/upload")
async def cert_upload(
    file: UploadFile = File(...),
    password: str = Form(default=""),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    cert_bytes = await file.read()
    try:
        meta = parse_cert(
            cert_bytes,
            password.encode() if password else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not parse certificate. Supported formats: PKCS#12, PEM",
        )

    try:
        storage_path = upload_cert(user.id, cert_bytes, meta["format"])
    except StorageError as exc:
        raise HTTPException(status_code=503, detail=f"Cert storage unavailable: {exc}")

    repo = CertRepo(session)
    cert = await repo.upsert(
        user_id=user.id,
        storage_path=storage_path,
        fmt=meta["format"],
        expires_at=meta["expires_at"],
    )

    return {
        "cert_id": str(cert.id),
        "format": cert.format,
        "expires_at": cert.expires_at.isoformat(),
        "days_until_expiry": meta["days_until_expiry"],
        "warn": meta["warn"],
    }


@router.post("/ttn/credentials")
def save_ttn_credentials(client_id: str, client_secret: str):
    return {"ttn_connected": True, "sandbox_mode": True}


@router.get("/status", response_model=OnboardingStatus)
async def onboarding_status(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    from datetime import datetime, timezone

    repo = CertRepo(session)
    cert = await repo.get_by_user(user.id)

    if cert is None:
        return OnboardingStatus(cert_ok=False, ttn_ok=False, ready_to_invoice=False)

    now = datetime.now(timezone.utc)
    days_remaining = (cert.expires_at - now).days
    cert_ok = days_remaining > 0

    return OnboardingStatus(
        cert_ok=cert_ok,
        ttn_ok=False,
        ready_to_invoice=cert_ok,
        cert_expires_at=cert.expires_at.isoformat(),
        cert_days_remaining=days_remaining,
    )
