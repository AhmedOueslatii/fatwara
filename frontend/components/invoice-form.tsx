"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { InvoiceCreate, InvoiceLineItem } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { formatTND, isValidMatricule } from "@/lib/utils";

const EMPTY_ITEM: InvoiceLineItem = {
  description: "",
  quantity: "1",
  unit_price: "0.000",
  tva_rate: "19",
};

const EMPTY_FORM: InvoiceCreate = {
  supplier_name: "",
  supplier_matricule: "",
  supplier_address: "",
  buyer_name: "",
  buyer_matricule: "",
  invoice_date: new Date().toISOString().slice(0, 10),
  items: [{ ...EMPTY_ITEM }],
  currency: "TND",
};

export function InvoiceForm() {
  const router = useRouter();
  const [form, setForm] = useState<InvoiceCreate>(EMPTY_FORM);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totals = useMemo(() => computeTotals(form.items), [form.items]);

  function setField<K extends keyof InvoiceCreate>(
    key: K,
    value: InvoiceCreate[K],
  ) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function setItem(idx: number, patch: Partial<InvoiceLineItem>) {
    setForm((f) => {
      const items = f.items.map((it, i) =>
        i === idx ? { ...it, ...patch } : it,
      );
      return { ...f, items };
    });
  }

  function addItem() {
    setForm((f) => ({ ...f, items: [...f.items, { ...EMPTY_ITEM }] }));
  }

  function removeItem(idx: number) {
    setForm((f) => ({ ...f, items: f.items.filter((_, i) => i !== idx) }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!isValidMatricule(form.supplier_matricule)) {
      setError("Matricule fournisseur invalide. Format attendu : 1234567A/P/M/000");
      return;
    }
    if (!isValidMatricule(form.buyer_matricule)) {
      setError("Matricule client invalide. Format attendu : 1234567A/P/M/000");
      return;
    }

    setLoading(true);
    try {
      const res = await api.invoices.create(form);
      router.push(`/dashboard/invoices/${res.invoice_id}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(JSON.stringify(err.body));
      } else {
        setError("Erreur reseau lors de l'envoi.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Fournisseur (vous)</CardTitle>
        </CardHeader>
        <CardBody className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field
            label="Raison sociale"
            value={form.supplier_name}
            onChange={(v) => setField("supplier_name", v)}
            required
          />
          <Field
            label="Matricule fiscal"
            value={form.supplier_matricule}
            onChange={(v) => setField("supplier_matricule", v)}
            placeholder="1234567A/P/M/000"
            required
          />
          <Field
            label="Adresse"
            value={form.supplier_address}
            onChange={(v) => setField("supplier_address", v)}
            className="md:col-span-2"
            required
          />
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Client</CardTitle>
        </CardHeader>
        <CardBody className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field
            label="Raison sociale"
            value={form.buyer_name}
            onChange={(v) => setField("buyer_name", v)}
            required
          />
          <Field
            label="Matricule fiscal"
            value={form.buyer_matricule}
            onChange={(v) => setField("buyer_matricule", v)}
            placeholder="9876543B/P/M/000"
            required
          />
          <div className="space-y-1">
            <Label htmlFor="invoice_date">Date de facture</Label>
            <Input
              id="invoice_date"
              type="date"
              value={form.invoice_date}
              onChange={(e) => setField("invoice_date", e.target.value)}
              required
            />
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Lignes</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {form.items.map((item, idx) => (
            <div
              key={idx}
              className="grid grid-cols-12 items-end gap-2 border-b border-slate-100 pb-3"
            >
              <div className="col-span-12 md:col-span-5">
                <Label>Description</Label>
                <Input
                  value={item.description}
                  onChange={(e) =>
                    setItem(idx, { description: e.target.value })
                  }
                  required
                />
              </div>
              <div className="col-span-3 md:col-span-2">
                <Label>Qte</Label>
                <Input
                  type="number"
                  step="0.001"
                  min="0"
                  value={item.quantity}
                  onChange={(e) => setItem(idx, { quantity: e.target.value })}
                  required
                />
              </div>
              <div className="col-span-4 md:col-span-2">
                <Label>PU HT (TND)</Label>
                <Input
                  type="number"
                  step="0.001"
                  min="0"
                  value={item.unit_price}
                  onChange={(e) =>
                    setItem(idx, { unit_price: e.target.value })
                  }
                  required
                />
              </div>
              <div className="col-span-3 md:col-span-2">
                <Label>TVA %</Label>
                <select
                  className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
                  value={item.tva_rate}
                  onChange={(e) => setItem(idx, { tva_rate: e.target.value })}
                >
                  <option value="0">0</option>
                  <option value="7">7</option>
                  <option value="19">19</option>
                </select>
              </div>
              <div className="col-span-2 md:col-span-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeItem(idx)}
                  disabled={form.items.length === 1}
                >
                  X
                </Button>
              </div>
            </div>
          ))}

          <Button type="button" variant="secondary" size="sm" onClick={addItem}>
            + Ajouter une ligne
          </Button>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Totaux</CardTitle>
        </CardHeader>
        <CardBody className="grid grid-cols-3 gap-4 text-sm">
          <Total label="Total HT" value={totals.ht} />
          <Total label="Total TVA" value={totals.tva} />
          <Total label="Total TTC" value={totals.ttc} highlight />
        </CardBody>
      </Card>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      <div className="flex justify-end">
        <Button type="submit" loading={loading} size="lg">
          Generer + signer + soumettre
        </Button>
      </div>
    </form>
  );
}

function Field({
  label,
  value,
  onChange,
  required,
  placeholder,
  className,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  placeholder?: string;
  className?: string;
}) {
  return (
    <div className={"space-y-1 " + (className ?? "")}>
      <Label>{label}</Label>
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        placeholder={placeholder}
      />
    </div>
  );
}

function Total({
  label,
  value,
  highlight,
}: {
  label: string;
  value: number;
  highlight?: boolean;
}) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div
        className={
          "mt-1 text-lg font-semibold " +
          (highlight ? "text-brand" : "text-slate-900")
        }
      >
        {formatTND(value)}
      </div>
    </div>
  );
}

function computeTotals(items: InvoiceLineItem[]) {
  let ht = 0;
  let tva = 0;
  for (const it of items) {
    const q = Number(it.quantity) || 0;
    const p = Number(it.unit_price) || 0;
    const r = Number(it.tva_rate) || 0;
    const line = q * p;
    ht += line;
    tva += line * (r / 100);
  }
  return { ht, tva, ttc: ht + tva };
}
