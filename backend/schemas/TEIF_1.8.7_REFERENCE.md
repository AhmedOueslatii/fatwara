# TEIF 1.8.7 — Working Reference

> **Source:** Distilled from Noqta's tutorial — https://noqta.tn/en/tutorials/format-teif-specifications-techniques-tunisie-2026
>
> **Status:** Secondary source. Noqta is a Tunisian invoicing fintech, so this is credible for shape and naming, but it is **not** the official DGI/TTN specification. The authoritative XSD (`teif_1.8.7.xsd`) is still missing from this repo and must be obtained from the TTN developer portal before the POC can claim full compliance. Until the XSD is bundled, `validate_against_xsd` silently passes — see `app/services/teif_generator.py`.

## Top-level structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:tn:gov:dgi:teif:1.8"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="urn:tn:gov:dgi:teif:1.8 TEIF_v1.8.7.xsd">

  <Header>...</Header>
  <Parties>
    <Supplier>...</Supplier>
    <Customer>...</Customer>
  </Parties>
  <InvoiceLines>
    <InvoiceLine>...</InvoiceLine>
  </InvoiceLines>
  <TaxTotal>...</TaxTotal>
  <LegalMonetaryTotal>...</LegalMonetaryTotal>
  <Signature>...</Signature>                    <!-- added by signer -->
  <VisibleElectronicSeal>...</VisibleElectronicSeal>  <!-- QR code, after signing -->
</Invoice>
```

Field levels in the schema: **M** (mandatory), **C** (conditional), **O** (optional).

## Header — mandatory fields

| Field                  | Type             | Example              |
| ---------------------- | ---------------- | -------------------- |
| `InvoiceID`            | string ≤ 50      | `FAC-2026-001234`    |
| `IssueDate`            | YYYY-MM-DD       | `2026-02-22`         |
| `IssueTime`            | HH:MM:SS         | `14:30:00`           |
| `InvoiceTypeCode`      | 3 digits         | `380`                |
| `DocumentCurrencyCode` | ISO 4217         | `TND`                |
| `DueDate`              | date (mandatory) | `2026-03-22`         |

### Document type codes
| Code | Type |
| ---- | ---- |
| 380  | Standard commercial invoice |
| 381  | Credit note (avoir) |
| 383  | Debit note |
| 386  | Prepayment / advance invoice |
| 389  | Self-billing |

## Parties

```xml
<Supplier>
  <PartyIdentification>
    <ID schemeID="TN_MF">12345678A000000</ID>   <!-- matricule fiscal, schemeID="TN_MF" mandatory -->
  </PartyIdentification>
  <PartyName><Name>Société Exemple SARL</Name></PartyName>
  <PostalAddress>
    <StreetName>Avenue Habib Bourguiba</StreetName>
    <CityName>Tunis</CityName>
    <PostalZone>1000</PostalZone>
    <CountrySubentity>Tunis</CountrySubentity>
    <Country><IdentificationCode>TN</IdentificationCode></Country>
  </PostalAddress>
  <TaxScheme>
    <ID>TVA</ID>
    <TaxTypeCode>VAT</TaxTypeCode>
  </TaxScheme>
</Supplier>
```

Rules: `schemeID="TN_MF"` is mandatory; address must match the DGI registration; country code `TN`.

## InvoiceLine

```xml
<InvoiceLine>
  <ID>1</ID>
  <InvoicedQuantity unitCode="C62">10</InvoicedQuantity>
  <LineExtensionAmount currencyID="TND">500.000</LineExtensionAmount>
  <Item>
    <Name>Prestation de développement web</Name>
    <SellersItemIdentification><ID>PROD-001</ID></SellersItemIdentification>
    <ClassifiedTaxCategory>
      <ID>S</ID>            <!-- S=Standard, Z=Zero, E=Exempt -->
      <Percent>19</Percent>
      <TaxScheme><ID>TVA</ID></TaxScheme>
    </ClassifiedTaxCategory>
  </Item>
  <Price>
    <PriceAmount currencyID="TND">50.000</PriceAmount>
    <BaseQuantity unitCode="C62">1</BaseQuantity>
  </Price>
</InvoiceLine>
```

Unit codes (UN/ECE Recommendation 20): `C62` = piece, `HUR` = hour.

### VAT rates (Tunisia)
| Code | Rate | Use |
| ---- | ---- | --- |
| S    | 19%  | General |
| S    | 13%  | Financial services, insurance |
| S    | 7%   | Basic foodstuffs, medicines |
| Z    | 0%   | Exports, exempt products |
| E    | —    | Specific legal exemptions |

## Totals

```xml
<TaxTotal>
  <TaxAmount currencyID="TND">266.000</TaxAmount>
  <TaxSubtotal>
    <TaxableAmount currencyID="TND">1400.000</TaxableAmount>
    <TaxAmount currencyID="TND">266.000</TaxAmount>
    <TaxCategory>
      <ID>S</ID>
      <Percent>19</Percent>
      <TaxScheme><ID>TVA</ID></TaxScheme>
    </TaxCategory>
  </TaxSubtotal>
</TaxTotal>

