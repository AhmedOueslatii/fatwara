from pathlib import Path

import pytest
from lxml import etree

from app.services.xades_signer import SigningError, sign_xml

FIXTURES = Path(__file__).parent / "fixtures"
P12_PATH = FIXTURES / "fatwara-test.p12"
PEM_PATH = FIXTURES / "fatwara-test.pem"

DSIG_NS = "http://www.w3.org/2000/09/xmldsig#"

SAMPLE_XML = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<Invoice xmlns="urn:tn:gov:dgi:teif:1.8">'
    b"<Header><InvoiceID>test-001</InvoiceID></Header>"
    b"</Invoice>"
)


def test_sign_xml_with_p12_appends_signature_element():
    """POC stub: real XAdES is deferred. We still expect a <Signature> element
    to be appended so callers can distinguish signed from unsigned bytes."""
    cert_bytes = P12_PATH.read_bytes()
    signed = sign_xml(SAMPLE_XML, cert_bytes)

    doc = etree.fromstring(signed)
    sig = doc.find(f".//{{{DSIG_NS}}}Signature")
    assert sig is not None, "no <Signature> element in signed XML"


def test_sign_xml_rejects_pem_without_key():
    cert_bytes = PEM_PATH.read_bytes()
    with pytest.raises(SigningError, match="PEM certificates without private key"):
        sign_xml(SAMPLE_XML, cert_bytes)


def test_sign_xml_rejects_garbage_cert():
    with pytest.raises(SigningError):
        sign_xml(SAMPLE_XML, b"not a cert")


def test_sign_xml_rejects_invalid_xml():
    cert_bytes = P12_PATH.read_bytes()
    with pytest.raises(SigningError, match="Invalid XML"):
        sign_xml(b"<not-well-formed", cert_bytes)
