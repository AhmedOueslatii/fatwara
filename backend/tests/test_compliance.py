import os
import sys
from datetime import date, time
from decimal import Decimal

from lxml import etree

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.invoice import (
    Address,
    InvoiceCreate,
    InvoiceLineItem,
    Party,
    TaxCategory,
)
from app.services.teif_generator import (
    TEIF_NS,
    generate_teif_xml,
    validate_against_xsd,
)


TEIF = f"{{{TEIF_NS}}}"


def _addr(street, city, zone, sub):
    return Address(
        street_name=street,
        city_name=city,
        postal_zone=zone,
        country_subentity=sub,
    )


def make_minimal_invoice():
    """A small invoice mixing zero-rated and standard-rated lines."""
    return InvoiceCreate(
        supplier=Party(
            name="Cabinet Dr. Ben Ali",
            matricule="1234567A/P/M/000",
            address=_addr("12 Rue de la Liberte", "Tunis", "1000", "Tunis"),
        ),
        customer=Party(
            name="Societe ABC",
            matricule="9876543B/P/M/000",
            address=_addr("45 Rue de Marseille", "Sfax", "3000", "Sfax"),
        ),
        invoice_date=date(2026, 5, 4),
        items=[
            InvoiceLineItem(
                description="Consultation medicale",
                quantity=Decimal("1"),
                unit_price=Decimal("150.000"),
                tva_rate=Decimal("0"),
            ),
            InvoiceLineItem(
                description="Analyses biologiques",
                quantity=Decimal("3"),
                unit_price=Decimal("45.000"),
                tva_rate=Decimal("19"),
            ),
        ],
    )


def make_noqta_example_invoice():
    """Reproduces the complete TEIF example from the Noqta tutorial.

    Reference: backend/schemas/TEIF_1.8.7_REFERENCE.md (Complete Example section).
    Lines: 20h dev front-end @ 50 TND + 10h API @ 40 TND = 1400 HT, 19% TVA = 266, TTC 1666.
    """
    return InvoiceCreate(
        supplier=Party(
            name="Tech Solutions SARL",
            matricule="12345678A000000",
            address=_addr("12 Rue des Entrepreneurs", "Tunis", "1002", "Tunis"),
        ),
        customer=Party(
            name="Client Entreprise SA",
            matricule="98765432B000111",
            address=_addr("45 Avenue de la Republique", "Sfax", "3000", "Sfax"),
        ),
        invoice_date=date(2026, 2, 22),
        issue_time=time(14, 30, 0),
        due_date=date(2026, 3, 22),
        note="Facture pour services de developpement web",
        items=[
            InvoiceLineItem(
                description="Developpement front-end React",
                quantity=Decimal("20"),
                unit_price=Decimal("50.000"),
                tva_rate=Decimal("19"),
            ),
            InvoiceLineItem(
                description="Integration API et tests",
                quantity=Decimal("10"),
                unit_price=Decimal("40.000"),
                tva_rate=Decimal("19"),
            ),
        ],
    )


def _parse(xml_bytes):
    return etree.fromstring(xml_bytes)


def test_namespace_is_teif_not_ubl():
    """Regression: earlier scaffold emitted UBL namespaces by mistake."""
    xml = generate_teif_xml(make_minimal_invoice(), "TEST-001")
    root = _parse(xml)
    assert root.tag == f"{TEIF}Invoice"
    assert TEIF_NS == "urn:tn:gov:dgi:teif:1.8"


def test_header_structure():
    inv = make_noqta_example_invoice()
    xml = generate_teif_xml(inv, "FAC-2026-001234")
    root = _parse(xml)
    header = root.find(f"{TEIF}Header")
    assert header is not None

    assert header.findtext(f"{TEIF}InvoiceID") == "FAC-2026-001234"
    assert header.findtext(f"{TEIF}IssueDate") == "2026-02-22"
    assert header.findtext(f"{TEIF}IssueTime") == "14:30:00"
    assert header.findtext(f"{TEIF}InvoiceTypeCode") == "380"
    assert header.findtext(f"{TEIF}DocumentCurrencyCode") == "TND"
    assert header.findtext(f"{TEIF}TaxCurrencyCode") == "TND"
    assert header.findtext(f"{TEIF}DueDate") == "2026-03-22"


