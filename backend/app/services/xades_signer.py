from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import load_pem_x509_certificate
from lxml import etree
from signxml import DigestAlgorithm, SignatureMethod
from signxml.xades import XAdESSigner


class SigningError(RuntimeError):
    pass


def _load_key_and_cert(cert_bytes: bytes, password: bytes | None):
    """Returns (private_key, cert_pem_bytes). Raises SigningError on invalid input."""
    try:
        key, cert, _ = pkcs12.load_key_and_certificates(cert_bytes, password or b"")
        if key is None or cert is None:
            raise SigningError(
                "PKCS#12 archive missing private key or certificate"
            )
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        return key, cert_pem
    except SigningError:
        raise
    except Exception:
        # Not PKCS#12 — PEM format requires a separate private key; we don't
        # support PEM-only certs for signing yet (no private key in the bundle).
        try:
            load_pem_x509_certificate(cert_bytes)
        except Exception as exc:
            raise SigningError(f"Unrecognized certificate format: {exc}") from exc
        raise SigningError(
            "PEM certificates without private key cannot be used to sign. "
            "Upload a PKCS#12 (.p12) bundle that contains both the key and cert."
        )


def sign_xml(
    xml_bytes: bytes,
    cert_bytes: bytes,
    cert_password: bytes | None = None,
) -> bytes:
    """Sign TEIF XML with XAdES-B-B (enveloped, RSA-SHA256, exclusive C14N).

    Returns the signed XML bytes. Raises SigningError with a clean message on
    any failure (cert parse, key missing, signature error).
    """
    try:
        key, cert_pem = _load_key_and_cert(cert_bytes, cert_password)
    except SigningError:
        raise
    except Exception as exc:
        raise SigningError(f"Failed to load signing material: {exc}") from exc

    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    try:
        doc = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as exc:
        raise SigningError(f"Invalid XML payload: {exc}") from exc

    try:
        signer = XAdESSigner(
            signature_algorithm=SignatureMethod.RSA_SHA256,
            digest_algorithm=DigestAlgorithm.SHA256,
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
        )
        signed = signer.sign(doc, key=key_pem, cert=cert_pem)
    except Exception as exc:
        raise SigningError(f"XAdES signing failed: {exc}") from exc

    return etree.tostring(signed, xml_declaration=True, encoding="UTF-8")
