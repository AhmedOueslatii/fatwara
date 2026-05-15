// Mirrors backend/app/models/invoice.py exactly.
// Keep in sync — when the Pydantic models change, change these too.

export type InvoiceStatus =
  | "draft"
  | "queued"
  | "submitted"
  | "accepted"
  | "rejected"
  | "error";

export type TaxCategory = "S" | "Z" | "E";

export interface Address {
  street_name: string;
  city_name: string;
  postal_zone: string;
  country_subentity: string;
  country_code: "TN";
}

export interface Party {
  name: string;
  matricule: string;
  address: Address;
}

export interface InvoiceLineItem {
  description: string;
  quantity: string;     // Decimal serialized as string to avoid float drift
  unit_price: string;
  tva_rate: string;     // "19", "13", "7", "0"
  tax_category?: TaxCategory | null;
  item_code?: string | null;
}

export interface InvoiceCreate {
  supplier: Party;
  customer: Party;
  invoice_date: string;       // ISO date YYYY-MM-DD
  issue_time?: string | null; // HH:MM:SS, defaults to now() server-side
  due_date?: string | null;
  invoice_type_code?: string; // defaults to "380"
  items: InvoiceLineItem[];
  currency: "TND";
  note?: string | null;
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

export interface InvoiceListItem {
  invoice_id: string;
  status: InvoiceStatus;
  invoice_date: string;
  customer_name: string;
  total_ttc: string;
  ttn_reference: string | null;
  created_at: string;
}

export interface UserResponse {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
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
