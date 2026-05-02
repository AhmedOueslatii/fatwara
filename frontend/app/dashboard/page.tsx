import Link from "next/link";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardHome() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Tableau de bord</h1>
        <p className="text-slate-600">
          Generez des factures TEIF et suivez leur soumission a la TTN.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>1. Onboarding</CardTitle>
          </CardHeader>
          <CardBody className="space-y-3">
            <p className="text-sm text-slate-600">
              Importez votre certificat ANCE et vos identifiants TTN.
            </p>
            <Link
              href="/dashboard/onboarding"
              className="text-sm font-medium text-brand hover:underline"
            >
              Configurer →
            </Link>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>2. Nouvelle facture</CardTitle>
          </CardHeader>
          <CardBody className="space-y-3">
            <p className="text-sm text-slate-600">
              Saisissez fournisseur, client, lignes et TVA.
            </p>
            <Link
              href="/dashboard/invoices/new"
              className="text-sm font-medium text-brand hover:underline"
            >
              Creer →
            </Link>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>3. Suivi TTN</CardTitle>
          </CardHeader>
          <CardBody className="space-y-3">
            <p className="text-sm text-slate-600">
              Consultez le statut TTN de chaque facture soumise.
            </p>
            <Link
              href="/dashboard/invoices"
              className="text-sm font-medium text-brand hover:underline"
            >
              Voir les factures →
            </Link>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
