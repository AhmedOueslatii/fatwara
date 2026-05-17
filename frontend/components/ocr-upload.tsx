"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { ExtractedInvoice } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

type Provider = "gemini" | "mistral";

export function OcrUpload({
  onExtracted,
}: {
  onExtracted: (data: ExtractedInvoice, provider: string) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [provider, setProvider] = useState<Provider>("gemini");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);

  async function onExtract() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setDone(null);
    try {
      const res = await api.invoices.extract(file, provider);
      onExtracted(res.extracted, res.provider);
      setDone(`Extrait via ${res.provider}. Verifiez et completez le formulaire.`);
    } catch (err) {
      if (err instanceof ApiError) {
        const detail =
          typeof err.body === "object" && err.body && "detail" in err.body
            ? String((err.body as { detail: unknown }).detail)
            : err.message;
        setError(detail);
      } else {
        setError("Erreur reseau lors de l'extraction.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="border-brand-200 bg-brand-50/40">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-lg">✨</span>
          Importer depuis une photo (IA)
        </CardTitle>
      </CardHeader>
      <CardBody className="space-y-4">
        <p className="text-sm text-slate-600">
          Photo ou PDF d&apos;une facture papier. L&apos;IA extrait fournisseur,
          client, date et lignes pour pre-remplir le formulaire ci-dessous.
        </p>

        <div className="flex flex-col gap-3 md:flex-row md:items-end">
          <div className="flex-1 space-y-1">
            <label className="text-xs font-medium uppercase tracking-wide text-slate-600">
              Fichier
            </label>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full rounded-md border border-slate-300 bg-white p-2 text-sm file:mr-3 file:rounded file:border-0 file:bg-brand-100 file:px-3 file:py-1.5 file:text-xs file:font-semibold file:text-brand-700 hover:file:bg-brand-200"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium uppercase tracking-wide text-slate-600">
              Moteur IA
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as Provider)}
              className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
            >
              <option value="gemini">Gemini 2.0 Flash</option>
              <option value="mistral">Mistral Pixtral</option>
            </select>
          </div>

          <Button
            type="button"
            onClick={onExtract}
            loading={loading}
            disabled={!file}
          >
            Extraire
          </Button>
        </div>

        {error && (
          <p className="text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        {done && (
          <p className="rounded-md bg-emerald-50 p-3 text-sm text-emerald-800">
            {done}
          </p>
        )}
      </CardBody>
    </Card>
  );
}
