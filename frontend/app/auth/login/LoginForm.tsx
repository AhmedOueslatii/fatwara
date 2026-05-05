"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginForm() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Connexion</CardTitle>
        </CardHeader>
        <CardBody>
          <form
            onSubmit={(e) => e.preventDefault()}
            className="space-y-4"
            aria-disabled
          >
            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" disabled autoComplete="email" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Mot de passe</Label>
              <Input
                id="password"
                type="password"
                disabled
                autoComplete="current-password"
              />
            </div>

            <p className="rounded-md bg-amber-50 p-3 text-sm text-amber-900">
              L&apos;authentification arrive bientot. Pour l&apos;instant, le
              tableau de bord est accessible sans connexion.
            </p>

            <Button type="submit" disabled className="w-full">
              Se connecter
            </Button>

            <p className="text-center text-sm text-slate-600">
              <Link
                href="/dashboard"
                className="font-medium text-brand hover:underline"
              >
                Acceder au tableau de bord
              </Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </main>
  );
}
