"""Regenerate the synthetic ANCE-style PKCS#12 test cert.

The original backend/tests/fixtures/fatwara-test.p12 was committed without a
known password and cryptography rejects it as "Invalid password or PKCS12 data".
This script regenerates the .p12 + .pem with an empty password, matching what
the tests expect.

Usage:  docker compose exec backend python /app/../scripts/gen_test_cert.py
   or:  python scripts/gen_test_cert.py    (needs cryptography installed locally)
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

OUT = Path(__file__).parent.parent / "backend" / "tests" / "fixtures"

# 1. Generate RSA private key
print("Generating RSA-2048 key...")
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# 2. Build a self-signed certificate that mimics an ANCE / TunTrust cert
subject = issuer = x509.Name(
    [
        x509.NameAttribute(NameOID.COUNTRY_NAME, "TN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tunis"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Tunis"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Cabinet Test (Synthetic)"),
        x509.NameAttribute(NameOID.COMMON_NAME, "fatwara-test.local"),
    ]
)
now = datetime.now(timezone.utc)
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(now - timedelta(days=1))
    .not_valid_after(now + timedelta(days=730))  # 2 years
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    .add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,  # non-repudiation
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    .sign(key, hashes.SHA256())
)

# 3. Bundle into PKCS#12 with NO password (matches what tests use: "").
#    cryptography's BestAvailableEncryption refuses zero-length passwords,
#    so we use NoEncryption — the .p12 is unencrypted, which is fine for a
#    test fixture and matches the empty-password UX of the upload form.
print("Building PKCS#12 bundle (no password)...")
p12_bytes = pkcs12.serialize_key_and_certificates(
    name=b"fatwara-test",
    key=key,
    cert=cert,
    cas=None,
    encryption_algorithm=serialization.NoEncryption(),
)

# Sanity check the result
key2, cert2, _ = pkcs12.load_key_and_certificates(p12_bytes, b"")
assert key2 is not None and cert2 is not None
print(f"  -> roundtrip OK; cert subject: {cert2.subject.rfc4514_string()}")
print(f"  -> expires: {cert2.not_valid_after_utc.isoformat()}")

# 4. Also write a PEM (cert only — matches what fatwara-test.pem currently is:
#    a cert without the private key, used to test the parser's PEM branch)
pem_bytes = cert.public_bytes(serialization.Encoding.PEM)

# 5. Write both files
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "fatwara-test.p12").write_bytes(p12_bytes)
(OUT / "fatwara-test.pem").write_bytes(pem_bytes)
print(f"\nWrote {OUT / 'fatwara-test.p12'} ({len(p12_bytes)} bytes)")
print(f"Wrote {OUT / 'fatwara-test.pem'} ({len(pem_bytes)} bytes)")
print("\nPassword: <empty>  (use empty string in the upload form)")
