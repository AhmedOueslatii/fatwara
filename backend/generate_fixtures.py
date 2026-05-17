import datetime
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12 as pkcs12_ser
from cryptography.x509.oid import NameOID

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
cert = (
    x509.CertificateBuilder()
    .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "fatwara-test")]))
    .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "fatwara-test")]))
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
    .sign(key, hashes.SHA256())
)

p12_bytes = pkcs12_ser.serialize_key_and_certificates(
    name=b"fatwara-test",
    key=key,
    cert=cert,
    cas=None,
    encryption_algorithm=serialization.NoEncryption(),
)
Path("tests/fixtures").mkdir(parents=True, exist_ok=True)
Path("tests/fixtures/fatwara-test.p12").write_bytes(p12_bytes)

pem_bytes = cert.public_bytes(serialization.Encoding.PEM)
Path("tests/fixtures/fatwara-test.pem").write_bytes(pem_bytes)

print("Done!")
print("tests/fixtures/fatwara-test.p12")
print("tests/fixtures/fatwara-test.pem")