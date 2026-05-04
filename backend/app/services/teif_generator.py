from lxml import etree
from app.core.config import settings
from app.models.invoice import InvoiceCreate, Party, InvoiceLineItem, TaxCategory
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
import os

TEIF_NS = "urn:tn:gov:dgi:teif:1.8"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

NSMAP = {None: TEIF_NS, "xsi": XSI_NS}


def _q(amount: Decimal) -> str:
    return str(amount.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def _sub(parent, tag, text=None, **attribs):
    el = etree.SubElement(parent, f"{{{TEIF_NS}}}{tag}", **attribs)
    if text is not None:
        el.text = str(text)
    return el


def _category_for(item: InvoiceLineItem) -> str:
    if item.tax_category is not None:
        return item.tax_category.value
    return TaxCategory.zero.value if item.tva_rate == 0 else TaxCategory.standard.value


def generate_teif_xml(invoice: InvoiceCreate, invoice_id: str) -> bytes:
    root = etree.Element(f"{{{TEIF_NS}}}Invoice", nsmap=NSMAP)
    root.set(
        f"{{{XSI_NS}}}schemaLocation",
        f"{TEIF_NS} TEIF_v{settings.TEIF_SCHEMA_VERSION}.xsd",
    )

    issue_time = invoice.issue_time or datetime.now(timezone.utc).time().replace(microsecond=0)

    header = _sub(root, "Header")
    _sub(header, "InvoiceID", invoice_id)
    _sub(header, "IssueDate", invoice.invoice_date.isoformat())
    _sub(header, "IssueTime", issue_time.strftime("%H:%M:%S"))
    _sub(header, "InvoiceTypeCode", invoice.invoice_type_code)
    _sub(header, "DocumentCurrencyCode", invoice.currency)
    _sub(header, "TaxCurrencyCode", invoice.currency)
    if invoice.due_date is not None:
        _sub(header, "DueDate", invoice.due_date.isoformat())
    if invoice.note:
        _sub(header, "Note", invoice.note)

    parties = _sub(root, "Parties")
    _build_party(parties, "Supplier", invoice.supplier)
    _build_party(parties, "Customer", invoice.customer)

    lines = _sub(root, "InvoiceLines")
    line_totals: list[Decimal] = []
    tax_buckets: dict[Decimal, Decimal] = {}

    for i, item in enumerate(invoice.items, 1):
        line_ext = item.quantity * item.unit_price
        line_totals.append(line_ext)
        tax_buckets[item.tva_rate] = tax_buckets.get(item.tva_rate, Decimal("0")) + line_ext

        line = _sub(lines, "InvoiceLine")
        _sub(line, "ID", str(i))
        _sub(line, "InvoicedQuantity", str(item.quantity), unitCode="C62")
        _sub(line, "LineExtensionAmount", _q(line_ext), currencyID=invoice.currency)

        item_el = _sub(line, "Item")
        _sub(item_el, "Name", item.description)
        if item.item_code:
            sii = _sub(item_el, "SellersItemIdentification")
            _sub(sii, "ID", item.item_code)
        ctc = _sub(item_el, "ClassifiedTaxCategory")
        _sub(ctc, "ID", _category_for(item))
        _sub(ctc, "Percent", str(item.tva_rate))
        ts = _sub(ctc, "TaxScheme")
        _sub(ts, "ID", "TVA")

        price_el = _sub(line, "Price")
        _sub(price_el, "PriceAmount", _q(item.unit_price), currencyID=invoice.currency)
        _sub(price_el, "BaseQuantity", "1", unitCode="C62")

    total_ht = sum(line_totals, Decimal("0"))
    total_tva = sum(
        (taxable * (rate / Decimal("100")) for rate, taxable in tax_buckets.items()),
        Decimal("0"),
    )
    total_ttc = total_ht + total_tva

    tax_total = _sub(root, "TaxTotal")
    _sub(tax_total, "TaxAmount", _q(total_tva), currencyID=invoice.currency)
    for rate, taxable in tax_buckets.items():
        sub_tax = taxable * (rate / Decimal("100"))
        st = _sub(tax_total, "TaxSubtotal")
        _sub(st, "TaxableAmount", _q(taxable), currencyID=invoice.currency)
        _sub(st, "TaxAmount", _q(sub_tax), currencyID=invoice.currency)
        cat = _sub(st, "TaxCategory")
        _sub(cat, "ID", TaxCategory.zero.value if rate == 0 else TaxCategory.standard.value)
        _sub(cat, "Percent", str(rate))
        ts = _sub(cat, "TaxScheme")
        _sub(ts, "ID", "TVA")

    legal = _sub(root, "LegalMonetaryTotal")
    _sub(legal, "LineExtensionAmount", _q(total_ht), currencyID=invoice.currency)
    _sub(legal, "TaxExclusiveAmount", _q(total_ht), currencyID=invoice.currency)
    _sub(legal, "TaxInclusiveAmount", _q(total_ttc), currencyID=invoice.currency)
    _sub(legal, "PayableAmount", _q(total_ttc), currencyID=invoice.currency)

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def _build_party(parent, role: str, party: Party):
    el = _sub(parent, role)

    pid = _sub(el, "PartyIdentification")
    _sub(pid, "ID", party.matricule, schemeID="TN_MF")

    pname = _sub(el, "PartyName")
    _sub(pname, "Name", party.name)

    addr = party.address
    postal = _sub(el, "PostalAddress")
    _sub(postal, "StreetName", addr.street_name)
    _sub(postal, "CityName", addr.city_name)
    _sub(postal, "PostalZone", addr.postal_zone)
    _sub(postal, "CountrySubentity", addr.country_subentity)
    country = _sub(postal, "Country")
    _sub(country, "IdentificationCode", addr.country_code)

    if role == "Supplier":
        scheme = _sub(el, "TaxScheme")
        _sub(scheme, "ID", "TVA")
        _sub(scheme, "TaxTypeCode", "VAT")


class XSDNotBundledError(RuntimeError):
    pass


def validate_against_xsd(xml_bytes: bytes, *, strict: bool | None = None) -> tuple[bool, list[str]]:
    schema_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "schemas",
        f"teif_{settings.TEIF_SCHEMA_VERSION}.xsd",
    )
    if strict is None:
        strict = bool(getattr(settings, "TEIF_STRICT_VALIDATION", False))

    if not os.path.exists(schema_file):
        if strict:
            raise XSDNotBundledError(
                f"TEIF XSD not found at {schema_file}. "
                "Obtain the official schema from the TTN developer portal and bundle it."
            )
        return False, [f"XSD not bundled at {schema_file} — validation skipped"]

    schema = etree.XMLSchema(etree.parse(schema_file))
    doc = etree.fromstring(xml_bytes)
    valid = schema.validate(doc)
    errors = [str(e) for e in schema.error_log]
    return valid, errors
