from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.cert_parser import parse_cert
from app.models.invoice import OnboardingStatus

router = APIRouter()

@router.post("/cert/upload")
async def upload_cert(
    file: UploadFile = File(...),
    password: str = Form(default="")
):
    cert_bytes = await file.read()
    try:
        meta = parse_cert(
            cert_bytes,
            password.encode() if password else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse certificate. Supported formats: PKCS#12, PEM")

    return {
        "cert_id": "local-dev",
        "format": meta["format"],
        "expires_at": meta["expires_at"],
        "days_until_expiry": meta["days_until_expiry"],
        "warn": meta["warn"],
    }

@router.post("/ttn/credentials")
def save_ttn_credentials(client_id: str, client_secret: str):
    # In production: encrypt + store in Supabase
    return {"ttn_connected": True, "sandbox_mode": True}

@router.get("/status", response_model=OnboardingStatus)
def onboarding_status():
    return OnboardingStatus(
        cert_ok=False,
        ttn_ok=False,
        ready_to_invoice=False,
    )