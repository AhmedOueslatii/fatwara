from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "schema_version": settings.TEIF_SCHEMA_VERSION,
        "ttn_sandbox": settings.TTN_SANDBOX,
    }

@router.get("/schema-version")
def schema_version():
    return {"version": settings.TEIF_SCHEMA_VERSION}