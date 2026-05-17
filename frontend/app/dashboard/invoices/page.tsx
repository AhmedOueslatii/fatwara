"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { InvoiceListItem } from "@/lib/types";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { formatDate, formatTND } from "@/lib/utils";

export default function InvoicesListPage() {
  const [invoices, setInvoices] = useState<InvoiceListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    api.invoices
      .list()
      .then((data) => {
        if (active) setInvoices(data);
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiError && err.status === 401) {
          setError("Session expiree. Reconnectez-vous.");
        } else {
          setError("Impossible de charger les factures.");
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Factures</h1>
          <p className="text-slate-600">
            Vos factures TEIF generees, signees et soumises.
          </p>
        </div>
        <Link href="/dashboard/invoices/new">
          <Button>Nouvelle facture</Button>
        </Link>
      </div>

      {error && (
        <Card>
          <CardBody>
            <p className="text-sm text-red-600">{error}</p>
          </CardBody>
        </Card>
      )}

      {!error && invoices === null && (
        <Card>
          <CardBody>
            <p className="text-sm text-slate-500">Chargement...</p>
          </CardBody>
        </Card>
      )}

      {!error && invoices && invoices.length === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Aucune facture</CardTitle>
          </CardHeader>
          <CardBody>
            <p className="text-sm text-slate-600">
              Vous n&apos;avez pas encore cree de facture. Cliquez sur{" "}
              <em>Nouvelle facture</em> pour commencer.
            </p>
          </CardBody>
        </Card>
      )}

      {!error && invoices && invoices.length > 0 && (
        <Card>
          <CardBody className="p-0">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Client</th>
                  <th className="px-4 py-3">Total TTC</th>
                  <th className="px-4 py-3">Statut</th>
                  <th className="px-4 py-3">Reference TTN</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr
                    key={inv.invoice_id}
                    className="border-b border-slate-100 last:border-0"
                  >
                    <td className="px-4 py-3">
                      {formatDate(inv.invoice_date)}
                    </td>
                    <td className="px-4 py-3">{inv.customer_name}</td>
                    <td className="px-4 py-3 font-medium">
                      {formatTND(inv.total_ttc)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={inv.status} />
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-600">
                      {inv.ttn_reference ?? "-"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/dashboard/invoices/${inv.invoice_id}`}
                        className="text-sm font-medium text-brand hover:underline"
                      >
                        Suivi →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
