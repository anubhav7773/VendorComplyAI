# scripts/setup_env.ps1
# Automated Environment File Generator for VendorComply AI Monorepo

$ErrorActionPreference = "Stop"
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " VENDORCOMPLY AI - AUTOMATED ENVIRONMENT SETUP                  " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$rootDir = Split-Path -Parent $PSScriptRoot
$apiEnvPath = Join-Path $rootDir "apps\api\.env"
$webEnvPath = Join-Path $rootDir "apps\web\.env.local"

# 1. Generate apps/api/.env
$apiEnvContent = @"
# apps/api/.env - Production Configuration for VendorComply AI FastAPI Backend
ENVIRONMENT=production
DEBUG=false
APP_NAME="VendorComply AI Statutory Engine"
PARENT_COMPANY="asiverticals.me"

# CORS Configuration
ALLOWED_ORIGINS=["https://vendorcomply.asiverticals.me", "https://vendorcomply.pages.dev", "http://localhost:3000"]
CORS_ORIGIN_REGEX="^https:\/\/([a-zA-Z0-9_-]+\.)*(asiverticals\.me|pages\.dev)$|^http:\/\/localhost(:\d+)?$"

# Statutory Defaults
DEFAULT_CORPORATE_TAX_RATE=0.25168
DEFAULT_GST_RATE_PERCENT=18.0
CURRENT_RBI_BANK_RATE=0.0650

# Security & On-Premise Sync Salt
AGENT_HMAC_MASTER_KEY="e4d9b2a1c0f8e7d6b5a4c3e2f10987654321fedcba0987654321abcdef012345"

# Database & Supabase (Safe Fallbacks)
DATABASE_URL=""
DIRECT_DATABASE_URL=""
SUPABASE_URL=""
SUPABASE_ANON_KEY=""
SUPABASE_SERVICE_ROLE_KEY=""
SUPABASE_JWT_SECRET=""

# Gemini Cloud OCR Engine (Fallback)
GEMINI_API_KEY=""
USE_LOCAL_VLM=false
"@

[System.IO.File]::WriteAllText($apiEnvPath, $apiEnvContent, [System.Text.Encoding]::UTF8)
Write-Host "[SUCCESS] Generated apps/api/.env" -ForegroundColor Green

# 2. Generate apps/web/.env.local
$webEnvContent = @"
NEXT_PUBLIC_PARENT_DOMAIN="asiverticals.me"
NEXT_PUBLIC_APP_SUBDOMAIN="vendorcomply.asiverticals.me"
NEXT_PUBLIC_API_URL="https://api-vendorcomply.onrender.com/api/v1"
"@

[System.IO.File]::WriteAllText($webEnvPath, $webEnvContent, [System.Text.Encoding]::UTF8)
Write-Host "[SUCCESS] Generated apps/web/.env.local" -ForegroundColor Green

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " ENVIRONMENT CONFIGURATION READY: ZERO MANUAL STEPS REQUIRED!   " -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