def test_supplier_matricule_carries_tn_mf_scheme_id():
    xml = generate_teif_xml(make_noqta_example_invoice(), "FAC-2026-001234")
    root = _parse(xml)
    supplier = root.find(f"{TEIF}Parties/{TEIF}Supplier")
    pid = supplier.find(f"{TEIF}PartyIdentification/{TEIF}ID")
    assert pid.get("schemeID") == "TN_MF"
    assert pid.text == "12345678A000000"


def test_customer_address_is_structured():
    xml = generate_teif_xml(make_noqta_example_invoice(), "FAC-2026-001234")
    root = _parse(xml)
    addr = root.find(f"{TEIF}Parties/{TEIF}Customer/{TEIF}PostalAddress")
    assert addr.findtext(f"{TEIF}StreetName") == "45 Avenue de la Republique"
    assert addr.findtext(f"{TEIF}CityName") == "Sfax"
    assert addr.findtext(f"{TEIF}PostalZone") == "3000"
    assert addr.findtext(f"{TEIF}Country/{TEIF}IdentificationCode") == "TN"


def test_totals_match_noqta_example():
    """1400 HT, 266 TVA, 1666 TTC — straight from the Noqta example."""
    xml = generate_teif_xml(make_noqta_example_invoice(), "FAC-2026-001234")
    root = _parse(xml)
    legal = root.find(f"{TEIF}LegalMonetaryTotal")
    assert legal.findtext(f"{TEIF}LineExtensionAmount") == "1400.000"
    assert legal.findtext(f"{TEIF}TaxExclusiveAmount") == "1400.000"
    assert legal.findtext(f"{TEIF}TaxInclusiveAmount") == "1666.000"
    assert legal.findtext(f"{TEIF}PayableAmount") == "1666.000"


def test_tax_subtotal_aggregates_per_rate():
    xml = generate_teif_xml(make_minimal_invoice(), "TEST-002")
    root = _parse(xml)
    subtotals = root.findall(f"{TEIF}TaxTotal/{TEIF}TaxSubtotal")
    by_rate = {st.findtext(f"{TEIF}TaxCategory/{TEIF}Percent"): st for st in subtotals}
    assert "0" in by_rate and "19" in by_rate

    zero = by_rate["0"]
    assert zero.findtext(f"{TEIF}TaxableAmount") == "150.000"
    assert zero.findtext(f"{TEIF}TaxAmount") == "0.000"
    assert zero.findtext(f"{TEIF}TaxCategory/{TEIF}ID") == TaxCategory.zero.value

    standard = by_rate["19"]
    assert standard.findtext(f"{TEIF}TaxableAmount") == "135.000"
    assert standard.findtext(f"{TEIF}TaxAmount") == "25.650"
    assert standard.findtext(f"{TEIF}TaxCategory/{TEIF}ID") == TaxCategory.standard.value


def test_amounts_use_three_decimals():
    xml = generate_teif_xml(make_minimal_invoice(), "TEST-003")
    root = _parse(xml)
    payable = root.findtext(f"{TEIF}LegalMonetaryTotal/{TEIF}PayableAmount")
    # 150 + (3*45) + (3*45*0.19) = 285 + 25.65 = 310.65 -> 310.650
    assert payable == "310.650"
    assert payable.split(".")[1] == "650"


def test_xsd_validation_reports_missing_schema_loudly():
    """Regression: previously returned (True, []) when XSD was absent — silent pass."""
    xml = generate_teif_xml(make_minimal_invoice(), "TEST-004")
    valid, errors = validate_against_xsd(xml)
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "schemas", "teif_1.8.7.xsd"
    )
    if os.path.exists(schema_path):
        # If the official XSD has been bundled, the test invoice should validate.
        # If this fails, the generator output diverges from the real schema.
        assert valid, f"XSD validation failed: {errors}"
    else:
        assert not valid
        assert any("not bundled" in e.lower() for e in errors)
