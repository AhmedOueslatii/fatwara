import { cn } from "@/lib/utils";
import type { InvoiceStatus } from "@/lib/types";

const STYLES: Record<InvoiceStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  queued: "bg-amber-100 text-amber-800",
  submitted: "bg-blue-100 text-blue-800",
  accepted: "bg-emerald-100 text-emerald-800",
  rejected: "bg-red-100 text-red-800",
  error: "bg-red-100 text-red-800",
};

const LABELS: Record<InvoiceStatus, string> = {
  draft: "Brouillon",
  queued: "En attente",
  submitted: "Soumise",
  accepted: "Acceptee TTN",
  rejected: "Rejetee TTN",
  error: "Erreur",
};

export function StatusBadge({ status }: { status: InvoiceStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        STYLES[status],
      )}
    >
      {LABELS[status]}
    </span>
  );
}
