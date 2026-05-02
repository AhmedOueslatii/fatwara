// Mirrors backend/app/models/invoice.py exactly.
// Keep in sync — when the Pydantic models change, change these too.

export type InvoiceStatus =
  | "draft"
  | "queued"
  | "submitted"
  | "accepted"
  | "rejected"
  | "error";

export interface InvoiceLineItem {
  description: string;
  quantity: string;     // Decimal serialized as string to avoid float drift
  unit_price: string;
  tva_rate: string;     // "19", "7", "0"
}

export interface InvoiceCreate {
  supplier_name: string;
  supplier_matricule: string;
  supplier_address: string;
  buyer_name: string;
  buyer_matricule: string;
  invoice_date: string; // ISO date YYYY-MM-DD
  items: InvoiceLineItem[];
  currency: "TND";
}

export interface InvoiceResponse {
  invoice_id: string;
  idempotency_key: string;
  status: InvoiceStatus;
  ttn_reference: string | null;
  total_ht: string;
  total_tva: string;
  total_ttc: string;
  created_at: string;
}

export interface InvoiceStatusResponse {
  status: InvoiceStatus;
  ttn_reference: string | null;
}

export interface OnboardingStatus {
  cert_ok: boolean;
  ttn_ok: boolean;
  ready_to_invoice: boolean;
  cert_expires_at: string | null;
  cert_days_remaining: number | null;
}

export interface CertUploadResponse {
  cert_id: string;
  format: "pkcs12" | "pem";
  expires_at: string;
  days_until_expiry: number;
  warn: boolean;
}

export interface SystemHealth {
  status: "ok";
  schema_version: string;
  ttn_sandbox: boolean;
}
