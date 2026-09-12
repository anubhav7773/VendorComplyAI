# ==============================================================================
# VENDORCOMPLY AI — SYSTEM ARCHITECTURE & FREE-TIER STACK SPECIFICATION
# Document ID: 01_ARCHITECTURE_AND_STACK.md
# Parent Entity: asiverticals.me
# Production Subdomain: vendorcomply.asiverticals.me
# Target Environment: 100% Free Tier (Production Grade & Anti-Litigation Hardened)
# ==============================================================================

## 1. EXECUTIVE ARCHITECTURAL BLUEPRINT

VendorComply AI is an autonomous, B2B statutory compliance and accounts payable (AP) automation platform operated under the parent corporate umbrella **asiverticals.me**. The platform is engineered to eliminate corporate tax disallowance exposure under Section 43B(h) of the Income-tax Act, 1961, and prevent non-deductible compound penal interest liabilities under Section 16 of the MSMED Act, 2006.

The system uses a **Hybrid Edge-Cloud-Desktop Architecture**:
1. **On-Premise Desktop Daemon (`apps/agent`)**: A headless Windows background service operating on the client's accounting server that interfaces with Tally Prime's local XML HTTP server on `http://127.0.0.1:9000` to extract purchase vouchers, bill allocations, and vendor ledgers[cite: 1, 2].
2. **Cloudflare Global Edge Proxy (`vendorcomply.asiverticals.me`)**: Unifies frontend delivery, static asset caching, and backend API routing under a single domain origin to completely eliminate Cross-Origin Resource Sharing (CORS) friction and browser latency.
3. **Core Statutory & Payout API (`apps/api`)**: A high-performance Python FastAPI service running statutory aging calculations, 15/45-day rolling clocks, NIC-code trader exclusions, and bank-grade batch payout generation[cite: 1, 2].
4. **Relational Multi-Tenant Data Store (`packages/database`)**: Supabase PostgreSQL featuring strict Row-Level Security (RLS) bound to JWT tenant claims, composite B-Tree indexes, and transaction connection pooling.
5. **CFO Executive Web App (`apps/web`)**: A Next.js 15 (App Router) web application providing the 43B(h) Countdown Radar, Maker-Checker authorization modals, and Tax Audit Form 3CD Clause 22 reporting[cite: 1, 2].

---

## 2. DOMAIN TOPOLOGY & EDGE ROUTING

