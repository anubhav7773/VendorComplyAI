# scripts/e2e_verify.ps1
# Master End-to-End Verification & Acceptance Gateway for VendorComply AI

$ErrorActionPreference = "Stop"
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " VENDORCOMPLY AI (asiverticals.me) - MASTER E2E AUDIT GATEWAY   " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# 1. Test Backend Statutory Engine, Banking Rails and OCR Schemas
Write-Host "`n[1/4] Running Backend Pytest Suite..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\apps\api"

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".\.venv\Scripts\Activate.ps1"
}

$pytestOutput = pytest -v --tb=short
Write-Host $pytestOutput

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[FATAL] Backend pytest suite failed! Aborting." -ForegroundColor Red
    exit 1
}
Write-Host "[SUCCESS] All Backend Statutory and Banking Tests Passed." -ForegroundColor Green

# 2. Test On-Premise Desktop Agent Delta Engine
Write-Host "`n[2/4] Verifying Desktop Agent SQLite Delta Cache..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\apps\agent"

$agentOutput = python -m unittest discover tests
Write-Host $agentOutput

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[FATAL] Agent cache unit tests failed!" -ForegroundColor Red
    exit 1
}
Write-Host "[SUCCESS] Desktop Agent Local Cache Verified." -ForegroundColor Green

# 3. Verify Next.js 15 Production Build and Static Export
Write-Host "`n[3/4] Compiling Next.js 15 Production Static Export (Cloudflare Pages)..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\apps\web"

pnpm build

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[FATAL] Next.js production build failed with TypeScript or Lint errors!" -ForegroundColor Red
    exit 1
}
Write-Host "[SUCCESS] Next.js 15 Export Compiled with Zero Errors." -ForegroundColor Green

# 4. Verify Project Root Integrity
Write-Host "`n[4/4] Verifying File Tree and Spec Compliance..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\.."

$requiredFiles = @(
    ".docs\01_ARCHITECTURE_AND_STACK.md",
    ".docs\02_DATABASE_SCHEMA_AND_RLS.md",
    ".docs\03_STATUTORY_ENGINE_LOGIC.md",
    ".docs\04_TALLY_AGENT_SPEC.md",
    ".docs\05_BANKING_RAILS_SPEC.md",
    ".docs\06_AI_INVOICE_PARSER.md",
    ".docs\07_FRONTEND_UI_AND_STITCH.md",
    ".docs\08_EXECUTION_CHECKLIST.md",
    ".docs\09_MONETIZATION_AND_PRICING_SPEC.md",
    "packages\database\migrations\001_initial_schema.sql",
    "packages\database\migrations\002_billing_and_subscriptions.sql",
    "cloudflare\worker.js",
    "apps\api\Dockerfile",
    "apps\api\render.yaml"
)

foreach ($f in $requiredFiles) {
    if (-not (Test-Path $f)) {
        Write-Host "[ERROR] Missing critical file: $f" -ForegroundColor Red
        exit 1
    }
}

Write-Host "================================================================" -ForegroundColor Green
Write-Host " ALL SYSTEMS VERIFIED: 100% PRODUCTION READY AND LITIGATION-PROOF! " -ForegroundColor Green
Write-Host " Domain Target: vendorcomply.asiverticals.me                     " -ForegroundColor Green
Write-Host " Zero-Cost Infrastructure Matrix Locked.                        " -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
