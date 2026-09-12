// apps/web/components/dashboard/kpi-row.tsx
"use client";

import React from "react";
import { AlertTriangle, ShieldCheck, TrendingUp, Clock } from "lucide-react";
import { formatINR } from "@/lib/utils";

export interface KPIData {
  totalAtRiskPayables: number;
  atRiskVendorCount: number;
  potentialTaxDisallowance: number;
  corporateTaxRatePercent: number;
  accruedPenalInterest: number;
  complianceHealthScore: number;
}

export function KPIRow({ data }: { data: KPIData }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Card 1: At-Risk MSME Payables */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            At-Risk MSME Payables
          </span>
          <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
            <Clock className="w-5 h-5" />
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

      {/* Card 2: 43B(h) Corporate Tax Disallowance Exposure */}
      <div className="bg-white p-5 rounded-xl border border-rose-200 shadow-sm flex flex-col justify-between relative overflow-hidden">
        <div className="absolute top-0 right-0 w-2 h-full bg-rose-500" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-700">
            Imminent Tax Disallowance
          </span>
          <div className="p-2 bg-rose-50 rounded-lg text-rose-600">
            <AlertTriangle className="w-5 h-5" />
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

      {/* Card 3: Accrued Section 16 Penal Interest */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Accrued Penal Interest
          </span>
          <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
            <TrendingUp className="w-5 h-5" />
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
            <ShieldCheck className="w-5 h-5" />
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
