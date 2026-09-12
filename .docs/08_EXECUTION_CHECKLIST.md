# ==============================================================================
# VENDORCOMPLY AI — ANTIGRAVITY IDE MASTER EXECUTION CHECKLIST & BUILD PROTOCOL
# Document ID: 08_EXECUTION_CHECKLIST.md
# Parent Entity: asiverticals.me
# Target System: VendorComply AI (vendorcomply.asiverticals.me)
# Architecture Standard: Modular Monorepo / Zero-Cost Cloud / On-Premise Windows Daemon
# ==============================================================================

## 1. ORCHESTRATION PHILOSOPHY FOR ANTIGRAVITY IDE

To build a zero-defect, production-grade enterprise platform, **Antigravity IDE must never attempt to generate the entire monorepo in a single execution step**. Monolithic code generation exhausts context limits, introduces truncated functions, and silently skips edge-case validations.

Execution is strictly divided into **8 Phased Milestones**. Each phase:
1. Consumes a specific reference document from `/.docs/`.
2. Implements a discrete subsystem with complete type definitions and zero placeholders.
3. Passes an explicit **Verification Gateway** (unit test, build pass, or schema migration check) before the next phase begins.

[Phase 1: Repo Setup] ──► [Phase 2: Database DDL & RLS] ──► [Phase 3: Statutory Engine]
│                                                            │
▼                                                            ▼
[Phase 6: AI OCR Parser] ◄── [Phase 5: Desktop Agent] ◄── [Phase 4: Banking Rails]
│
▼
[Phase 7: Next.js Frontend] ──► [Phase 8: Edge Routing & Deploy]


---

## 2. PRE-FLIGHT ENVIRONMENT MATRIX

Before issuing the first prompt to Antigravity IDE, verify that the following local developer runtime dependencies are available:

* [ ] **Node.js**: `v20.x` or `v22.x` LTS (`node -v`)
* [ ] **Package Manager**: `pnpm` (recommended) or `npm` (`pnpm -v`)
* [ ] **Python**: `3.11.x` or `3.12.x` 64-bit (`python --version`)
* [ ] **Git**: Configured with user email and branch `main` (`git status`)
* [ ] **Supabase CLI**: (Optional for local migrations) or active Supabase project URL and keys.
* [ ] **Operating System**: Windows 11 with WSL2 (Ubuntu) / PowerShell 7+.

---

## 3. PHASED EXECUTION ROADMAP & PROMPT SEQUENCER

---

### PHASE 1: Monorepo Scaffolding & Tooling Setup
* **Reference Spec**: `.docs/01_ARCHITECTURE_AND_STACK.md`
* **Objective**: Initialize the monorepo workspace containing `/apps/web`, `/apps/api`, `/apps/agent`, and `/packages/database`. Configure root package scripts, TypeScript configurations, Python virtual environments, and `.gitignore`.
* **Verification Gateway**:
  * Root `pnpm install` or `npm install` completes with zero errors.
  * Python virtual environment created with required baseline dependencies.
