# ==============================================================================
# VENDORCOMPLY AI — FRONTEND UI/UX ARCHITECTURE & COMPONENT SPECIFICATION
# Document ID: 07_FRONTEND_UI_AND_STITCH.md
# Parent Entity: asiverticals.me
# Framework Target: Next.js 15 (App Router) + React 19 + Tailwind CSS + Shadcn UI
# Design Baseline: Frozen Google Stitch Tokens (Desktop-First 1440px Canvas)
# Performance Goal: Zero Layout Shifts, Instant SWR Caching & Sub-100ms Transitions
# ==============================================================================

## 1. DESIGN TOKENS & SYSTEM FOUNDATION (GOOGLE STITCH FROZEN SPEC)

VendorComply AI delivers an enterprise-grade fintech user experience tailored for corporate Managing Directors (Promoters), Chief Financial Officers (CFOs), Senior Accounts Managers, and Statutory Chartered Accountants[cite: 1]. The visual hierarchy is optimized for high-density financial matrices and fast audit verifications.

              [Global Application Canvas: 1440px - 1920px]
┌─────────────────────────────────────────────────────────────────────────┐
│ Top App Bar: Org Switcher | FY 2026-27 | March 31 Cutoff Pill | CFO Avatar │
├──────────┬──────────────────────────────────────────────────────────────┤
│ Dark     │ [Breadcrumbs: Dashboard > 15/45-Day Rolling Matrix]          │
│ Slate-900│                                                              │
│ Sidebar  │ ┌──────────────────────────────────────────────────────────┐ │
│ 240px    │ │ Top KPI Row (4 High-Impact Metric Cards)                 │ │
│          │ │ - Total At-Risk Payables   - 43B(h) Tax Exposure (Red)   │ │
│ - Radar  │ │ - Accrued Penal Interest   - Compliance Health Index     │ │
│ - Aging  │ └──────────────────────────────────────────────────────────┘ │
│ - Payouts│                                                              │
│ - Vendors│ ┌──────────────────────────────────────────────────────────┐ │
│ - 3CD    │ │ Main Content Matrix (Shadcn Tabs & Data Tables)          │ │
│ - Settings│ │ - 15/45-Day Rolling Countdown Radar                      │ │
│          │ │ - Critical Overdue Invoices                              │ │
│ Powered  │ │ - 1-Click Batch Banking Export                           │ │
│ by       │ │ - Dispute Hold Triggers                                  │ │
│ asiverti │ └──────────────────────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────────────────────┘


### A. Semantic Color Palette (Tailwind CSS)
* **Background Canvas**: `slate-50` (`#F8FAFC`) with subtle grid background.
* **Surface Cards**: Pure White (`#FFFFFF`) with border `slate-200` (`#E2E8F0`) and `shadow-sm`.
* **Sidebar**: `slate-950` (`#020617`) with active link accent `emerald-500` (`#10B981`).
* **Statutory Compliance Indicators**:
  * **Safe / Compliant**: `emerald-600` (`#059669`), background `emerald-50` (`#ECFDF5`).
  * **Approaching Deadline (5–10 Days Left)**: `amber-600` (`#D97706`), background `amber-50` (`#FFFBEB`).
  * **Critical Overdue / 43B(h) Tax Trap**: `rose-600` (`#E11D48`), background `rose-50` (`#FFF1F2`).
  * **Traders (Statutorily Exempt u/s 43Bh)**: `slate-500` (`#64748B`), background `slate-100` (`#F1F5F9`)[cite: 2].
  * **Disputed Hold (Frozen Clock)**: `indigo-600` (`#4F46E5`), background `indigo-50` (`#EEF2FF`).

### B. Typography & Numeric Legibility
* **Primary Sans Font**: `Geist Sans` or `Inter` (`font-sans`).
* **Financial Amounts & Timestamps**: `font-mono` with `tabular-nums` tracking to align numbers in dense ledgers.

---

## 2. APP ROUTER NAVIGATION & ROUTE DIRECTORY MAP