<LegalMonetaryTotal>
  <LineExtensionAmount currencyID="TND">1400.000</LineExtensionAmount>
  <TaxExclusiveAmount currencyID="TND">1400.000</TaxExclusiveAmount>
  <TaxInclusiveAmount currencyID="TND">1666.000</TaxInclusiveAmount>
  <PayableAmount currencyID="TND">1666.000</PayableAmount>
</LegalMonetaryTotal>
```

**Format rules:** all amounts are 3-decimal (`1400.000`), Tunisian dinar convention.

## Digital signature

W3C XMLDSig, **enveloped**, **RSA-SHA256**, canonicalization **C14N**.

Process:
1. Generate the invoice XML without `<Signature>`.
2. Canonicalize (C14N: `http://www.w3.org/TR/2001/REC-xml-c14n-20010315`).
3. SHA-256 the canonical bytes.
4. RSA-sign the digest with the TUNTRUST/ANCE cert's private key → `SignatureValue`.
5. Embed the `<Signature>` block (with `<X509Certificate>` of the signer) inside `<Invoice>`.

```xml
<Signature Id="TEIF-SIG-001">
  <SignedInfo>
    <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
    <SignatureMethod      Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
    <Reference URI="">
      <Transforms>
        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
      </Transforms>
      <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
      <DigestValue>...</DigestValue>
    </Reference>
  </SignedInfo>
  <SignatureValue>...base64...</SignatureValue>
  <KeyInfo><X509Data><X509Certificate>...base64...</X509Certificate></X509Data></KeyInfo>
</Signature>
```

Library to use: `signxml`. Any mutation after signing invalidates the signature → re-sign required.

## Visible Electronic Seal (QR code, "CEV")

QR encodes a verification URL on `verify.elfatoora.tn` with parameters:

| Param | Description |
| ----- | ----------- |
| `iid` | Unique TTN invoice identifier (hash) |
| `sid` | Supplier matricule fiscal |
| `dt`  | Issue date+time (compact format `YYYYMMDDHHMMSS`) |
| `amt` | Total TTC |
| `sig` | Truncated control hash |

Example: `https://verify.elfatoora.tn/v?iid=a3f7e2b1c9d4&sid=12345678A000000&dt=20260222143000&amt=619.000&sig=f4e2a1b3`

```xml
<VisibleElectronicSeal>
  <QRCode format="QR_CODE" version="2">...base64-encoded URL...</QRCode>
  <SealDescription>Facture électronique certifiée TTN</SealDescription>
  <SealDate>2026-02-22T14:30:00</SealDate>
</VisibleElectronicSeal>
```

QR is generated **after** signing because it references the signed invoice's hash.

## Integration modes

- **Web mode:** humans use `elfatoora.tn` portal; no API integration, no automation. Out of scope for Fatwara.
- **EDI mode (API):** what we are building.

## TTN API (EDI mode)

| Endpoint | Method | Purpose |
| -------- | ------ | ------- |
| `/api/v1/auth/token`            | POST | OAuth2 access token |
| `/api/v1/invoices`              | POST | Submit signed invoice |
| `/api/v1/invoices/{id}`         | GET  | Status |
| `/api/v1/invoices/{id}/ack`     | GET  | Acknowledgement |
| `/api/v1/invoices/{id}/pdf`     | GET  | PDF |
| `/api/v1/invoices/search`       | GET  | Search |

**Bases:**
- Sandbox: `https://api-sandbox.elfatoora.tn`
- Production: `https://api.elfatoora.tn`

## Lifecycle

```
CREATED → SIGNED → SUBMITTED → VALIDATING → VALID
                                    │
                                    └── INVALID  (with error code)
```

| Status     | Meaning                              | Action |
| ---------- | ------------------------------------ | ------ |
| CREATED    | XML built, unsigned                  | Sign |
| SIGNED     | Signed, not submitted                | POST to API |
| SUBMITTED  | Received, validation in progress     | Wait |
| VALIDATING | Verification (< 30 s)                | Wait |
| VALID      | Accepted, archived                   | Keep ack |
| INVALID    | Rejected for non-compliance          | Fix and resubmit |
| CANCELLED  | Replaced by credit note              | Reference credit note |

## Archiving

DGI requires **5 years** retention. TTN-managed archiving rates (TND):
- XML/data storage: 0.190 / 50 KB
- PDF copy: 0.250 each
- XML copy: 0.250 each

Average TEIF XML: 5–15 KB. Storage cost is negligible at SMB scale.

## Open questions (verify against TTN sandbox or official docs)

1. Exact OAuth2 grant payload (`client_credentials`? scopes? header style?).
2. Submission body: raw signed XML? base64 in JSON? multipart?
3. Error code catalogue for `INVALID` responses.
4. Whether `TaxCurrencyCode` is mandatory or optional in `<Header>` (Noqta lists it without an M/C/O label).
5. Canonical `unitCode` list — Noqta uses `HUR` for hours, `C62` for "piece"; need full UN/ECE 20 mapping for our domain.
6. Whether the `<Signature>` element must be a direct child of `<Invoice>` or wrapped (Noqta shows direct child).
