import { InvoiceForm } from "@/components/invoice-form";

export default function NewInvoicePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Nouvelle facture</h1>
        <p className="text-slate-600">
          La facture sera generee en TEIF 1.8.7, signee XAdES-B, puis soumise a
          la TTN.
        </p>
      </div>

      <InvoiceForm />
    </div>
  );
}
