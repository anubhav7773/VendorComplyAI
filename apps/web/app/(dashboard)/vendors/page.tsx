"use client";

import React, { useState } from "react";
import { RefreshCw, CheckCircle2 } from "lucide-react";
import { formatINR } from "@/lib/utils";

interface VendorLedger {
  id: string;
  name: string;
  pan: string;
  gstin: string;
  udyamRegNo: string;
  category: "MICRO" | "SMALL" | "MEDIUM" | "UNREGISTERED";
  activity: "MANUFACTURER" | "SERVICE_PROVIDER" | "TRADER";
  isTraderExempt: boolean;
  creditDays: number;
  openBillsCount: number;
  totalPayableAmount: number;
}

export default function VendorsPage() {
  const [vendors] = useState<VendorLedger[]>([
    {
      id: "v-1",
      name: "Precision Components Ltd",
      pan: "AABCP1234K",
      gstin: "27AABCP1234K1Z5",
      udyamRegNo: "UDYAM-MH-01-0012345",
      category: "MICRO",
      activity: "MANUFACTURER",
      isTraderExempt: false,
      creditDays: 30,
      openBillsCount: 2,
      totalPayableAmount: 500000,
    },
    {
      id: "v-2",
      name: "Apex Wholesale Trading Corp",
      pan: "XYZAP9876C",
      gstin: "27XYZAP9876C1Z1",
      udyamRegNo: "UDYAM-MH-02-0098765",
      category: "SMALL",
      activity: "TRADER",
      isTraderExempt: true,
      creditDays: 60,
      openBillsCount: 1,
      totalPayableAmount: 1200000,
    },
    {
      id: "v-3",
      name: "BioTech Solutions LLP",
      pan: "BBBPB4321D",
      gstin: "27BBBPB4321D1Z8",
      udyamRegNo: "UDYAM-MH-01-0054321",
      category: "SMALL",
      activity: "MANUFACTURER",
      isTraderExempt: false,
      creditDays: 15,
      openBillsCount: 3,
      totalPayableAmount: 850000,
    },
  ]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Sundry Creditors Master & Udyam Intelligence
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Dynamic Udyam verification, NIC-code trader exclusions, and agreed credit terms synced from Tally Prime
          </p>
        </div>

        <button className="px-4 py-2 text-xs font-semibold border border-slate-200 rounded-lg hover:bg-slate-50 flex items-center gap-1.5 text-slate-700 bg-white shadow-sm">
          <RefreshCw className="w-4 h-4" /> Sync Tally Creditors (Port 9000)
        </button>
      </div>

      {/* Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="font-semibold text-xs text-slate-700 uppercase tracking-wider">
            Verified Supplier Ledgers ({vendors.length})
          </span>
          <span className="text-xs text-slate-500">
            Auto-classified via Gazette S.O. 2119(E)
          </span>
        </div>

        <table className="w-full text-left text-xs divide-y divide-slate-200">
          <thead>
            <tr className="bg-slate-50/50 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              <th className="py-3 px-6">Vendor Legal Entity</th>
              <th className="py-3 px-4">PAN / GSTIN</th>
              <th className="py-3 px-4">Udyam Registration</th>
              <th className="py-3 px-4">Classification</th>
              <th className="py-3 px-4">Agreed Credit</th>
              <th className="py-3 px-4 text-center">Open Bills</th>
              <th className="py-3 px-6 text-right">Total Payable</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {vendors.map((v) => (
              <tr key={v.id} className="hover:bg-slate-50 transition-colors">
                <td className="py-3.5 px-6">
                  <div className="font-semibold text-slate-900">{v.name}</div>
                  <div className="text-[10px] text-slate-400">Tally Ledger Mapped</div>
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-700">
                  <div>{v.pan}</div>
                  <div className="text-[11px] text-slate-400">{v.gstin}</div>
                </td>
                <td className="py-3.5 px-4">
                  <span className="inline-flex items-center gap-1 font-mono text-slate-800">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    {v.udyamRegNo}
                  </span>
                </td>
                <td className="py-3.5 px-4">
                  {v.isTraderExempt ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                      Trader (Exempt u/s 43Bh)
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {v.category} {v.activity}
                    </span>
                  )}
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-800">
                  {v.creditDays > 0 ? `${v.creditDays} Days` : "15 Days (Default)"}
                </td>
                <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-700">
                  {v.openBillsCount}
                </td>
                <td className="py-3.5 px-6 text-right font-mono font-bold text-slate-900">
                  {formatINR(v.totalPayableAmount)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