* **Antigravity Prompt 1**:
  ```text
  You are the Principal Systems Architect for VendorComply AI (under parent entity asiverticals.me).
  Read and adhere strictly to .docs/01_ARCHITECTURE_AND_STACK.md.
  
  TASK:
  1. Initialize a production monorepo workspace at the project root.
  2. Create the exact directory tree specified in Section 4 of Doc 01:
     - /apps/web (Next.js 15 App Router workspace)
     - /apps/api (FastAPI Python backend workspace)
     - /apps/agent (On-premise Windows daemon workspace)
     - /packages/database (SQL migrations & seed workspace)
  3. Generate root configuration files:
     - pnpm-workspace.yaml (or package.json workspaces configuration)
     - Root .gitignore (covering node_modules, .next, __pycache__, .venv, dist, build, *.db, *.spec)
     - .env.example templates for all workspaces as defined in Section 8 of Doc 01.
  4. Ensure all package.json files have strict TypeScript and modern build configurations.
  Do not create functional business code yet. Output complete configuration files with zero placeholders.
PHASE 2: Database Migrations & Row-Level Security (RLS)
Reference Spec: .docs/02_DATABASE_SCHEMA_AND_RLS.md

Objective: Establish the PostgreSQL 16 schema in Supabase with strict tenant isolation, UUID primary keys, composite B-tree indexes, and dispute triggers.

Verification Gateway:

Execute migration against Supabase SQL Editor.

Verify all 10 tables exist: tenants, tenant_users, vendor_master, purchase_vouchers, voucher_payments, statutory_disputes, statutory_exposure_cache, batch_payout_runs, batch_payout_items, audit_trail.

Confirm RLS is enabled on all 10 tables.

Antigravity Prompt 2:

Plaintext
Read and adhere strictly to .docs/02_DATABASE_SCHEMA_AND_RLS.md.

TASK:
1. In /packages/database/migrations/001_initial_schema.sql, generate the complete, executable PostgreSQL DDL script.
2. Include all custom ENUM types: msme_category_type, msme_activity_type, voucher_status_type, banking_rail_type, payout_status_type, objection_channel_type, tenant_role_type.
3. Create all 10 tables with exact column definitions, numeric precisions (NUMERIC(15,2)), foreign keys with cascade rules, and check constraints.
4. Implement all Row-Level Security (RLS) policies using the cached helper function public.current_tenant_id() bound to auth.jwt() ->> 'tenant_id'.
5. Include all composite B-Tree indexes for rolling aging and March 31 tax cutoff performance.
6. Implement PL/pgSQL triggers:
   - Automatic updated_at synchronization
   - Statutory dispute freeze trigger (auto-locking vouchers to DISPUTED_HOLD)
   - Payment waterfall reconciliation trigger (recalculating paid and outstanding amounts)
Ensure the SQL is 100% valid, idempotent where appropriate, and ready to run in Supabase.
PHASE 3: Core Statutory Calculation Engine & Test Suite
Reference Spec: .docs/03_STATUTORY_ENGINE_LOGIC.md

Objective: Build the deterministic mathematical calculation engine in Python FastAPI using strict decimal.Decimal arithmetic to compute Section 43B(h) disallowance and MSMED Section 16 penal interest.

Verification Gateway:

Run pytest apps/api/tests/test_statutory_engine.py.

All test fixtures (Trader Exemption, Waterfall Compounding, Dispute Freeze) must pass with zero assertions failing.

Antigravity Prompt 3:

Plaintext
Read and adhere strictly to .docs/03_STATUTORY_ENGINE_LOGIC.md.

TASK:
1. In /apps/api/app/services/statutory_engine.py, implement the complete MSMEStatutoryEngine class.
2. Implement zero floating-point arithmetic using strict decimal.Decimal with ROUND_HALF_UP quantization to 2 decimal places.
3. Implement:
   - Section 15 statutory due date calculation (15 days default vs capped 45 days contract).
   - Section 16 monthly rest compound interest with exact calendar boundaries and leap year handling.
   - Partial payment waterfall algorithm reducing active principal before monthly rests.
   - Section 43B(h) year-end corporate tax disallowance base calculation (excluding GST if ITC claimed).
   - Ministry OM 2021 Trader Exemption (NIC codes 45, 46, 47 set to ₹0.00 exposure).
   - Dispute hold status freezing the statutory clock.
4. In /apps/api/tests/test_statutory_engine.py, implement the complete pytest test suite matching the fixtures in Section 5 of Doc 03.
Ensure all Pydantic models are strictly typed and error handling is comprehensive.
PHASE 4: Connected Banking Batch Exporter & Sanitization Rails
Reference Spec: .docs/05_BANKING_RAILS_SPEC.md

Objective: Implement the corporate banking batch payment file generators for ICICI CIB (PAB_VENDOR) and HDFC ENet with two-pass sanitization, IFSC regex gates, and SHA-256 cryptographic checksum calculation.

Verification Gateway:

Run pytest apps/api/tests/test_banking_exporter.py.

Verify ICICI files strictly yield 11 CSV columns and HDFC files strictly yield 10 CSV columns with zero comma shifts.

Antigravity Prompt 4:

Plaintext
Read and adhere strictly to .docs/05_BANKING_RAILS_SPEC.md.

TASK:
1. In /apps/api/app/services/banking_exporter.py, implement the BankingBatchExporter class and PayoutLineItem Pydantic schema.
2. Implement the strict two-pass text sanitizer:
   - Pass 1: Strip commas, semicolons, quotes, slashes, and control characters to prevent CSV column shifts.
   - Pass 2: Filter strictly to alphanumeric characters and hyphens, convert to uppercase, and enforce column width bounds.
3. Implement generate_icici_cib_batch producing the standard 11-column PAB_VENDOR CSV layout.
4. Implement generate_hdfc_enet_batch producing the standard 10-column ENet CSV layout.
5. Calculate and return the SHA-256 cryptographic checksum of generated CSV bytes.
6. In /apps/api/app/routers/payouts.py, implement the Maker-Checker authorization endpoint enforcing corporate signatory roles and mandatory legal indemnification confirmation.
7. In /apps/api/tests/test_banking_exporter.py, implement the complete pytest test suite.
PHASE 5: On-Premise Tally Sync Daemon & PyInstaller Build
Reference Spec: .docs/04_TALLY_AGENT_SPEC.md

Objective: Build the local Windows background daemon that queries Tally Prime on localhost:9000, maintains a local SQLite delta cache, signs payloads with HMAC-SHA256, and compiles to a standalone .exe.

Verification Gateway:

Run python apps/agent/main.py --test-tally against a local/mock port.

Run pyinstaller --clean apps/agent/vendorcomply_agent.spec and verify VendorComplyAgent.exe is generated in apps/agent/dist/.

Antigravity Prompt 5:

Plaintext
Read and adhere strictly to .docs/04_TALLY_AGENT_SPEC.md.

TASK:
1. In /apps/agent/src/, implement:
   - config.py: Pydantic configuration loader reading agent_config.json.
   - tally_client.py: XML envelope builder and HTTP client querying [http://127.0.0.1:9000](http://127.0.0.1:9000) for Sundry Creditors, Purchase Vouchers, and Payment settlements (Agst Ref). Handles 'No Company Loaded' and network errors cleanly.
   - local_cache.py: SQLite manager maintaining fingerprint hashes to compute deltas and eliminate redundant cloud transmissions.
   - sync_manager.py: HTTPS sender packaging deltas and computing HMAC-SHA256 signatures over request bodies with replay attack timestamp validation.
2. In /apps/agent/main.py, implement the CLI runner supporting --test-tally, --sync-now, and long-polling background daemon modes.
3. In /apps/agent/vendorcomply_agent.spec, provide the complete PyInstaller build specification to compile the daemon into a single standalone Windows executable.
4. In /apps/api/app/routers/sync.py, implement the cloud ingestion endpoint verifying HMAC signatures and upserting deltas into Supabase.
PHASE 6: AI Invoice OCR & Structured Extraction Engine
Reference Spec: .docs/06_AI_INVOICE_PARSER.md

Objective: Implement the document normalization and structured invoice extraction engine supporting Outlines guided decoding locally with Google AI Studio free tier fallback.

Verification Gateway:

Run pytest apps/api/tests/test_ocr_extractor.py.

Validate regex patterns for PAN and GSTIN extraction and ensure 100% valid Pydantic object returns.

Antigravity Prompt 6:

Plaintext
Read and adhere strictly to .docs/06_AI_INVOICE_PARSER.md.

TASK:
1. In /apps/api/app/schemas/invoice_ocr.py, implement the StructuredInvoiceOutput and InvoiceLineItem Pydantic v2 schemas with strict regex validation for Indian PAN and GSTIN numbers.
2. In /apps/api/app/services/document_preprocessor.py, implement the PDF and image preprocessing pipeline utilizing PyMuPDF (fitz) and Pillow to normalize aspect ratio, contrast, and orientation.
3. In /apps/api/app/services/ocr_extractor.py, implement the InvoiceOCRExtractor class featuring dual-engine support:
   - Local CUDA Outlines guided decoding with Qwen2-VL-2B-Instruct.
   - Cloud fallback using Google AI Studio Gemini 2.0 Flash with response_schema enforcement.
4. In /apps/api/app/routers/ocr.py, implement the /api/v1/ocr/parse-invoice endpoint accepting multipart/form-data uploads up to 10MB.
5. In /apps/api/tests/test_ocr_extractor.py, implement the verification tests.
PHASE 7: Next.js 15 Web Application & UI Components
Reference Spec: .docs/07_FRONTEND_UI_AND_STITCH.md

Objective: Build the Next.js 15 CFO Executive Dashboard adhering to the frozen Google Stitch design tokens, including KPI cards, 15/45-day rolling matrix, dispute modal, batch release modal, and Form 3CD Clause 22 audit views.

Verification Gateway:

Run pnpm --filter web build (or npm run build inside apps/web).

Verify zero TypeScript errors and successful static/edge page compilation.

Antigravity Prompt 7:

Plaintext
Read and adhere strictly to .docs/07_FRONTEND_UI_AND_STITCH.md.

TASK:
1. In /apps/web, set up Next.js 15 (App Router) with Tailwind CSS, Lucide icons, and Shadcn UI primitives.
2. Implement the persistent application shell in /apps/web/app/(dashboard)/layout.tsx featuring the 240px slate-950 sidebar, company header, and March 31 countdown pill.
3. Implement dashboard components:
   - /components/dashboard/kpi-row.tsx: Top 4 statutory risk cards.
   - /components/aging/aging-table.tsx: 15/45-day rolling matrix with countdown status pills and filter tabs.
   - /components/aging/dispute-modal.tsx: Section 15 MSMED Act statutory dispute logging modal.
   - /components/payouts/batch-release-modal.tsx: Maker-Checker approval modal with ICICI/HDFC selectors and indemnification checkbox.
4. Implement application pages:
   - /app/(dashboard)/page.tsx: CFO Executive Radar.
   - /app/(dashboard)/aging/page.tsx: Rolling matrix view.
   - /app/(dashboard)/payouts/page.tsx: Monday batch execution screen.
   - /app/(dashboard)/audit-3cd/page.tsx: Form 3CD Clause 22 Tax Audit Scrutiny view.
Ensure clean modular code, tabular font formatting for currency, and zero layout shift.
PHASE 8: Edge Routing, Keep-Alive Cron & Production Deployment
Reference Spec: .docs/01_ARCHITECTURE_AND_STACK.md

Objective: Deploy the Next.js web application to Cloudflare Pages under vendorcomply.asiverticals.me, deploy FastAPI to Render Free Tier, and configure the Cloudflare Worker keep-alive cron to eliminate cold starts.

Verification Gateway:

Send GET https://vendorcomply.asiverticals.me/api/v1/health and verify HTTP 200 response with sub-100ms latency.

Verify full TLS strict encryption and domain routing under asiverticals.me.

Antigravity Prompt 8:

Plaintext
Read and adhere strictly to Section 2 and Section 7 of .docs/01_ARCHITECTURE_AND_STACK.md.

TASK:
1. In /cloudflare/worker.js, implement the Cloudflare Worker script that:
   - Acts as an edge reverse proxy routing /api/* requests to the FastAPI Render service.
   - Executes a scheduled cron trigger every 10 minutes (* /10 * * * *) pinging the /health endpoint to prevent Render free-tier cold starts.
2. In /apps/web, configure next.config.ts for Cloudflare Pages static export (@cloudflare/next-on-pages or output: 'export').
3. In /apps/api, provide a production-ready Dockerfile and render.yaml blueprint for one-click deployment to Render Web Services.
4. Provide the exact DNS configuration instructions for Cloudflare DNS to bind:
   - vendorcomply.asiverticals.me -> Cloudflare Pages
   - api-vendorcomply.asiverticals.me -> Render Service
Verify SSL/TLS settings and confirm zero-cost operational limits.
4. MASTER VERIFICATION & PRODUCTION ACCEPTANCE AUDIT
Before presenting the platform to corporate clients or statutory auditors, run the following automated end-to-end audit:

Bash
# 1. Run Backend Statutory & Banking Test Suites
cd apps/api
pytest -v --tb=short

# 2. Verify Frontend Production Build
cd ../web
pnpm build

# 3. Test Tally XML Ingestion (Port 9000 Mock)
cd ../agent
python main.py --test-tally

# 4. Verify Database RLS Isolation
# Execute cross-tenant query test in Supabase SQL Editor:
# Tenant A must receive 0 rows when attempting to select Tenant B vouchers.
Final Acceptance Sign-Off Criteria:
[ ] Legal Protection: Wholesale/retail traders (NIC 45, 46, 47) show ₹0.00 in 43B(h) exposure.

[ ] Dispute Defense: Logged disputes freeze aging countdowns and suspend Section 16 interest.

[ ] Banking Accuracy: ICICI and HDFC CSV exports contain zero illegal commas or column shifts.

[ ] Audit Trail: Every payout authorization logs an immutable SHA-256 hash in PostgreSQL.

[ ] Zero Cloud Cost: Entire cloud architecture operates sustainably within free quotas.