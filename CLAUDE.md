# CLAUDE.md — Fatwara

Loaded automatically by Claude Code at the start of every session in this repo. Read this before doing anything substantive. The deep "why" lives in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — this file is the operating manual.

## 1. What this repo is

Fatwara is a Tunisian e-invoicing SaaS for liberal professionals (doctors, lawyers, accountants, consultants). The product:

1. Accepts invoice data via web form
2. Generates **TEIF 1.8.7 XML** (`urn:tn:gov:dgi:teif:1.8`) — the format the Tunisian DGI mandates
3. Signs with **XAdES-B** using an ANCE/TunTrust certificate the user uploads
4. Submits to **TTN** (Tunisie TradeNet), the government clearinghouse, and tracks status

Target: 14-day POC for a solo founder (Ahmed). Demo path: cert upload → invoice form → signed XML → mock TTN → status. Real TTN submission is deferred until Ahmed has matricule fiscal + TunTrust cert.

## 2. Stack

- **Backend:** FastAPI 0.115, Python 3.11, SQLAlchemy 2 async, Alembic, lxml, cryptography. Bcrypt + PyJWT cookie auth (no FastAPI-Users — we rolled our own; simpler for the POC).
- **Frontend:** Next.js 14 App Router, React 18, Tailwind, plain `fetch`. Auth via httpOnly cookie set by the backend.
- **Storage:** Postgres 16, MinIO (cert blobs).
- **Local dev:** docker-compose. `docker-compose.yml` runs db + minio + backend + frontend, all hot-reload.
- **CI:** GitHub Actions — `backend-ci.yml`, `frontend-ci.yml`, `compliance-gate.yml`.

## 3. Repo layout

```
backend/
  app/
    api/v1/         # routers: auth, invoices, onboarding, system
    auth/           # JWT, password hashing, current_user dep
    core/           # config (pydantic-settings), database (async engine)
    models/         # pydantic schemas (top-level), db/ SQLAlchemy models
    repositories/   # one repo per aggregate (InvoiceRepo, CertRepo, AuditRepo)
    services/       # teif_generator, cert_parser, storage (MinIO), xades_signer, ttn_client, invoice_pipeline
    workers/        # empty for now
  alembic/versions/ # migrations
  schemas/          # TEIF reference doc + XSD (XSD not yet bundled)
  tests/            # pytest, see conftest.py for fixtures
frontend/
  app/              # Next.js App Router pages
  components/       # shared UI (invoice-form, status-badge, ui/*)
  lib/              # api client, types, utils
docs/ARCHITECTURE.md  # the "why" — read this for design rationale
```

## 4. Always / never

**Always:**
- Wait for **green CI** on every PR before merging. No exceptions.
- Run backend tests inside docker compose, not against a local `.venv` (creating `backend/.venv/` makes uvicorn watchfiles thrash).
- Use the **PowerShell** tool on this machine — host is Windows. Bash is available via the Bash tool but PowerShell is primary.
- Convert relative dates in commit messages and docs to absolute (`2026-05-12`, not "today").
- When touching `teif_generator.py` or `app/models/invoice.py`, expect `compliance-gate.yml` to fire on the PR.
- New endpoints scope to `current_user` from `app.auth.deps` unless they're explicitly public.
- Repositories own their session and call `await session.commit()` themselves. Routes pass the session in via `Depends(get_session)`.
- Decimal amounts: 3-decimal quantization (`Decimal("0.001")`) — TEIF requirement.
- Matricule format: regex `^\d{7}[A-Z]/[A-Z]/[A-Z]/\d{3}$` (e.g. `1234567A/P/M/000`).

**Never:**
- Don't commit `.env` (only `.env.example`). Don't commit `frontend/node_modules/`.
- Don't venv inside `backend/` while docker compose is running.
- Don't bypass git hooks (`--no-verify`) — investigate the failure instead.
- Don't store cert passwords in the database. POC re-prompts on each signing operation.
- Don't put real TTN credentials anywhere. The `RealTTNClient` is a `NotImplementedError` skeleton until matricule arrives.
- Don't add Celery / RabbitMQ / Redis / a real queue for the POC. `BackgroundTasks` is enough.
- Don't introduce abstractions for hypothetical future requirements — see "Scope discipline" below.

## 5. Conventions

