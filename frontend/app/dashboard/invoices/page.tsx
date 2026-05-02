import Link from "next/link";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function InvoicesListPage() {
  // POC: list endpoint not yet implemented on the backend.
  // Wire to api.invoices.list() once GET /api/v1/invoices is available.
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

      <Card>
        <CardHeader>
          <CardTitle>Aucune facture</CardTitle>
        </CardHeader>
        <CardBody>
          <p className="text-sm text-slate-600">
            Le listing sera branche sur GET /api/v1/invoices une fois
            l'endpoint backend ajoute.
          </p>
        </CardBody>
      </Card>
    </div>
  );
}
