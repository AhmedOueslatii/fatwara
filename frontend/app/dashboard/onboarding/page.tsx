"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { CertUploadResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

export default function OnboardingPage() {
  const [file, setFile] = useState<File | null>(null);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CertUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.onboarding.uploadCert(file, password);
      setResult(res);
    } catch (err) {
      if (err instanceof ApiError) {
        const detail =
          typeof err.body === "object" && err.body && "detail" in err.body
            ? String((err.body as { detail: unknown }).detail)
            : err.message;
        setError(detail);
      } else {
        setError("Erreur inconnue lors de l'envoi.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Onboarding</h1>
        <p className="text-slate-600">
          Importez votre certificat ANCE pour signer les factures.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Certificat ANCE</CardTitle>
        </CardHeader>
        <CardBody>
          <form onSubmit={onUpload} className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="cert">
                Fichier (.p12, .pfx, .pem)
              </Label>
              <Input
                id="cert"
                type="file"
                accept=".p12,.pfx,.pem,.crt"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Mot de passe (PKCS#12 uniquement)</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Laisser vide si PEM"
              />
            </div>

            {error && (
              <p className="text-sm text-red-600" role="alert">
                {error}
              </p>
            )}

            <Button type="submit" loading={loading} disabled={!file}>
              Verifier le certificat
            </Button>
          </form>

          {result && (
            <div className="mt-6 rounded-md border border-emerald-200 bg-emerald-50 p-4 text-sm">
              <p className="font-medium text-emerald-900">
                Certificat valide ({result.format.toUpperCase()})
              </p>
              <p className="mt-1 text-emerald-800">
                Expire le{" "}
                <span className="font-medium">
                  {new Date(result.expires_at).toLocaleDateString("fr-TN")}
                </span>{" "}
                ({result.days_until_expiry} jours restants)
              </p>
              {result.warn && (
                <p className="mt-2 rounded bg-amber-100 p-2 text-amber-900">
                  Attention : votre certificat expire dans moins de 30 jours.
                  Renouvelez-le aupres de l'ANCE pour eviter une interruption.
                </p>
              )}
            </div>
          )}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Identifiants TTN (a venir)</CardTitle>
        </CardHeader>
        <CardBody>
          <p className="text-sm text-slate-600">
            Le formulaire d'identifiants TTN OAuth2 sera ajoute apres
            l'enregistrement au portail developpeur TTN.
          </p>
        </CardBody>
      </Card>
    </div>
  );
}
