// apps/web/components/payouts/working-capital-card.tsx
"use client";

import React, { useState } from "react";
import { Landmark, ArrowRight, ShieldCheck } from "lucide-react";
import { formatINR } from "@/lib/utils";

export function WorkingCapitalFinancingCard({
  batchAmount,
}: {
  batchAmount: number;
}) {
  const [submitted, setSubmitted] = useState(false);

  const handleApply = () => {
    setSubmitted(true);
  };

  return (
    <div className="mt-6 p-5 bg-gradient-to-r from-blue-50/70 to-indigo-50/70 border border-blue-200 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div className="flex items-start gap-3.5">
        <div className="p-2.5 bg-blue-600 text-white rounded-xl shadow-sm shrink-0">
          <Landmark className="w-5 h-5" />
        </div>
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-blue-900 flex items-center gap-1.5">
            <span>Instant MSME Vendor Financing (TReDS / Partner Credit)</span>
            <span className="px-1.5 py-0.2 rounded text-[10px] bg-blue-200 text-blue-800">
              Prime Rates
            </span>
          </div>
          <p className="text-xs text-blue-800 mt-1 max-w-xl">
            Short of working capital to clear this {formatINR(batchAmount)} batch? Disburse funds
            within 48 hours through partner TReDS rails at prime corporate rates (8.5%–10.5% p.a.) and protect
            statutory 43B(h) compliance.
          </p>
        </div>
      </div>

      <button
        onClick={handleApply}
        disabled={submitted}
        className="px-4 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors shadow-sm shrink-0 flex items-center gap-1.5 disabled:bg-emerald-600"
      >
        {submitted ? (
          <>
            <ShieldCheck className="w-4 h-4" /> Desk Contacted
          </>
        ) : (
          <>
            Apply for Batch Credit <ArrowRight className="w-3.5 h-3.5" />
          </>
        )}
      </button>
    </div>
  );
}