### Backend
- Async everywhere. No sync `def` for I/O paths.
- Errors → `HTTPException`. Domain-specific exceptions (`IdempotencyConflict`, `SigningError`, `TTNTimeout`, `StorageError`) raised by services, caught by routes.
- One repository per aggregate. Repositories take `AsyncSession` in `__init__`, do not create their own.
- Background work via `fastapi.BackgroundTasks`. The pipeline task owns its own DB session via `SessionLocal()` because the request session is closed by then.
- Audit-log everything that transitions invoice state. Use `AuditRepo.log(user_id=..., action=..., invoice_id=..., detail=...)`.

### Frontend
- Server components by default; `"use client"` only when needed (forms, polling, hooks).
- API calls go through `lib/api.ts` — never hand-craft `fetch` in pages.
- Types in `lib/types.ts` mirror Pydantic response models.
- Use the design system in `components/ui/*` (`Button`, `Input`, `Card`, `Label`). Don't reach for raw Tailwind buttons.

### Tests
- pytest + pytest-asyncio. `auth_client` fixture in `conftest.py` registers a user and carries the JWT cookie.
- `reset_db_between_tests` truncates `users, invoices, certs, audit_log`.
- `reset_minio_between_tests` clears the `certs` bucket; silently skips if MinIO is down (so unrelated tests still run).
- Mark MinIO-dependent test files with `pytestmark = pytest.mark.skipif(not _minio_available(), ...)`.

### Commits and PRs
- Conventional commits: `feat(backend): ...`, `fix(frontend): ...`, `ci(backend): ...`, `chore(...): ...`.
- One concern per PR. Slice big changes into stacked PRs rather than mega-PRs.
- Always add `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>` when the work was paired with Claude.

## 6. Known deferrals (don't "fix" these — they're deliberate)

These are flagged so future-you / future-Claude doesn't try to silently resolve them.

| Item | Status | Why deferred |
|---|---|---|
| **Real XAdES-B signing** | Stubbed in `xades_signer.py`; appends `<Signature stub="true">` marker | signxml 3.x pulls broken pyopenssl; signxml 4.x is a major API rework. Mock TTN accepts any bytes, so pipeline runs end-to-end. Swap site: `_stub_sign()`. |
| **Official `teif_1.8.7.xsd`** | Missing from `backend/schemas/` | Need to obtain from TTN developer portal. Compliance gate runs in skip mode until it lands, then auto-blocks merges that break schema. |
| **Real TTN client** | `RealTTNClient.submit()` raises `NotImplementedError` | Blocked on matricule fiscal → TunTrust cert → TTN partner registration. Mock TTN behind same interface; flip via `TTN_SANDBOX=false`. |
| **Retry worker** | `backend/app/workers/` empty | Pipeline runs inline via `BackgroundTasks`. Real worker is post-POC if TTN flakiness justifies it. |
| **QR code (CEV)** | Not implemented | TEIF spec requires it but TTN sandbox doesn't validate it. Add when needed. |
| **Prod Dockerfile + VPS deploy** | Only `Dockerfile.dev` exists | Deferred until POC demo is signed off. |
| **OCR (PDF → form pre-fill)** | Not started | Explicit days 12-14 stretch goal. |

## 7. Scope discipline

This is a 14-day POC for a solo founder. Apply this filter before adding code:

- **Bug fix?** Fix the bug. Don't refactor surrounding code.
- **New feature?** Build the smallest version that works. No "while we're here."
- **Abstraction?** Don't, until you have three concrete call sites that need it.
- **Error handling at internal boundaries?** Trust internal code. Validate only at API boundaries (route handlers, external service calls).
- **Comments?** Default to none. Only when WHY is non-obvious (a workaround, a TTN spec quirk, a hidden invariant).
- **Backwards-compat shims for unmerged work?** No. If something is removed, remove it cleanly.

When in doubt about scope: ask the user, with options. Don't speculatively expand.

## 8. Risk watch (project-management hat)

Things that turn a working demo into a non-shippable demo. Flag these proactively when you see them slipping.

1. **ANCE cert format chaos.** Multiple PKCS#12 + PEM variants exist in the wild. `cert_parser.py` must handle them all. Silent signing failure = invalid invoice = legal exposure for the user.
2. **Schema version pinning.** `TEIF_SCHEMA_VERSION` is a config flag in `app/core/config.py`. Never hardcode. XSD validation failure in CI must block merges.
3. **TTN access lead time.** Bureaucratic, not technical. The mock-first architecture exists so this doesn't block development — protect that property when refactoring.

## 9. When something feels off

- **CI red?** Read the failing job's logs in full before guessing. Don't push speculative fixes.
- **Memory says X but code says Y?** Trust the code. Update memory.
- **A subagent / `/ultrareview` report contradicts your local read?** Reconcile by reading the file yourself before deciding.
- **A migration is destructive?** Confirm with the user before running.
