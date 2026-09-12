// apps/web/app/(dashboard)/payouts/page.tsx
"use client";

import React, { useState } from "react";
import { Send, CheckCircle2, ShieldAlert } from "lucide-react";
import { formatINR } from "@/lib/utils";
import { BatchReleaseModal } from "@/components/payouts/batch-release-modal";
import { WorkingCapitalFinancingCard } from "@/components/payouts/working-capital-card";

interface PayoutCandidate {
  id: string;
  vendorName: string;
  invoiceReference: string;
  bankAccountMasked: string;
  ifsc: string;
  amount: number;
  statutoryDueDate: string;
  taxProtected: number;
}

export default function PayoutsPage() {
  const [candidates] = useState<PayoutCandidate[]>([
    {
      id: "pay-1",
      vendorName: "Precision Components Ltd",
      invoiceReference: "INV/2026/0891",
      bankAccountMasked: "••••••••5621",
      ifsc: "SBIN0001234",
      amount: 500000,
      statutoryDueDate: "2026-09-09",
      taxProtected: 106644,
    },
    {
      id: "pay-2",
      vendorName: "BioTech Solutions LLP",
      invoiceReference: "BTS/2026/401",
      bankAccountMasked: "••••••••9843",
      ifsc: "HDFC0000240",
      amount: 850000,
      statutoryDueDate: "2026-09-09",
      taxProtected: 181294,
    },
    {
      id: "pay-3",
      vendorName: "Super Plast Polymers",
      invoiceReference: "SPP-9921",
      bankAccountMasked: "••••••••1102",
      ifsc: "ICIC0000007",
      amount: 1130000,
      statutoryDueDate: "2026-09-14",
      taxProtected: 241088,
    },
  ]);

  const [selectedIds, setSelectedIds] = useState<string[]>([
    "pay-1",
    "pay-2",
    "pay-3",
  ]);
  const [isReleaseModalOpen, setIsReleaseModalOpen] = useState(false);

  const selectedItems = candidates.filter((c) => selectedIds.includes(c.id));
  const totalDisbursement = selectedItems.reduce((acc, c) => acc + c.amount, 0);
  const totalTaxProtected = selectedItems.reduce(
    (acc, c) => acc + c.taxProtected,
    0
  );

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleDownload = async (bankRail: "ICICI_CIB" | "HDFC_ENET") => {
    // Calls API POST /api/v1/payouts/download-csv
    const fakeCsv =
      bankRail === "ICICI_CIB"
        ? "PAB_VENDOR,NFT,167105000250,PRECISION COMPONENTS,00000030123456789,SBIN0001234,500000.00,INR,12/09/2026,INV 0891 MSME,info@precision.com\r\n"
        : "NEFT,00000030123456789,500000.00,PRECISION COMPONENTS,PAR,VC09120001,SBIN0001234,HDFCCORP9988,12/09/2026,MSME CLR INV 0891\r\n";

    const blob = new Blob([fakeCsv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `${bankRail}_Batch_20260912_01.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Monday Morning Statutory Clearing Batch #2026-W37
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Prioritized disbursement batch protecting Section 43B(h) disallowances and stopping compounding penal interest
          </p>
        </div>

        <button
          onClick={() => setIsReleaseModalOpen(true)}
          disabled={selectedItems.length === 0}
          className="px-5 py-2.5 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-sm transition-all flex items-center gap-2 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          Authorize Batch ({selectedItems.length})
        </button>
      </div>

      {/* Hero Financial Protection Banner */}
      <div className="bg-emerald-50/80 border border-emerald-200 rounded-2xl p-5 flex items-center justify-between">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-emerald-800">
            Current Batch Protection Impact
          </div>
          <div className="text-xl font-black text-emerald-950 mt-1 font-mono">
            Paying {formatINR(totalDisbursement)} today protects {formatINR(totalTaxProtected)} in cash tax disallowances.
          </div>
          <p className="text-xs text-emerald-700 mt-1">
            Eliminates monthly compounding penal interest at 19.50% p.a. (3x RBI Bank Rate) under MSMED Act Section 16.
          </p>
        </div>

        <div className="text-right font-mono">
          <div className="text-xs text-slate-500">Selected Invoices</div>
          <div className="text-2xl font-bold text-slate-900">
            {selectedItems.length} of {candidates.length}
          </div>
        </div>
      </div>

      {/* Batch Candidates Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="font-semibold text-xs text-slate-700 uppercase tracking-wider">
            Invoices Due in the Next 7 Days (Micro & Small Manufacturers)
          </span>
          <span className="text-xs text-slate-500">
            Native Zero-Shift Banking Format Verified
          </span>
        </div>

        <table className="w-full text-left text-xs divide-y divide-slate-200">
          <thead>
            <tr className="bg-slate-50/50 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              <th className="py-3 px-4 w-12 text-center">Select</th>
              <th className="py-3 px-4">Beneficiary Legal Name</th>
              <th className="py-3 px-4">Invoice Reference</th>
              <th className="py-3 px-4">Bank Account</th>
              <th className="py-3 px-4">IFSC</th>
              <th className="py-3 px-4">Statutory Due</th>
              <th className="py-3 px-4 text-right">Payable Amount</th>
              <th className="py-3 px-4 text-right">Tax Shield Protected</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {candidates.map((item) => (
              <tr
                key={item.id}
                className={`hover:bg-slate-50 transition-colors ${
                  selectedIds.includes(item.id) ? "bg-emerald-50/20" : ""
                }`}
              >
                <td className="py-3.5 px-4 text-center">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(item.id)}
                    onChange={() => toggleSelect(item.id)}
                    className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 border-slate-300"
                  />
                </td>
                <td className="py-3.5 px-4 font-semibold text-slate-900">
                  {item.vendorName}
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-700">
                  {item.invoiceReference}
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-600">
                  {item.bankAccountMasked}
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-600">
                  {item.ifsc}
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-700">
                  {item.statutoryDueDate}
                </td>
                <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">
                  {formatINR(item.amount)}
                </td>
                <td className="py-3.5 px-4 text-right font-mono font-bold text-emerald-600">
                  {formatINR(item.taxProtected)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Embedded Working Capital Fintech Referral Card */}
      <WorkingCapitalFinancingCard batchAmount={totalDisbursement} />

      {/* Modal */}
      <BatchReleaseModal
        isOpen={isReleaseModalOpen}
        onClose={() => setIsReleaseModalOpen(false)}
        totalAmount={totalDisbursement}
        protectedTaxShield={totalTaxProtected}
        recordCount={selectedItems.length}
        onAuthorizeAndDownload={handleDownload}
      />
    </div>
  );
}
