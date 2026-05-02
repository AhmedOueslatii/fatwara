CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    idempotency_key TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    supplier_name TEXT NOT NULL,
    supplier_matricule TEXT NOT NULL,
    buyer_name TEXT NOT NULL,
    buyer_matricule TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    total_ht NUMERIC(12,3),
    total_tva NUMERIC(12,3),
    total_ttc NUMERIC(12,3),
    currency TEXT DEFAULT 'TND',
    teif_xml BYTEA,
    ttn_reference TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID REFERENCES invoices(id),
    user_id UUID,
    action TEXT NOT NULL,
    detail JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS certs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    format TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    warn_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);
