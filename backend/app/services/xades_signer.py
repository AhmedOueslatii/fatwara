"""TEIF XAdES-B-B signer.

POC STUB: real XAdES signing is deferred. signxml 3.x pulls in a pyopenssl
version that conflicts with the modern cryptography stack on CI, and signxml
4.x is a major rework that needs proper integration work. Until that lands,
this module:

  - validates that the cert material is parseable (PKCS#12 with key + cert),
  - validates that the XML is well-formed,
  - appends a placeholder <Signature> marker so downstream code can tell
    signed from unsigned bytes,
  - raises SigningError on the same failure modes the real signer will.

The TTN mock accepts any bytes, so this is enough to drive the pipeline
end-to-end. Replace _stub_sign() with the real implementation when we
move signxml in.
"""

from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import load_pem_x509_certificate
from lxml import etree


class SigningError(RuntimeError):
    pass


def _validate_signing_material(cert_bytes: bytes, password: bytes | None) -> None:
    try:
        key, cert, _ = pkcs12.load_key_and_certificates(cert_bytes, password or b"")
        if key is None or cert is None:
            raise SigningError(
                "PKCS#12 archive missing private key or certificate"
            )
        return
    except SigningError:
        raise
    except Exception:
        pass

    try:
        load_pem_x509_certificate(cert_bytes)
    except Exception as exc:
        raise SigningError(f"Unrecognized certificate format: {exc}") from exc
    raise SigningError(
        "PEM certificates without private key cannot be used to sign. "
        "Upload a PKCS#12 (.p12) bundle that contains both the key and cert."
    )


def _stub_sign(xml_bytes: bytes) -> bytes:
    """Append a placeholder Signature element so signed != unsigned at the
    byte level. Real XAdES signing will replace this entirely."""
    try:
        doc = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as exc:
        raise SigningError(f"Invalid XML payload: {exc}") from exc

    marker = etree.SubElement(
        doc, "{http://www.w3.org/2000/09/xmldsig#}Signature"
    )
    marker.set("stub", "true")
    note = etree.SubElement(marker, "Note")
    note.text = "POC stub — real XAdES-B signing not yet implemented"

    return etree.tostring(doc, xml_declaration=True, encoding="UTF-8")


def sign_xml(
    xml_bytes: bytes,
    cert_bytes: bytes,
    cert_password: bytes | None = None,
) -> bytes:
    """Sign TEIF XML (POC stub — see module docstring).

    Returns the "signed" XML bytes. Raises SigningError on cert parse failure,
    missing key, or invalid XML.
    """
    _validate_signing_material(cert_bytes, cert_password)
    return _stub_sign(xml_bytes)
