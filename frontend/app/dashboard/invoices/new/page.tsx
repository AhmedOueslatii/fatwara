"use client";

import { useState } from "react";
import { InvoiceForm } from "@/components/invoice-form";
import { OcrUpload } from "@/components/ocr-upload";
import type { ExtractedInvoice } from "@/lib/types";

export default function NewInvoicePage() {
  const [extracted, setExtracted] = useState<ExtractedInvoice | undefined>();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Nouvelle facture</h1>
        <p className="text-slate-600">
          La facture sera generee en TEIF 1.8.7, signee XAdES-B, puis soumise a
          la TTN.
        </p>
      </div>

      <OcrUpload onExtracted={(data) => setExtracted(data)} />

      <InvoiceForm defaults={extracted} />
    </div>
  );
}
