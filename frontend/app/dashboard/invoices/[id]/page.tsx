"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { InvoiceStatus } from "@/lib/types";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/status-badge";

const TERMINAL: InvoiceStatus[] = ["accepted", "rejected", "error"];

export default function InvoiceStatusPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [status, setStatus] = useState<InvoiceStatus>("queued");
  const [ttnRef, setTtnRef] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function poll() {
      try {
        const res = await api.invoices.status(id);
        if (!active) return;
        setStatus(res.status);
        setTtnRef(res.ttn_reference);
      } catch (err) {
        if (!active) return;
        if (err instanceof ApiError) setError(err.message);
        else setError("Erreur reseau");
      }
    }

    poll();
    const interval = setInterval(() => {
      if (TERMINAL.includes(status)) {
        clearInterval(interval);
        return;
      }
      poll();
    }, 3000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [id, status]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Suivi de facture</h1>
        <p className="font-mono text-sm text-slate-600">{id}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Statut TTN</CardTitle>
        </CardHeader>
        <CardBody className="space-y-3">
          <div className="flex items-center gap-3">
            <StatusBadge status={status} />
            {!TERMINAL.includes(status) && (
              <span className="text-sm text-slate-500">
                Actualisation toutes les 3 secondes...
              </span>
            )}
          </div>
          {ttnRef && (
            <p className="text-sm">
              <span className="text-slate-500">Reference TTN :</span>{" "}
              <span className="font-mono">{ttnRef}</span>
            </p>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
        </CardBody>
      </Card>
    </div>
  );
}
