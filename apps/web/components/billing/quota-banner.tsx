// apps/web/components/billing/quota-banner.tsx
"use client";

import React from "react";
import Link from "next/link";
import { Zap } from "lucide-react";

export function QuotaBanner({
  processedCount,
  quotaLimit,
  tierName,
}: {
  processedCount: number;
  quotaLimit: number;
  tierName: string;
}) {
  const percentage = Math.min(100, Math.round((processedCount / quotaLimit) * 100));
  const isNearLimit = percentage >= 80;

  if (!isNearLimit && tierName !== "EVALUATION_TRIAL") return null;

  return (
    <div className="mb-6 p-4 bg-gradient-to-r from-slate-900 to-slate-950 text-white rounded-xl shadow-md border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          <Zap className="w-5 h-5" />
        </div>
        <div>
          <div className="text-xs font-semibold text-slate-200">
            Monthly Ingestion Quota:{" "}
            <span className="text-emerald-400 font-mono font-bold">
              {processedCount} / {quotaLimit} Bills
            </span>{" "}
            ({percentage}%)
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">
            {isNearLimit
              ? "You are nearing your plan limit. Upgrade to Growth Tier to prevent sync interruption."
              : "You are currently running the 30-Day Free Evaluation Pilot."}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <div className="w-32 bg-slate-800 rounded-full h-2 overflow-hidden hidden sm:block">
          <div
            className={`h-2 rounded-full transition-all ${
              percentage > 90 ? "bg-rose-500" : "bg-emerald-500"
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <Link
          href="/settings/billing"
          className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-colors shadow-sm"
        >
          Upgrade Plan
        </Link>
      </div>
    </div>
  );
}
