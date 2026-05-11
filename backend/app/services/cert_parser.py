from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import load_pem_x509_certificate
import datetime

def parse_cert(cert_bytes: bytes, password: bytes | None = None) -> dict:
    try:
        _, certificate, _ = pkcs12.load_key_and_certificates(
            cert_bytes, password or b""
        )
        fmt = "pkcs12"
    except Exception:
        certificate = load_pem_x509_certificate(cert_bytes)
        fmt = "pem"

    expiry = certificate.not_valid_after_utc
    now = datetime.datetime.now(datetime.timezone.utc)
    days_left = (expiry - now).days

    if days_left <= 0:
        raise ValueError("Certificate expired — invoices will be unsigned and non-compliant")

    return {
        "format": fmt,
        "subject": certificate.subject.rfc4514_string(),
        "expires_at": expiry,
        "days_until_expiry": days_left,
        "warn": days_left <= 30,
    }