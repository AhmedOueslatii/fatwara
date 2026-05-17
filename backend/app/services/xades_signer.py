"""XAdES-B signing — POC stub.

signxml 3.x pulls a broken pyopenssl (`OpenSSL.crypto.verify` is gone); signxml
4.x is a major API rework. Until the real signer lands (its own PR), this
module validates the cert material so cert errors stay realistic, then appends
a `<Signature stub="true">` marker. Mock TTN accepts any bytes, so the rest of
the pipeline still runs end-to-end.

Swap site for real XAdES-B: replace `_stub_sign()` with a signxml 4.x (or
xmlsec) call. The cert-loading logic above it is already production-shaped.
"""

from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import load_pem_x509_certificate
from lxml import etree


XADES_NS = "http://uri.etsi.org/01903/v1.3.2#"
DS_NS = "http://www.w3.org/2000/09/xmldsig#"


class SigningError(RuntimeError):
    pass


def _load_key_and_cert(cert_bytes: bytes, password: bytes | None):
    try:
        key, cert, _ = pkcs12.load_key_and_certificates(cert_bytes, password or b"")
        if key is None or cert is None:
            raise SigningError(
                "PKCS#12 archive missing private key or certificate"
            )
        return key, cert
    except SigningError:
        raise
    except Exception:
        try:
            load_pem_x509_certificate(cert_bytes)
        except Exception as exc:
            raise SigningError(f"Unrecognized certificate format: {exc}") from exc
        raise SigningError(
            "PEM certificates without private key cannot be used to sign. "
            "Upload a PKCS#12 (.p12) bundle that contains both the key and cert."
        )


def _stub_sign(doc: etree._Element) -> etree._Element:
    sig = etree.SubElement(
        doc,
        f"{{{DS_NS}}}Signature",
        attrib={"stub": "true"},
        nsmap={"ds": DS_NS, "xades": XADES_NS},
    )
    etree.SubElement(sig, f"{{{DS_NS}}}SignedInfo")
    etree.SubElement(sig, f"{{{DS_NS}}}SignatureValue").text = "STUB"
    return doc


def sign_xml(
    xml_bytes: bytes,
    cert_bytes: bytes,
    cert_password: bytes | None = None,
) -> bytes:
    try:
        _load_key_and_cert(cert_bytes, cert_password)
    except SigningError:
        raise
    except Exception as exc:
        raise SigningError(f"Failed to load signing material: {exc}") from exc

    try:
        doc = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as exc:
        raise SigningError(f"Invalid XML payload: {exc}") from exc

    signed = _stub_sign(doc)
    return etree.tostring(signed, xml_declaration=True, encoding="UTF-8")
