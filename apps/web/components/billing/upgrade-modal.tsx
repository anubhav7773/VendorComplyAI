// apps/web/components/billing/upgrade-modal.tsx
"use client";

import React from "react";
import Link from "next/link";
import { Check, ShieldCheck, Zap, X } from "lucide-react";
import { formatINR } from "@/lib/utils";

export function UpgradeModal({
  isOpen,
  onClose,
  detectedTaxRiskAmount,
}: {
  isOpen: boolean;
  onClose: () => void;
  detectedTaxRiskAmount: number;
}) {
  if (!isOpen) return null;

  const annualSubscription = 78000;
  const roiMultiplier = (detectedTaxRiskAmount / annualSubscription).toFixed(1);

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
            <Zap className="w-5 h-5 text-emerald-600" />
            Upgrade to VendorComply Growth Tier
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* The Direct Financial ROI Anchor */}
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mt-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-800">
              Tax Disallowance Exposure in Your Books
            </span>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
              {roiMultiplier}x Direct ROI
            </span>
          </div>
          <div className="text-2xl font-black font-mono text-emerald-950 mt-1">
            {formatINR(detectedTaxRiskAmount)}
          </div>
          <p className="text-xs text-emerald-700 mt-1">
            A single Section 43B(h) disallowance freezes more working capital than the entire annual
            subscription fee of VendorComply AI.
          </p>
        </div>

        {/* Feature Comparison Highlights */}
        <div className="mt-5 space-y-2.5 text-xs text-slate-700">
          {[
            "1-Click ICICI CIB & HDFC ENet Connected Banking CSV File Generators",
            "Up to 1,000 Purchase Invoices Processed per month",
            "Full Form 3CD Clause 22 Tax Audit Certified Excel Annexure Package",
            "Automated Monday Morning WhatsApp OTP & Alerts for Promoter / CFO",
            "Support for up to 3 Corporate GSTINs under the same PAN",
          ].map((item, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <div className="p-0.5 rounded-full bg-emerald-100 text-emerald-700">
                <Check className="w-3.5 h-3.5" />
              </div>
              <span>{item}</span>
            </div>
          ))}
        </div>

        {/* Pricing Card */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mt-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Growth Plan (Billed Annually)
            </div>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-2xl font-extrabold text-slate-900 font-mono">₹6,500</span>
              <span className="text-xs text-slate-500">/ month (₹78,000 + GST / year)</span>
            </div>
          </div>
          <Link
            href="/settings/billing"
            className="px-5 py-2.5 rounded-xl font-bold text-xs bg-emerald-600 hover:bg-emerald-700 text-white transition-all shadow-md flex items-center gap-1.5"
          >
            <ShieldCheck className="w-4 h-4" />
            Upgrade Now
          </Link>
        </div>

        <div className="text-center mt-3 text-[11px] text-slate-400">
          Official B2B Tax Invoice with GST input credit automatically issued by asiverticals.me
        </div>
      </div>
    </div>
  );
}
