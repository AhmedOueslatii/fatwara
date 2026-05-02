from lxml import etree
from app.core.config import settings
from app.models.invoice import InvoiceCreate
from decimal import Decimal
import os

UBL_INV = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

NSMAP = {
    None: UBL_INV,
    "cbc": CBC,
    "cac": CAC,
}

def _sub(parent, ns, tag, text=None, **attribs):
    el = etree.SubElement(parent, f"{{{ns}}}{tag}", **attribs)
    if text is not None:
        el.text = str(text)
    return el

def generate_teif_xml(invoice: InvoiceCreate, invoice_id: str) -> bytes:
    root = etree.Element(f"{{{UBL_INV}}}Invoice", nsmap=NSMAP)

    _sub(root, CBC, "UBLVersionID", "2.1")
    _sub(root, CBC, "CustomizationID", "urn:www.cenbii.eu:transaction:biitrns010:ver2.0")
    _sub(root, CBC, "ID", invoice_id)
    _sub(root, CBC, "IssueDate", invoice.invoice_date.isoformat())
    _sub(root, CBC, "InvoiceTypeCode", "380")  # 380 = commercial invoice
    _sub(root, CBC, "DocumentCurrencyCode", invoice.currency)

    # Supplier
    supplier_party = _sub(root, CAC, "AccountingSupplierParty")
    party = _sub(supplier_party, CAC, "Party")
    party_name = _sub(party, CAC, "PartyName")
    _sub(party_name, CBC, "Name", invoice.supplier_name)
    postal = _sub(party, CAC, "PostalAddress")
    _sub(postal, CBC, "StreetName", invoice.supplier_address)
    _sub(postal, CBC, "CountrySubentity", "TN")
    country = _sub(postal, CAC, "Country")
    _sub(country, CBC, "IdentificationCode", "TN")
    tax_scheme_el = _sub(party, CAC, "PartyTaxScheme")
    _sub(tax_scheme_el, CBC, "CompanyID", invoice.supplier_matricule)
    scheme = _sub(tax_scheme_el, CAC, "TaxScheme")
    _sub(scheme, CBC, "ID", "VAT")

    # Buyer
    buyer_party = _sub(root, CAC, "AccountingCustomerParty")
    bparty = _sub(buyer_party, CAC, "Party")
    bparty_name = _sub(bparty, CAC, "PartyName")
    _sub(bparty_name, CBC, "Name", invoice.buyer_name)
    btax = _sub(bparty, CAC, "PartyTaxScheme")
    _sub(btax, CBC, "CompanyID", invoice.buyer_matricule)
    bscheme = _sub(btax, CAC, "TaxScheme")
    _sub(bscheme, CBC, "ID", "VAT")

    # Totals
    total_ht = sum(item.quantity * item.unit_price for item in invoice.items)
    total_tva = sum(
        item.quantity * item.unit_price * (item.tva_rate / Decimal("100"))
        for item in invoice.items
    )
    total_ttc = total_ht + total_tva

    tax_total = _sub(root, CAC, "TaxTotal")
    _sub(tax_total, CBC, "TaxAmount", str(round(total_tva, 3)), currencyID=invoice.currency)

    legal = _sub(root, CAC, "LegalMonetaryTotal")
    _sub(legal, CBC, "LineExtensionAmount", str(round(total_ht, 3)), currencyID=invoice.currency)
    _sub(legal, CBC, "TaxExclusiveAmount", str(round(total_ht, 3)), currencyID=invoice.currency)
    _sub(legal, CBC, "TaxInclusiveAmount", str(round(total_ttc, 3)), currencyID=invoice.currency)
    _sub(legal, CBC, "PayableAmount", str(round(total_ttc, 3)), currencyID=invoice.currency)

    # Line items
    for i, item in enumerate(invoice.items, 1):
        line = _sub(root, CAC, "InvoiceLine")
        _sub(line, CBC, "ID", str(i))
        _sub(line, CBC, "InvoicedQuantity", str(item.quantity), unitCode="C62")
        line_ext = item.quantity * item.unit_price
        _sub(line, CBC, "LineExtensionAmount", str(round(line_ext, 3)), currencyID=invoice.currency)
        item_el = _sub(line, CAC, "Item")
        _sub(item_el, CBC, "Description", item.description)
        tax_cat = _sub(item_el, CAC, "ClassifiedTaxCategory")
        _sub(tax_cat, CBC, "Percent", str(item.tva_rate))
        ts = _sub(tax_cat, CAC, "TaxScheme")
        _sub(ts, CBC, "ID", "VAT")
        price_el = _sub(line, CAC, "Price")
        _sub(price_el, CBC, "PriceAmount", str(item.unit_price), currencyID=invoice.currency)

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

def validate_against_xsd(xml_bytes: bytes) -> tuple[bool, list[str]]:
    schema_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "schemas",
        f"teif_{settings.TEIF_SCHEMA_VERSION}.xsd"
    )
    if not os.path.exists(schema_file):
        return True, []  # schema not bundled yet — skip in dev
    schema_doc = etree.parse(schema_file)
    schema = etree.XMLSchema(schema_doc)
    doc = etree.fromstring(xml_bytes)
    valid = schema.validate(doc)
    errors = [str(e) for e in schema.error_log]
    return valid, errors