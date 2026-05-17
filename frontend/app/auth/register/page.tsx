"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caracteres.");
      return;
    }
    setLoading(true);
    try {
      await api.auth.register(email, password);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError("Cet email est deja enregistre.");
      } else if (err instanceof ApiError) {
        setError(`Erreur ${err.status}`);
      } else {
        setError("Erreur reseau.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Creer un compte</CardTitle>
        </CardHeader>
        <CardBody>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="email">Email professionnel</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Mot de passe</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
              />
              <p className="text-xs text-slate-500">8 caracteres minimum.</p>
            </div>

            {error && (
              <p className="text-sm text-red-600" role="alert">
                {error}
              </p>
            )}

            <Button type="submit" loading={loading} className="w-full">
              Creer le compte
            </Button>

            <p className="text-center text-sm text-slate-600">
              Deja inscrit ?{" "}
              <Link
                href="/auth/login"
                className="font-medium text-brand hover:underline"
              >
                Se connecter
              </Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </main>
  );
}
