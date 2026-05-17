# Fatwara — Architecture

**Status:** active
**Last revised:** 2026-05-05
**Owner:** Ahmed Oueslati (solo)

This document captures *why* the stack looks the way it does. Code answers "what"; this answers "why this and not something else." Keep it short. Update it when an architectural decision changes — not for every code change.

---

## 1. Product context (so the architecture makes sense)

Fatwara is a Tunisian e-invoicing SaaS for liberal professionals (doctors, lawyers, accountants, consultants). The legal flow it automates:

1. The professional generates an invoice for a client.
2. The invoice is encoded as **TEIF 1.8.7 XML** (the format mandated by Tunisia's DGI tax authority).
3. The XML is **signed with XAdES-BES** using the professional's PKCS#12 certificate issued by **TunTrust** (ANCE, the Tunisian certificate authority).
4. The signed XML is **submitted to TTN** (Tunisie TradeNet, the government clearinghouse).
5. TTN returns a reference number — that's what gives the invoice legal standing.

The product wraps this with: signup, cert upload, invoice form, status tracking, retention.

**Out of scope for the POC:** WhatsApp, payments, OCR, RAG over Tunisian fiscal law (deferred).

## 2. Constraints that shape the stack

These are non-negotiable inputs the architecture has to respect:

| Constraint | Implication |
|---|---|
| Tunisian data residency (regulatory + trust) | Production hosting must be in Tunisia. No managed cloud BaaS in EU/US. |
| Solo founder, no funding, pre-revenue | Minimize ops burden and monthly cost. Boring tech beats clever tech. |
| 14-day POC timeline | Reuse mature libraries, don't write what's already commoditized. |
| TTN API access blocked on matricule fiscal | TTN integration must be **mockable**. The day creds arrive, only a base URL flips. |
| Tax data is sensitive + retained for 10 years | Postgres (real ACID, real backups), not NoSQL. Encrypted blob storage. |
| User cannot lose unsigned/signed XML | Both versions persisted, both retrievable, both auditable. |

## 3. The chosen stack — and why

### Backend — FastAPI + Postgres + MinIO + FastAPI-Users
- **FastAPI** for the API. Already chosen, already scaffolded. Async Python fits the IO-bound workload (TTN calls, DB calls).
- **Postgres** for relational data. Real SQL, real migrations, real tooling, no vendor lock-in. Will run in docker locally and on the production VPS.
- **SQLAlchemy 2.0 (async) + Alembic** for ORM and migrations. Mature, standard, swappable.
- **MinIO** for blob storage (PKCS#12 cert files). S3-compatible API so we can switch to AWS S3 / R2 later if we ever leave Tunisia. Single binary in prod, docker container locally.
- **FastAPI-Users** for auth (signup, login, JWT issuance, password reset). Battle-tested library; we don't write auth ourselves.

**Rejected: Supabase (managed and self-hosted).**
- Managed Supabase: data sits in EU/US, fails Tunisian residency requirement.
- Self-hosted Supabase: 7 services to operate, fragile self-host story, too much ops burden for a solo founder. We'd inherit GoTrue's self-host edge cases for no real gain.

**Rejected: Firebase.** NoSQL is wrong for relational invoice data (invoices ↔ line items ↔ tax buckets ↔ users ↔ certs).

### Frontend — Next.js + httpOnly cookie auth
- **Next.js 14 App Router**. Already scaffolded. Good for the SSR-friendly dashboard.
- **JWT in httpOnly cookie** issued by the FastAPI backend. Frontend never touches the token directly — XSS can't steal it. CSRF mitigated by SameSite=Lax + double-submit token on state-changing routes.
- **Rejected: localStorage tokens.** XSS-readable; for a product handling tax certificates, that's an unacceptable blast radius.

### Compliance and signing
- **lxml** for XML construction (already in use, working).
- **signxml** for XAdES-BES signing — RSA-SHA256, enveloped, C14N. The library handles the algorithm details TTN cares about.
- **Official TEIF XSD** — not yet bundled. CI compliance gate runs in skip mode until we obtain it from the TTN developer portal. When the file lands, the gate auto-blocks merges that break schema.

### OCR (invoice photo → form pre-fill)

- Vision-LLM extraction via a `OcrClient` interface, two implementations: Gemini 2.0 Flash (free, US-hosted) and Mistral Pixtral (free, EU-hosted). Provider switched by `OCR_PROVIDER` env var.
- **Residency note:** the source image is sent to the chosen provider for the duration of one HTTP call and is **not persisted** (not in Postgres, not in MinIO). Only the structured fields the user accepts are persisted, as part of the regular invoice flow. This is transient processing, the same category as transactional email — distinct from the storage-residency requirement that drove the no-Supabase decision. Documented in code at `backend/app/services/ocr_client.py` so the choice is auditable.
- If a stricter "no foreign processing" stance is later required, swap to a self-hosted Llama 3.2 Vision (or similar) on the Tunisian VPS — the `OcrClient` interface is the swap site.

### TTN integration — interface, not implementation
- One interface: `TTNClient`.
- Two implementations:
  - `MockTTNClient` — used during POC and CI. Returns plausible accept/reject responses synchronously. Lets us prove the full pipeline works without real credentials.
  - `RealTTNClient` — skeleton built now, switched on once Ahmed has matricule fiscal → TunTrust cert → TTN EDI registration → sandbox creds. The day creds arrive, we change a config flag and a base URL — no code rewrite.
- This is the single most important architectural property of the POC: **the absence of TTN credentials does not block development.**

## 4. Data model (high level)

```
users
  id (uuid, pk)
  email (unique)
  hashed_password
  is_active, is_verified
  created_at, updated_at

certs
  id (uuid, pk)
  user_id (fk users) UNIQUE      -- one cert per user for the POC
  format (pkcs12 | pem)
  storage_path                    -- MinIO object key
  expires_at
  created_at

invoices
  id (uuid, pk)
  user_id (fk users)
  idempotency_key (unique)        -- prevents duplicate submission
  status (draft | queued | submitted | accepted | rejected | error)
  invoice_date
  supplier_*, customer_*          -- denormalized snapshot at issue time
  total_ht, total_tva, total_ttc, currency
  teif_xml (bytea)                -- unsigned XML, audit
  signed_xml (bytea)              -- signed XML submitted to TTN
  ttn_reference
  created_at, updated_at

audit_log
  id (uuid, pk)
  invoice_id (fk invoices, nullable)
  user_id (fk users)
  action                           -- e.g. "cert.uploaded", "invoice.submitted", "invoice.accepted"
  detail (jsonb)
  created_at
```

Cert passwords are **never stored**. Re-prompted on each signing operation. That's a UX cost we're paying for a smaller blast radius — POC-acceptable, can revisit with envelope encryption later if user research demands it.

## 5. Request flow — happy path

```
[Browser] -- POST /auth/login --> [FastAPI: FastAPI-Users] -- verify --> [Postgres: users]
   <-- Set-Cookie: access_token=JWT (httpOnly, SameSite=Lax) --

[Browser] -- POST /onboarding/cert/upload (cookie + multipart .p12)
   --> [FastAPI: cert_parser] -- validate format/expiry
   --> [MinIO: put_object] -- store .p12 bytes
   --> [Postgres: certs INSERT]
   <-- 200 { cert_id, expires_at, days_until_expiry }

[Browser] -- POST /invoices (cookie + JSON body + cert_password)
   --> [FastAPI: validate body via Pydantic]
   --> [generate_teif_xml]                          -- pure, no IO
   --> [MinIO: get_object cert] + [signxml.sign]    -- XAdES-BES
   --> [TTNClient.submit(signed_xml)]                -- mock or real
   --> [Postgres: invoices INSERT with teif_xml + signed_xml + status]
   --> [Postgres: audit_log INSERT]
   <-- 200 { invoice_id, status, ttn_reference }

[Browser] -- GET /invoices/{id}/status (poll)
   --> [Postgres: invoices SELECT]
   <-- 200 { status, ttn_reference }
```

## 6. Local dev vs. production

### Local (developer machine)
- `docker-compose.yml` runs: postgres, minio, backend (FastAPI hot-reload), frontend (Next.js hot-reload).
- All secrets in `.env` (gitignored). `.env.example` committed.
- No HTTPS locally. Cookies set with `Secure=False` in dev.

### Production (Tunisian VPS)
- Single VPS, ~4 GB RAM / 2 vCPU / 40 GB SSD.
- Provider: one of Topnet / Tunisie Telecom Cloud / Ooredoo / GlobalNet — pick on price + uptime SLA.
- Stack runs via `docker-compose.prod.yml`:
  - Caddy (reverse proxy + automatic Let's Encrypt TLS)
  - FastAPI backend
  - Next.js frontend
  - Postgres (with pgbackrest or simple cron-based pg_dump for nightly backup)
  - MinIO
- DNS: A record pointing to VPS IP.
- Backups: nightly Postgres dump + MinIO snapshot, encrypted, copied to a *second* Tunisian location (second VPS or Tunisian object storage). **Backups must not leave Tunisia** — that would re-create the residency problem we're avoiding.
- Email (for FastAPI-Users password reset): TBD. Either Tunisian SMTP (Topnet, Ooredoo) or accept that transactional email leaves Tunisia (it's email metadata, not tax data — defensible).

### Cost ceiling for POC
- VPS: 60–120 TND/month
- Backup target: 10–20 TND/month
- Domain: ~30 TND/year
- Total: ~100 TND/month operational

## 7. What this architecture explicitly chooses *not* to do

These are deliberate omissions. If you're tempted to add them, re-read this section first.

- **No microservices.** One FastAPI app, one Next.js app. A monolith for years.
- **No message queue (Celery/RabbitMQ/Redis).** TTN submission is synchronous in the request handler for the POC. If TTN becomes flaky in production, *then* we add a queue.
- **No retry worker yet.** Mock TTN returns synchronously; real TTN failures get a manual retry button in the UI. Background retries are post-POC.
- **No multi-tenant isolation beyond `user_id` foreign keys.** No row-level security. RLS adds complexity for a single-user POC.
- **No real-time / websockets.** Status polling every few seconds is fine.
- **No CDN / edge caching.** One VPS, direct.
- **No observability platform (Sentry, Datadog).** Structured stdout logs to start. Add Sentry only if errors are hard to reproduce.

## 8. Decisions that are still open

These are flagged so we don't forget them:

- **Email provider for password reset.** Tunisian SMTP vs. transactional service. Decide before going to production.
- **Cert password storage.** POC = re-prompt. Post-POC = consider envelope encryption with a server-side KMS key.
- **Backup encryption-at-rest.** Need to choose the encryption tool (age, gpg, restic). Decide before first production deploy.
- **VPS provider.** Compare 2–3 Tunisian providers on price, uptime SLA, support quality. Decide before Phase 4.

## 9. How to evolve this document

- Update on architectural changes, not feature additions. Adding an endpoint = no update needed. Swapping Postgres for MySQL = update.
- When you change something here, also update the relevant memory entry (`project_architecture.md` in `~/.claude/projects/.../memory/`).
- If the document and the code disagree, the code is right and this is stale — fix the document immediately.
