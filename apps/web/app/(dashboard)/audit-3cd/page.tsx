"use client";

import React, { useState } from "react";
import { Printer, ShieldCheck, FileSpreadsheet } from "lucide-react";
import { formatINR } from "@/lib/utils";
import { UpgradeModal } from "@/components/billing/upgrade-modal";

export default function Audit3CDPage() {
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);

  const auditData = {
    fyYear: "2026-27",
    ayYear: "2027-28",
    unpaidPrincipalAtYearEnd: 3420000.0,
    interestDueAtYearEnd: 485210.0,
    interestPaidBeyondAppointedDay: 0.0,
    accruedUnpaidInterestCarriedForward: 485210.0,
    totalDisallowanceSec43Bh: 3420000.0,
  };

  const handleExportClick = () => {
    // Gated for Growth / Enterprise tier
    setIsUpgradeModalOpen(true);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Form 3CD Clause 22 Tax Audit Scrutiny Portal
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Statutory disclosure computation under Section 22 of MSMED Act, 2006 & Section 43B(h) of Income-tax Act, 1961
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="px-4 py-2 text-xs font-semibold border border-slate-200 rounded-lg hover:bg-slate-50 flex items-center gap-1.5 text-slate-700"
          >
            <Printer className="w-4 h-4" /> Print Sheet
          </button>
          <button
            onClick={handleExportClick}
            className="px-4 py-2 text-xs font-semibold bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center gap-1.5 shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4" /> Export CA Working Annexure (.XLSX)
          </button>
        </div>
      </div>

      {/* Statutory Form 3CD Clause 22 Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="font-semibold text-xs text-slate-700 uppercase tracking-wider">
            Statutory Particulars (Form 3CD Clause 22 Annexure)
          </div>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
            <ShieldCheck className="w-3.5 h-3.5" /> Verified against Tally Vouchers
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
          the taxable income of the assessee (0% Tax Shield).
        </div>
      </div>

      {/* Upgrade Paywall Modal */}
      <UpgradeModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
        detectedTaxRiskAmount={auditData.totalDisallowanceSec43Bh * 0.2517}
      />
    </div>
  );
}