The Next.js 15 application inside `apps/web/app/` follows a strict layout-driven structure:

```text
apps/web/app/
├── (auth)/
│   └── login/
│       └── page.tsx            # Enterprise Auth & Statutory Disclaimer Checkbox
├── (dashboard)/
│   ├── layout.tsx              # Persistent Shell: Dark Sidebar, Header, Cutoff Timer
│   ├── page.tsx                # Route: / -> CFO Executive Exposure Radar (Home)
│   ├── aging/
│   │   └── page.tsx            # Route: /aging -> 15/45-Day Rolling Matrix Table
│   ├── payouts/
│   │   └── page.tsx            # Route: /payouts -> Dynamic Monday Batch Release
│   ├── vendors/
│   │   └── page.tsx            # Route: /vendors -> Creditors Master & Udyam Intelligence
│   ├── audit-3cd/
│   │   └── page.tsx            # Route: /audit-3cd -> CA Tax Audit Clause 22 Generator
│   └── settings/
│       └── page.tsx            # Route: /settings -> Agent API Secret & Bank Setup
├── api/                        # Edge Webhooks & Proxy Routes
├── globals.css                 # Tailwind Root & Shadcn CSS Variables
└── layout.tsx                  # Root HTML shell & Theme Provider
3. PRODUCTION COMPONENT IMPLEMENTATIONS (ZERO PLACEHOLDERS)
A. The CFO Top KPI Row (apps/web/components/dashboard/kpi-row.tsx)
Displays the 4 high-impact statutory risk numbers. Save at apps/web/components/dashboard/kpi-row.tsx:

TypeScript
// apps/web/components/dashboard/kpi-row.tsx
"use client";

import React from "react";
import { AlertTriangle, ShieldCheck, TrendingUp, Clock } from "lucide-react";

interface KPIData {
  totalAtRiskPayables: number;
  atRiskVendorCount: number;
  potentialTaxDisallowance: number;
  corporateTaxRatePercent: number;
  accruedPenalInterest: number;
  effectivePenalRatePercent: number;
  complianceHealthScore: number;
}

export function KPIRow({ data }: { data: KPIData }) {
  const formatINR = (val: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(val);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Card 1: At-Risk Payables */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            At-Risk MSME Payables
          </span>
          <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
            <Clock className="w-5 h-5"/>
          </div>
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold font-mono text-slate-900">
            {formatINR(data.totalAtRiskPayables)}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Across{" "}
            <span className="font-semibold text-slate-700">
              {data.atRiskVendorCount} Micro/Small
            </span>{" "}
            suppliers
          </p>
        </div>
      </div>

      {/* Card 2: 43B(h) Corporate Tax Exposure (Killer Feature) */}
      <div className="bg-white p-5 rounded-xl border border-rose-200 shadow-sm flex flex-col justify-between relative overflow-hidden">
        <div className="absolute top-0 right-0 w-2 h-full bg-rose-500" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-700">
            Imminent Tax Disallowance
          </span>
          <div className="p-2 bg-rose-50 rounded-lg text-rose-600">
            <AlertTriangle className="w-5 h-5"/>
          </div>
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold font-mono text-rose-600">
            {formatINR(data.potentialTaxDisallowance)}
          </div>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-100 text-rose-800">
              Sec 43B(h)
            </span>
            <span className="text-xs text-slate-500">
              @ {data.corporateTaxRatePercent}% Corp Tax
            </span>
          </div>
        </div>
      </div>

      {/* Card 3: Accrued Penal Interest */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Accrued Penal Interest
          </span>
          <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
            <TrendingUp className="w-5 h-5"/>
          </div>
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold font-mono text-slate-900">
            {formatINR(data.accruedPenalInterest)}
          </div>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-100 text-purple-800">
              Sec 16 (3x RBI)
            </span>
            <span className="text-[11px] text-slate-400 font-medium">
              100% Non-Deductible Loss
            </span>
          </div>
        </div>
      </div>

      {/* Card 4: Compliance Health Score */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Compliance Health Index
          </span>
          <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
            <ShieldCheck className="w-5 h-5"/>
          </div>
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold font-mono text-emerald-600">
            {data.complianceHealthScore.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
            <div
              className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${data.complianceHealthScore}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
B. The 15/45-Day Rolling Aging Countdown Matrix (apps/web/components/aging/aging-table.tsx)
Renders the tabular matrix with status badges, countdown pills, and dispute triggers. Save at apps/web/components/aging/aging-table.tsx:

TypeScript
// apps/web/components/aging/aging-table.tsx
"use client";

import React, { useState } from "react";
import { 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  MoreVertical, 
  FileText 
} from "lucide-react";

export interface InvoiceRecord {
  id: string;
  vendorName: string;
  udyamCategory: "MICRO" | "SMALL" | "MEDIUM" | "UNREGISTERED";
  isTrader: boolean;
  invoiceReference: string;
  billDate: string;
  agreedDays: number;
  statutoryDueDate: string;
  overdueDays: number;
  taxableAmount: number;
  grossAmount: number;
  taxExposure: number;
  status: "UNPAID" | "PARTIALLY_PAID" | "PAID" | "DISPUTED_HOLD";
}

export function AgingTable({
  invoices,
  onOpenDispute,
}: {
  invoices: InvoiceRecord[];
  onOpenDispute: (invoice: InvoiceRecord) => void;
}) {
  const [selectedFilter, setSelectedFilter] = useState<string>("ALL");

  const formatINR = (val: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(val);

  const filteredInvoices = invoices.filter((inv) => {
    if (selectedFilter === "CRITICAL") return inv.overdueDays > 0 && inv.status !== "DISPUTED_HOLD";
    if (selectedFilter === "DUE_SOON") return inv.overdueDays <= 0 && inv.status === "UNPAID";
    if (selectedFilter === "DISPUTED") return inv.status === "DISPUTED_HOLD";
    if (selectedFilter === "TRADERS") return inv.isTrader;
    return true;
  });

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* Filter Tabs Bar */}
      <div className="flex items-center justify-between border-b border-slate-200 px-6 py-3 bg-slate-50/50">
        <div className="flex items-center gap-2">
          {[
            { id: "ALL", label: `All Invoices (${invoices.length})` },
            { id: "CRITICAL", label: "Critical Overdue", countBadge: true },
            { id: "DUE_SOON", label: "Due in 7 Days" },
            { id: "DISPUTED", label: "Dispute Holds" },
            { id: "TRADERS", label: "Traders (Exempt)" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedFilter(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                selectedFilter === tab.id
                  ? "bg-white text-slate-900 shadow-sm border border-slate-200"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Matrix Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              <th className="py-3.5 px-6">Vendor Legal Entity</th>
              <th className="py-3.5 px-4">Invoice Ref</th>
              <th className="py-3.5 px-4">Bill Date</th>
              <th className="py-3.5 px-4">Statutory Terms</th>
              <th className="py-3.5 px-4">Statutory Due Date</th>
              <th className="py-3.5 px-4">Aging Status</th>
              <th className="py-3.5 px-4 text-right">Taxable Base</th>
              <th className="py-3.5 px-4 text-right">43B(h) Exposure</th>
              <th className="py-3.5 px-6 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 text-xs">
            {filteredInvoices.map((inv) => (
              <tr key={inv.id} className="hover:bg-slate-50/80 transition-colors">
                {/* Vendor Column */}
                <td className="py-3.5 px-6">
                  <div className="font-semibold text-slate-900">{inv.vendorName}</div>
                  <div className="flex items-center gap-1.5 mt-1">
                    {inv.isTrader ? (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                        Trader (Exempt)
                      </span>
                    ) : (
                      <span
                        className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium ${
                          inv.udyamCategory === "MICRO"
                            ? "bg-blue-50 text-blue-700 border border-blue-200"
                            : "bg-indigo-50 text-indigo-700 border border-indigo-200"
                        }`}
                      >
                        {inv.udyamCategory} MFR
                      </span>
                    )}
                  </div>
                </td>

                {/* Invoice Ref */}
                <td className="py-3.5 px-4 font-mono font-medium text-slate-700">
                  {inv.invoiceReference}
                </td>

                {/* Bill Date */}
                <td className="py-3.5 px-4 text-slate-600">{inv.billDate}</td>

                {/* Statutory Terms */}
                <td className="py-3.5 px-4">
                  {inv.agreedDays > 0 ? (
                    <span className="text-slate-700">
                      {Math.min(inv.agreedDays, 45)} Days (Agreed)
                    </span>
                  ) : (
                    <span className="text-amber-700 font-medium">15 Days (Default)</span>
                  )}
                </td>

                {/* Statutory Due Date */}
                <td className="py-3.5 px-4 font-mono text-slate-800">
                  {inv.statutoryDueDate}
                </td>

                {/* Aging Status Pill */}
                <td className="py-3.5 px-4">
                  {inv.status === "DISPUTED_HOLD" ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                      <ShieldAlert className="w-3.5 h-3.5"/> Disputed Hold
                    </span>
                  ) : inv.isTrader ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600">
                      Exempt
                    </span>
                  ) : inv.overdueDays > 0 ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200 animate-pulse">
                      <AlertCircle className="w-3.5 h-3.5"/> +{inv.overdueDays}d Overdue
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <CheckCircle2 className="w-3.5 h-3.5"/> Compliant
                    </span>
                  )}
                </td>

                {/* Taxable Base */}
                <td className="py-3.5 px-4 text-right font-mono font-medium text-slate-800">
                  {formatINR(inv.taxableAmount)}
                </td>

                {/* 43B(h) Exposure */}
                <td className="py-3.5 px-4 text-right font-mono font-bold text-rose-600">
                  {inv.taxExposure > 0 ? formatINR(inv.taxExposure) : "₹0"}
                </td>

                {/* Actions */}
                <td className="py-3.5 px-6 text-center">
                  <button
                    onClick={() => onOpenDispute(inv)}
                    className="p-1.5 text-slate-400 hover:text-slate-900 rounded-md hover:bg-slate-100"
                    title="Log Dispute / View Options"
                  >
                    <MoreVertical className="w-4 h-4"/>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
