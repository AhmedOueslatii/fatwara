"""Generate a realistic Tunisian invoice PDF for OCR demo testing.

Zero dependencies — emits a single-page PDF directly using the spec. Output:
backend/tests/fixtures/sample_invoice.pdf (already gitignored if pdf is in
your local .gitignore; otherwise add it).

Usage:  python scripts/gen_sample_invoice.py
"""

from pathlib import Path

LINES = [
    ("FACTURE N° FACT-2026-0042", 18, "bold"),
    ("", 8, ""),
    ("Date : 15/05/2026", 11, ""),
    ("Echeance : 30/05/2026", 11, ""),
    ("", 6, ""),
    ("FOURNISSEUR", 12, "bold"),
    ("Cabinet Dr. Ahmed Ben Salah", 11, ""),
    ("Cardiologue", 10, ""),
    ("12 Avenue Habib Bourguiba, 1000 Tunis", 10, ""),
    ("Matricule fiscal : 1234567A/P/M/000", 10, ""),
    ("", 8, ""),
    ("CLIENT", 12, "bold"),
    ("STEG - Societe Tunisienne d'Electricite et du Gaz", 11, ""),
    ("38 Rue Kemal Ataturk, 1080 Tunis", 10, ""),
    ("Matricule fiscal : 0001234B/N/M/000", 10, ""),
    ("", 12, ""),
    ("DESIGNATION                          Qte    PU HT     TVA    Total HT", 10, "bold"),
    ("------------------------------------------------------------------", 10, ""),
    ("Consultation cardiologique             1   180,000   19%    180,000", 10, ""),
    ("Echographie Doppler                    1   240,000   19%    240,000", 10, ""),
    ("Test d'effort                          1   320,000   19%    320,000", 10, ""),
    ("", 12, ""),
    ("                                          Total HT       :    740,000 TND", 10, ""),
    ("                                          TVA 19%        :    140,600 TND", 10, ""),
    ("                                          Total TTC      :    880,600 TND", 11, "bold"),
    ("", 12, ""),
    ("Mode de paiement : Virement bancaire", 10, ""),
    ("RIB : 04 015 0123456789 12", 10, ""),
    ("", 8, ""),
    ("Cachet et signature du fournisseur", 9, ""),
]


def escape_pdf_text(s: str) -> str:
    """Escape parens and backslashes for the PDF string literal."""
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_content_stream() -> bytes:
    """Build the page content stream: text positioning + font selection."""
    parts = ["BT"]
    y = 780
    for text, size, weight in LINES:
        font = "/F2" if weight == "bold" else "/F1"
        # Each line: font + size, position, then show text.
        parts.append(f"{font} {size} Tf")
        parts.append(f"50 {y} Td")
        if text:
            parts.append(f"({escape_pdf_text(text)}) Tj")
        # Move down for next line. Td is relative; we already moved to (50,y),
        # next iteration we move to (50, y - size - 4) by setting absolute Td.
        # Reset by emitting a fresh "Tm" each line is simpler:
        parts.append("ET")
        parts.append("BT")
        y -= max(size + 3, 11)
    parts.append("ET")
    return "\n".join(parts).encode("latin-1")


def build_pdf() -> bytes:
    """Assemble a minimal valid PDF with two fonts (Helvetica + Helvetica-Bold)."""
    content = build_content_stream()

    objects: list[bytes] = []

    # 1: catalog
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    # 2: pages
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # 3: page (A4 = 595 x 842 pt)
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> "
        b"/Contents 4 0 R >>"
    )
    # 4: content stream
    objects.append(
        f"<< /Length {len(content)} >>\nstream\n".encode("latin-1")
        + content
        + b"\nendstream"
    )
    # 5: font Helvetica
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    # 6: font Helvetica-Bold
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    # Assemble with byte offsets for the xref table.
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]  # object 0 is the free entry
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("latin-1") + body + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode("latin-1")

    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("latin-1")
    return bytes(out)


if __name__ == "__main__":
    out_path = Path(__file__).parent.parent / "backend" / "tests" / "fixtures" / "sample_invoice.pdf"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(build_pdf())
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")
