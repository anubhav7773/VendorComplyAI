// apps/web/components/payouts/batch-release-modal.tsx
"use client";

import React, { useState } from "react";
import { ShieldCheck, Download, X } from "lucide-react";
import { formatINR } from "@/lib/utils";

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
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            Maker-Checker Payout Authorization
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
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
            <Download className="w-4 h-4" />
            {loading ? "Sealing SHA-256..." : "Authorize & Export CSV"}
          </button>
        </div>
      </div>
    </div>
  );
}