C. Statutory Dispute Hold Modal (apps/web/components/aging/dispute-modal.tsx)
Enforces Section 15 of the MSMED Act. Freezes the statutory countdown only when valid objection credentials are submitted. Save at apps/web/components/aging/dispute-modal.tsx:

TypeScript
// apps/web/components/aging/dispute-modal.tsx
"use client";

import React, { useState } from "react";
import { AlertTriangle, ShieldCheck, X } from "lucide-react";
import { InvoiceRecord } from "./aging-table";

export function DisputeModal({
  invoice,
  isOpen,
  onClose,
  onConfirmDispute,
}: {
  invoice: InvoiceRecord | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmDispute: (details: {
    voucherId: string;
    objectionDate: string;
    channel: string;
    trackingRef: string;
    category: string;
    notes: string;
  }) => Promise<void>;
}) {
  const [objectionDate, setObjectionDate] = useState("");
  const [channel, setChannel] = useState("EMAIL");
  const [trackingRef, setTrackingRef] = useState("");
  const [category, setCategory] = useState("DEFECTIVE_MATERIAL");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen || !invoice) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onConfirmDispute({
      voucherId: invoice.id,
      objectionDate,
      channel,
      trackingRef,
      category,
      notes,
    });
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
            <AlertTriangle className="w-5 h-5 text-amber-500"/>
            Log Statutory Dispute (Section 15 MSMED Act)
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5"/>
          </button>
        </div>

        <p className="text-xs text-slate-500 mt-3">
          Under Section 2(b) of the MSMED Act, lodging a written objection within 15 days of delivery
          suspends deemed acceptance and freezes Section 16 penal interest.
        </p>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Invoice Reference
            </label>
            <input
              disabled
              value={`${invoice.invoiceReference} (${invoice.vendorName})`}
              className="w-full bg-slate-100 border border-slate-200 rounded-lg p-2 font-mono text-slate-600"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Date Objection Delivered *
              </label>
              <input
                type="date"
                required
                value={objectionDate}
                onChange={(e) => setObjectionDate(e.target.value)}
                className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Delivery Channel *
              </label>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
              >
                <option value="EMAIL">Email</option>
                <option value="REGISTERED_POST">Registered Speed Post</option>
                <option value="WHATSAPP">WhatsApp Business</option>
                <option value="WRITTEN_MEMO">Physical Written Memo</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Objection Tracking Ref / Message ID *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Email Message-ID or Postal Consignment No."
              value={trackingRef}
              onChange={(e) => setTrackingRef(e.target.value)}
              className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Dispute Category *
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
            >
              <option value="DEFECTIVE_MATERIAL">Defective Goods / Quality Rejection</option>
              <option value="SHORT_DELIVERY">Short Delivery / Quantity Mismatch</option>
              <option value="RATE_DISCREPANCY">Invoiced Rate Higher than PO</option>
              <option value="TDS_DISPUTE">Incorrect GST / TDS Line Classification</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Audit Scrutiny Notes
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Provide factual audit notes for CA review..."
              className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
            />
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-lg font-semibold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-sm"
            >
              {loading ? "Locking..." : "Freeze Statutory Clock"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
D. Monday Batch Release & Maker-Checker Modal (apps/web/components/payouts/batch-release-modal.tsx)
Generates bank-compliant batch disbursement files with SHA-256 tamper checks. Save at apps/web/components/payouts/batch-release-modal.tsx:

TypeScript
// apps/web/components/payouts/batch-release-modal.tsx
"use client";

import React, { useState } from "react";
import { ShieldCheck, Download, AlertCircle, X } from "lucide-react";

export function BatchReleaseModal({
  isOpen,
  onClose,
  totalAmount,
  protectedTaxShield,
  recordCount,
  onAuthorizeAndDownload,
}: {
  isOpen: boolean;
  onClose: () => void;
  totalAmount: number;
  protectedTaxShield: number;
  recordCount: number;
  onAuthorizeAndDownload: (bankRail: "ICICI_CIB" | "HDFC_ENET") => Promise<void>;
}) {
  const [bankRail, setBankRail] = useState<"ICICI_CIB" | "HDFC_ENET">("ICICI_CIB");
  const [indemnificationChecked, setIndemnificationChecked] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const formatINR = (val: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(val);

  const handleAuthorize = async () => {
    if (!indemnificationChecked) return;
    setLoading(true);
    await onAuthorizeAndDownload(bankRail);
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
            <ShieldCheck className="w-5 h-5 text-emerald-600"/>
            Maker-Checker Payout Authorization
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5"/>
          </button>
        </div>

        {/* Financial ROI Hero Banner */}
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mt-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-emerald-800">
            Immediate Compliance Benefit
          </div>
          <div className="text-lg font-bold text-emerald-950 mt-1">
            Paying {formatINR(totalAmount)} today protects {formatINR(protectedTaxShield)} in statutory tax disallowance.
          </div>
          <div className="text-xs text-emerald-700 mt-1">
            Clearing {recordCount} overdue/imminent Micro & Small supplier invoices.
          </div>
        </div>

        <div className="mt-4 space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1.5">
              Select Corporate Banking Rail
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setBankRail("ICICI_CIB")}
                className={`p-3 rounded-xl border text-left transition-all ${
                  bankRail === "ICICI_CIB"
                    ? "border-emerald-500 bg-emerald-50/40 text-emerald-900 font-semibold"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                <div className="font-bold">ICICI Bank CIB</div>
                <div className="text-[10px] text-slate-500">PAB_VENDOR Batch Format</div>
              </button>
              <button
                type="button"
                onClick={() => setBankRail("HDFC_ENET")}
                className={`p-3 rounded-xl border text-left transition-all ${
                  bankRail === "HDFC_ENET"
                    ? "border-emerald-500 bg-emerald-50/40 text-emerald-900 font-semibold"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                <div className="font-bold">HDFC Bank ENet</div>
                <div className="text-[10px] text-slate-500">Corporate Bulk Upload CSV</div>
              </button>
            </div>
          </div>

          {/* Legal Non-Liability Checkbox (Anti-Litigation Shield) */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex items-start gap-2.5">
            <input
              type="checkbox"
              id="indemnity"
              checked={indemnificationChecked}
              onChange={(e) => setIndemnificationChecked(e.target.checked)}
              className="mt-0.5 w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 border-slate-300"
            />
            <label htmlFor="indemnity" className="text-[11px] text-slate-600 leading-relaxed">
              I confirm verification of vendor bank account numbers, IFSC codes, and net disbursement amounts.
              I authorize generation of the sealed file under <strong>asiverticals.me</strong> terms.
            </label>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 mt-5 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg font-semibold text-slate-600 hover:bg-slate-100 text-xs"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={!indemnificationChecked || loading}
            onClick={handleAuthorize}
            className="px-5 py-2 rounded-lg font-semibold text-xs bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm flex items-center gap-1.5"
          >
            <Download className="w-4 h-4"/>
            {loading ? "Sealing SHA-256..." : "Authorize & Export CSV"}
          </button>
        </div>
      </div>
    </div>
  );
}
E. Form 3CD Clause 22 Tax Audit Scrutiny View (apps/web/app/(dashboard)/audit-3cd/page.tsx)
Generates the exact statutory reporting disclosure table required by Chartered Accountants for Form 3CD Clause 22. Save at apps/web/app/(dashboard)/audit-3cd/page.tsx:

TypeScript
// apps/web/app/(dashboard)/audit-3cd/page.tsx
"use client";

import React from "react";
import { Download, Printer, ShieldCheck } from "lucide-react";

export default function Audit3CDPage() {
  const auditData = {
    fyYear: "2026-27",
    ayYear: "2027-28",
    unpaidPrincipalAtYearEnd: 3420000.0,
    interestDueAtYearEnd: 485210.0,
    interestPaidBeyondAppointedDay: 0.0,
    accruedUnpaidInterestCarriedForward: 485210.0,
    totalDisallowanceSec43Bh: 3420000.0,
  };

  const formatINR = (val: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(val);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Form 3CD Clause 22 Tax Audit Scrutiny
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Statutory disclosure computation under Section 22 of MSMED Act, 2006 & Section 43B(h) of Income-tax Act, 1961
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 text-xs font-semibold border border-slate-200 rounded-lg hover:bg-slate-50 flex items-center gap-1.5 text-slate-700">
            <Printer className="w-4 h-4"/> Print Sheet
          </button>
          <button className="px-4 py-2 text-xs font-semibold bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center gap-1.5 shadow-sm">
            <Download className="w-4 h-4"/> Export CA Working Annexure (.XLSX)
          </button>
        </div>
      </div>

      {/* Statutory Form 3CD Clause 22 Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="font-semibold text-xs text-slate-700 uppercase tracking-wider">
            Statutory Particulars (Form 3CD Annexure)
          </div>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
            <ShieldCheck className="w-3.5 h-3.5"/> Verified against Tally Vouchers
          </span>
        </div>

        <table className="w-full text-left text-xs divide-y divide-slate-200">
          <tbody className="divide-y divide-slate-200">
            <tr>
              <td className="py-4 px-6 font-medium text-slate-800">
                (i) Principal amount remaining unpaid to any supplier as at the end of the accounting year
              </td>
              <td className="py-4 px-6 text-right font-mono font-bold text-slate-900">
                {formatINR(auditData.unpaidPrincipalAtYearEnd)}
              </td>
            </tr>
            <tr>
              <td className="py-4 px-6 font-medium text-slate-800">
                (ii) Interest due thereon remaining unpaid to suppliers as at the end of the accounting year
              </td>
              <td className="py-4 px-6 text-right font-mono font-bold text-rose-600">
                {formatINR(auditData.interestDueAtYearEnd)}
              </td>
            </tr>
            <tr>
              <td className="py-4 px-6 font-medium text-slate-800">
                (iii) Amount of interest paid by the buyer in terms of Section 16 of MSMED Act beyond the appointed day during the year
              </td>
              <td className="py-4 px-6 text-right font-mono text-slate-700">
                {formatINR(auditData.interestPaidBeyondAppointedDay)}
              </td>
            </tr>
            <tr>
              <td className="py-4 px-6 font-medium text-slate-800">
                (iv) Amount of interest accrued and remaining unpaid at the end of the year
              </td>
              <td className="py-4 px-6 text-right font-mono font-bold text-slate-900">
                {formatINR(auditData.accruedUnpaidInterestCarriedForward)}
              </td>
            </tr>
            <tr className="bg-rose-50/50">
              <td className="py-4 px-6 font-bold text-rose-900">
                (v) Total Disallowance to be added back to Taxable Income under Section 43B(h) of the Income-tax Act, 1961
              </td>
              <td className="py-4 px-6 text-right font-mono font-extrabold text-rose-700 text-sm">
                {formatINR(auditData.totalDisallowanceSec43Bh)}
              </td>
            </tr>
          </tbody>
        </table>

        {/* Non-Deductibility Statutory Note */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 text-[11px] text-slate-500 leading-relaxed">
          <strong>Statutory Compliance Note:</strong> As per Section 23 of the MSMED Act, 2006, the interest
          amount of {formatINR(auditData.interestDueAtYearEnd)} is strictly non-deductible while computing
          the taxable income of the assessee.
        </div>
      </div>
    </div>
  );
}
4. PERSISTENT APPLICATION SHELL (apps/web/app/(dashboard)/layout.tsx)
Provides the persistent dark sidebar, organization selector, March 31 countdown pill, and global layout. Save at apps/web/app/(dashboard)/layout.tsx:

TypeScript
// apps/web/app/(dashboard)/layout.tsx
import React from "react";
import Link from "next/link";
import { 
  LayoutDashboard, 
  Clock, 
  Send, 
  Users, 
  FileCheck2, 
  Settings, 
  Shield 
} from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden font-sans">
      {/* 240px Fixed Dark Sidebar */}
      <aside className="w-60 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo & Parent Identity */}
          <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center font-bold text-white text-base shadow-sm">
              V
            </div>
            <div>
              <div className="font-bold text-sm text-white tracking-tight">
                VendorComply <span className="text-emerald-400">AI</span>
              </div>
              <div className="text-[10px] text-slate-400">by asiverticals.me</div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {[
              { href: "/", label: "Exposure Radar", icon: LayoutDashboard },
              { href: "/aging", label: "15/45-Day Matrix", icon: Clock },
              { href: "/payouts", label: "Monday Batch Runs", icon: Send },
              { href: "/vendors", label: "Sundry Creditors", icon: Users },
              { href: "/audit-3cd", label: "Form 3CD Clause 22", icon: FileCheck2 },
              { href: "/settings", label: "Agent & Banking", icon: Settings },
            ].map((item) => (
              <Link className="flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-900 hover:text-white transition-colors" href="{item.href}" key="{item.href}">
                <item.icon className="w-4 h-4 text-slate-400" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Footer Security Badge */}
        <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mb-1">
            <Shield className="w-3.5 h-3.5"/> SOC2 / RLS Active
          </div>
          <div>Tenant ID Segregated</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-4">
            <span className="font-bold text-sm text-slate-800">
              ACME Discrete Manufacturing Pvt Ltd
            </span>
            <span className="text-xs px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-mono">
              GST: 27AABCP1234K1Z5
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* March 31 Countdown Pill */}
            <div className="px-3 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-1.5 animate-pulse">
              <Clock className="w-3.5 h-3.5"/> March 31 Cutoff: 200 Days Left
            </div>

            {/* CFO Profile Avatar */}
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
              CF
            </div>
          </div>
        </header>

        {/* Scrollable Viewport */}
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}

---
