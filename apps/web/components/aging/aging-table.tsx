// apps/web/components/aging/aging-table.tsx
"use client";

import React, { useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  ShieldAlert,
  MoreVertical,
} from "lucide-react";
import { formatINR } from "@/lib/utils";

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

  const filteredInvoices = invoices.filter((inv) => {
    if (selectedFilter === "CRITICAL")
      return inv.overdueDays > 0 && inv.status !== "DISPUTED_HOLD";
    if (selectedFilter === "DUE_SOON")
      return inv.overdueDays <= 0 && inv.status === "UNPAID";
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
            { id: "CRITICAL", label: "Critical Overdue" },
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
              <tr
                key={inv.id}
                className="hover:bg-slate-50/80 transition-colors"
              >
                {/* Vendor Column */}
                <td className="py-3.5 px-6">
                  <div className="font-semibold text-slate-900">
                    {inv.vendorName}
                  </div>
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

                {/* Invoice Reference */}
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
                    <span className="text-amber-700 font-medium">
                      15 Days (Default)
                    </span>
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
                      <ShieldAlert className="w-3.5 h-3.5" /> Disputed Hold
                    </span>
                  ) : inv.isTrader ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600">
                      Exempt
                    </span>
                  ) : inv.overdueDays > 0 ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200 animate-pulse">
                      <AlertCircle className="w-3.5 h-3.5" /> +{inv.overdueDays}
                      d Overdue
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Compliant
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
                    title="Log Statutory Dispute"
                  >
                    <MoreVertical className="w-4 h-4" />
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