All public and internal network traffic is anchored to the parent root domain `asiverticals.me`.

                              [Internet / Client Browser]
                                           │
                                           ▼
                 [Cloudflare Edge: vendorcomply.asiverticals.me]
                 (Strict SSL/TLS, DDoS Shield, Zero-Cost CDN)
                                           │
             ┌─────────────────────────────┴─────────────────────────────┐
             ▼                                                           ▼
     Path: /* (Frontend)                                       Path: /api/v1/* (Backend)
 Cloudflare Pages Deployment                                 Cloudflare Worker Proxy
Next.js 15 (Edge/Static Export)                             Render Web Service (FastAPI)
[apps/web.vendorcomply.pages.dev]                           [api-vendorcomply.onrender.com]│                                                           │└─────────────────────────────┬─────────────────────────────┘▼[Supabase Cloud (PostgreSQL 16)]Database Host: aws-0-ap-south-1.pooler.supabase.comPort 6543 (Supavisor Transaction Pooler)▲│ Secure HTTPS Sync (HMAC-SHA256)│[Client On-Premise Windows Machine]VendorComply Agent (PyInstaller Daemon)│ Local XML/HTTP (Port 9000)▼[Tally Prime Desktop Engine]
### Routing Rules (Cloudflare Worker Edge Proxy):
* `GET/POST/PUT/DELETE https://vendorcomply.asiverticals.me/api/*`: Strips `/api` prefix and proxies directly to `https://api-vendorcomply.onrender.com/*`.
* `GET https://vendorcomply.asiverticals.me/*`: Delivers static and edge-rendered assets from Cloudflare Pages.
* **CORS Elimination**: Because both API and Web UI originate from `vendorcomply.asiverticals.me`, standard browser `Access-Control-Allow-Origin` preflight checks are bypassed, optimizing page load times and mobile web execution.

---

## 3. 100% FREE-TIER INFRASTRUCTURE MATRIX & CONSTRAINTS

The entire platform operates sustainably within the guaranteed free tiers of enterprise infrastructure providers:

| Component | Provider & Tier | Quota Allocation | Mitigation & Safety Architecture |
| :--- | :--- | :--- | :--- |
| **Frontend Web App** | **Cloudflare Pages** (Free) | Unlimited requests, unlimited bandwidth, 500 builds/month | Static export (`output: 'export'`) with edge SSR via `@cloudflare/next-on-pages`. Zero bandwidth or hosting fees. |
| **Edge Proxy & Crons** | **Cloudflare Workers** (Free) | 100,000 requests/day, 10ms CPU time/request | Handles `/api/*` reverse proxying and executes cron triggers every 10 minutes to prevent backend sleeping. |
| **Core Backend** | **Render Web Service** (Free) | 512 MB RAM, 0.1 CPU, 750 hours/month | Memory-optimized FastAPI application. Cold-starts eliminated via Cloudflare Worker scheduled keep-alive ping. |
| **Database & Auth** | **Supabase PostgreSQL** (Free) | 500 MB storage, 50,000 monthly active users, 500k Edge requests | Strict data eviction policies on ephemeral logs; Supavisor transaction pooler (Port 6543) prevents client connection starvation. |
| **Blob / File Storage** | **Cloudflare R2** (Free) | 10 GB storage/month, 10M Class B operations, **$0 Egress Fees** | Stores encrypted generated Bank CSV exports, Tax Audit working sheets, and raw invoice PDF attachments. |
| **AI Structured OCR** | **Outlines + Local VLM / Free Cloud API** | Zero Token Costs / 1,500 free requests/day | Executes via quantized local vision models on client agent or Free Gemini 2.0 Flash fallback via Google AI Studio. |
| **Tally Local Daemon** | **PyInstaller Standalone Executable** | Unlimited / Self-hosted on client hardware | Runs on client Windows hardware (0 cloud compute consumed)[cite: 1, 2]. |

---

## 4. MONOREPO STRUCTURAL SPECIFICATION

The repository uses a modular monorepo workspace structure configured for standard package managers (`pnpm` or `npm`):

```text
vendorcomply-ai/
├── .docs/                                # Master Architecture & Specification System
│   ├── 01_ARCHITECTURE_AND_STACK.md      # This file
│   ├── 02_DATABASE_SCHEMA_AND_RLS.md     # Supabase DDL & RLS Policies
│   ├── 03_STATUTORY_ENGINE_LOGIC.md     # 43B(h) & MSMED Mathematical Algorithms
│   ├── 04_TALLY_AGENT_SPEC.md           # Tally XML Gateway & Windows Agent
│   ├── 05_BANKING_RAILS_SPEC.md         # ICICI & HDFC Batch Payout Engine
│   ├── 06_AI_INVOICE_PARSER.md          # Structured OCR & Pydantic FSM
│   ├── 07_FRONTEND_UI_AND_STITCH.md     # Next.js Pages & Design Tokens
│   └── 08_EXECUTION_CHECKLIST.md        # Antigravity Step-by-Step Build Order
│
├── apps/
│   ├── web/                              # Next.js 15 Frontend Web Application
│   │   ├── app/                          # App Router Directory
│   │   │   ├── (auth)/login/page.tsx     # Enterprise Login & Legal Shield Acceptance
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx            # Shell Layout (Sidebar, Org Selector, Cutoff Pill)
│   │   │   │   ├── page.tsx              # CFO Executive Exposure Radar (Dashboard)
│   │   │   │   ├── aging/page.tsx        # 15/45-Day Rolling Countdown Matrix
│   │   │   │   ├── payouts/page.tsx      # Monday Morning Batch Run & Banking Exporter
│   │   │   │   ├── vendors/page.tsx      # Sundry Creditors & Udyam Intelligence Directory
│   │   │   │   └── audit-3cd/page.tsx    # CA Tax Audit Clause 22 Scrutiny Portal
│   │   │   ├── api/                      # Edge Webhook Handlers
│   │   │   └── layout.tsx                # Global Root Layout & Font Definitions
│   │   ├── components/                   # Shadcn UI & Custom Domain Components
│   │   │   ├── ui/                       # Buttons, Dialogs, Tables, Tooltips, Badges
│   │   │   ├── dashboard/                # KPICard, ExposureChart, CountdownBadge
│   │   │   ├── payouts/                  # MakerCheckerModal, BankFormatSelector
│   │   │   └── legal/                    # StatutoryDisclaimerBanner, AuditChecksumModal
│   │   ├── lib/                          # Supabase Browser Client, Formatting Utils
│   │   ├── package.json
│   │   ├── tailwind.config.ts
│   │   └── next.config.ts
│   │
│   ├── api/                              # FastAPI Backend Service (Render Deployment)
│   │   ├── app/
│   │   │   ├── core/                     # Configuration, Security, CORS, JWT
│   │   │   │   ├── config.py             # Pydantic BaseSettings & Env Validation
│   │   │   │   ├── security.py           # HMAC Agent Verification & JWT Claim Decoding
│   │   │   │   └── database.py           # Async SQLAlchemy Engine & Session Factory
│   │   │   ├── models/                   # SQLAlchemy ORM Models (Mirroring Supabase DDL)
│   │   │   ├── schemas/                  # Pydantic v2 Request/Response Schemas
│   │   │   ├── services/                 # Core Business & Statutory Engines
│   │   │   │   ├── statutory_engine.py   # 43B(h), Sec 16 Interest & Waterfall Logic
│   │   │   │   ├── trader_classifier.py  # NIC Code 45/46/47 Auto-Exemption Logic
│   │   │   │   ├── banking_exporter.py   # ICICI CIB & HDFC ENet CSV File Generators
│   │   │   │   └── ocr_extractor.py      # Outlines / Structured Vision Pipeline
│   │   │   ├── routers/                  # API Endpoints
│   │   │   │   ├── health.py             # Keep-Alive Route for Cloudflare Cron
│   │   │   │   ├── sync.py               # Desktop Agent Ingestion Gateway
│   │   │   │   ├── exposure.py           # Realtime 43B(h) Analytics Endpoints
│   │   │   │   ├── payouts.py            # Batch Run Lifecycle & File Downloads
│   │   │   │   └── audit.py              # Form 3CD Clause 22 Export Endpoints
│   │   │   └── main.py                   # FastAPI Application Entrypoint
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── agent/                            # Standalone On-Premise Windows Daemon
│       ├── src/
│       │   ├── tally_client.py           # Port 9000 XML Envelope Requester & Parser
│       │   ├── local_cache.py            # SQLite Delta Cache (Prevents Redundant Sync)
│       │   ├── sync_manager.py           # Outbound HTTPS Payload Packager & HMAC Signer
│       │   └── config.py                 # Local Config Reader (Tenant Key, Port, Intervals)
│       ├── main.py                       # CLI & Windows Background Daemon Runner
│       ├── build_installer.py            # PyInstaller Script (Compiles to Single .exe)
│       └── requirements.txt
│
└── packages/
    └── database/                         # Database Migration & Schema Assets
        ├── migrations/
        │   └── 001_initial_schema.sql    # Complete PostgreSQL DDL & RLS Policies
        └── seeds/
            └── nic_codes_seed.sql        # Master Dataset of MSME & Trader NIC Codes
5. NETWORK SECURITY & TENANT ISOLATION ARCHITECTUREMulti-tenancy is enforced strictly at the database engine level via PostgreSQL Row-Level Security (RLS). The platform completely segregates the accounting ledgers, purchase vouchers, and bank credentials of all client companies operating under asiverticals.me[cite: 1, 2].                   [Incoming Request to FastAPI Backend]
                                   │
               Does header contain "Authorization: Bearer <JWT>"?
                                   │
                  ┌────────────────┴────────────────┐
                  ▼ YES                             ▼ NO
       Decode Supabase JWT               Does header contain "X-Agent-Key"?
                  │                                 │
                  ▼                                 ▼ YES
       Extract "tenant_id" Claim         Lookup Agent Secret in `tenants`
                  │                                 │
                  ▼                                 ▼
       Set Postgres Session Variable:    Set Postgres Session Variable:
       SET LOCAL request.jwt.claim.tenant_id = '<tenant_id>';
                                   │
                                   ▼
                     [Execute Database SQL Query]
                                   │
                  Postgres Engine Checks RLS Policy:
       `USING (tenant_id = (SELECT public.current_tenant_id()))`
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼ MATCH                                             ▼ MISMATCH
   Return Tenant Data                              Empty Result Set (HTTP 404/403)
On-Premise Desktop Agent Authentication:When an enterprise signs up on vendorcomply.asiverticals.me, a cryptographic tenant_id (UUID) and an agent_api_secret (64-character hex string) are generated.The agent configuration file agent_config.json stores these credentials securely on the client machine.Every payload sent from the Windows agent to https://vendorcomply.asiverticals.me/api/v1/sync/push includes:Header X-Tenant-ID: The tenant's UUID.Header X-Agent-Signature: An HMAC-SHA256 signature computed across the JSON payload using the agent_api_secret.Header X-Sync-Timestamp: ISO 8601 UTC timestamp (requests older than 300 seconds are rejected to prevent replay attacks).6. END-TO-END DATA LIFECYCLE & REQUEST SEQUENCEThe following sequence details how an invoice moves from Tally Prime desktop to cloud calculation, CFO batch approval, and zero-shift banking export[cite: 1, 2]:[Tally Prime]     [Local Agent]     [FastAPI Edge]    [Supabase DB]     [CFO Dashboard]    [ICICI/HDFC Bank]
      │                 │                 │                 │                  │                 │
      │◄──Poll Port 9000│                 │                 │                  │                 │
      │   (XML Request)[cite: 1, 2]       │                 │                  │                 │
      │───XML Vouchers─►│                 │                 │                  │                 │
      │   (Response)[cite: 2]    │                 │                 │                  │                 │
      │                 │──Compute Delta──│                 │                  │                 │
      │                 │  (SHA-256 Hash) │                 │                  │                 │
      │                 │──Push New Bills►│                 │                  │                 │
      │                 │  (HMAC Signed)  │                 │                  │                 │
      │                 │                 │──Run 43B(h) Math│                  │                 │
      │                 │                 │  & Trader Check[cite: 2]          │                 │
      │                 │                 │──Upsert Rows───►│                  │                 │
      │                 │                 │  (RLS Protected)[cite: 2]          │                 │
      │                 │                 │                 │◄──Fetch Radar────│                 │
      │                 │                 │                 │   (Live Aging)   │                 │
      │                 │                 │                 │───Return Metrics►│                 │
      │                 │                 │                 │   (Red/Amber KPI)│                 │
      │                 │                 │                 │                  │                 │
      │                 │                 │                 │  [Monday 9 AM]   │                 │
      │                 │                 │                 │◄──Approve Batch──│                 │
      │                 │                 │                 │   (Maker-Checker)│                 │
      │                 │                 │◄──Request Export│                  │                 │
      │                 │                 │   (ICICI / HDFC)[cite: 2]          │                 │
      │                 │                 │──Sanitize Text──│                  │                 │
      │                 │                 │  (Strip Commas)[cite: 2]          │                 │
      │                 │                 │──Generate CSV──►│                  │                 │
      │                 │                 │  (SHA-256 Logged)                  │                 │
      │                 │                 │───────────────────────────────────►│                 │
      │                 │                 │    Return Bulletproof Bank File    │                 │
      │                 │                 │                                    │──Upload Batch──►│
      │                 │                 │                                    │   (1-Click CMS) │
7. RENDER COLD-START MITIGATION & KEEP-ALIVE WORKERRender free web services spin down after 15 minutes of inactivity, resulting in a 50-second cold-start latency for the next API call. To ensure zero cold starts, a Cloudflare Worker executes a scheduled cron job every 10 minutes.Cloudflare Worker Script (workers/keep_alive.js):JavaScriptexport default {
  // Cloudflare Scheduled Cron: Runs every 10 minutes (* /10 * * * *)
  async scheduled(event, env, ctx) {
    const targetUrl = "[https://api-vendorcomply.onrender.com/api/v1/health](https://api-vendorcomply.onrender.com/api/v1/health)";
    try {
      const response = await fetch(targetUrl, {
        method: "GET",
        headers: { "User-Agent": "VendorComply-KeepAlive-Bot/1.0" }
      });
      console.log(`Keep-alive ping dispatched at ${new Date().toISOString()}. Status: ${response.status}`);
    } catch (error) {
      console.error(`Keep-alive failed: ${error.message}`);
    }
  },

  // Standard Edge Reverse Proxy for API traffic
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) {
      const backendUrl = "[https://api-vendorcomply.onrender.com](https://api-vendorcomply.onrender.com)" + url.pathname.replace(/^\/api/, "") + url.search;
      const modifiedRequest = new Request(backendUrl, {
        method: request.method,
        headers: request.headers,
        body: request.body,
        redirect: "follow"
      });
      return fetch(modifiedRequest);
    }
    return new Response("Not Found", { status: 404 });
  }
};
8. COMPREHENSIVE ENVIRONMENT VARIABLE CONTRACTSStrict type validation must be enforced using Pydantic v2 Settings in the backend and T3-Env / Zod in the frontend. Missing variables must halt application boot immediately.A. Core API Service (apps/api/.env)Bash# Environment Mode
ENVIRONMENT=production
DEBUG=false
APP_NAME="VendorComply AI Engine"
PARENT_COMPANY="asiverticals.me"

# Cloudflare Edge & Domain Binding
ALLOWED_ORIGINS=["[https://vendorcomply.asiverticals.me](https://vendorcomply.asiverticals.me)"]
PUBLIC_API_URL="[https://vendorcomply.asiverticals.me/api](https://vendorcomply.asiverticals.me/api)"

# Supabase Database (Port 6543 Supavisor Connection Pooler)
DATABASE_URL="postgresql://postgres.[PROJECT-REF]:[PASSWORD]@[aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require](https://aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require)"
DIRECT_DATABASE_URL="postgresql://postgres.[PROJECT-REF]:[PASSWORD]@[aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require](https://aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require)"

# Supabase Authentication & Secret
SUPABASE_URL="https://[PROJECT-REF].supabase.co"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOi..."
SUPABASE_JWT_SECRET="super-secret-jwt-signing-key-from-supabase-settings"

# Statutory Baseline Configuration
DEFAULT_CORPORATE_TAX_RATE=0.25168 # Section 115BAA: 22% + 10% Surcharge + 4% Cess
CURRENT_RBI_BANK_RATE=0.0650       # 6.50% p.a. (MSMED Sec 16 rate = 19.50% p.a.)

# Security Salt for Desktop Agent HMAC Verification
AGENT_HMAC_MASTER_KEY="64-byte-cryptographically-random-hex-string"
B. Next.js Web Frontend (apps/web/.env.local)Bash# Public Client-Side Variables
NEXT_PUBLIC_APP_URL="[https://vendorcomply.asiverticals.me](https://vendorcomply.asiverticals.me)"
NEXT_PUBLIC_PARENT_DOMAIN="asiverticals.me"
NEXT_PUBLIC_SUPABASE_URL="https://[PROJECT-REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOi..."

# Server-Side Only Secrets
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOi..."
INTERNAL_API_URL="[https://vendorcomply.asiverticals.me/api/v1](https://vendorcomply.asiverticals.me/api/v1)"
C. Desktop Tally Agent (apps/agent/agent_config.json)JSON{
  "tally_host": "[http://127.0.0.1](http://127.0.0.1)",
  "tally_port": 9000,
  "tally_company_name": "ABC Manufacturing Pvt Ltd",
  "cloud_sync_url": "[https://vendorcomply.asiverticals.me/api/v1/sync/push](https://vendorcomply.asiverticals.me/api/v1/sync/push)",
  "tenant_id": "00000000-0000-0000-0000-000000000000",
  "agent_secret_key": "YOUR_64_CHAR_HEX_AGENT_SECRET_KEY",
  "sync_interval_seconds": 3600,
  "local_cache_db_path": "./tally_local_cache.db"
}
9. NON-NEGOTIABLE ARCHITECTURAL GUARDRAILSWhen generating code in Antigravity IDE, the following architectural invariants must NEVER be violated:Zero Raw SQL without Tenant Predicates: Direct SQL queries must never be written without an explicit tenant_id filter, even though Row-Level Security is active at the engine level[cite: 2].Double Precision Floating-Point Ban: Financial amounts, interest figures, and tax rates must NEVER use standard IEEE 754 floating-point types (float in Python or standard number in JS math). All calculations must use decimal.Decimal with explicit ROUND_HALF_UP quantization to exactly 2 decimal places to prevent penny-discrepancies in Tax Audit Form 3CD[cite: 2].No Unsanitized CSV String Concatenation: Banking CSV export files must never be assembled using raw string template interpolation (f"{name},{amt}"). They must strictly pass through Python's standard csv.writer with explicit text sanitization stripping all commas, quotes, and control characters to prevent mainframe column shifting[cite: 2].Mandatory Statutory Dispute Audit Trail: An invoice can never be marked as DISPUTED_HOLD without logging the dispute date, objection reference number, and objection channel (Email/WhatsApp/Courier) to satisfy Section 15 of the MSMED Act during IT department scrutinies.No Client Secret Exposure: The SUPABASE_SERVICE_ROLE_KEY and AGENT_HMAC_MASTER_KEY must never be referenced or imported in /apps/web client components.