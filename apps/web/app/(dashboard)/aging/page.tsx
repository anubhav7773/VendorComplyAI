// apps/web/app/(dashboard)/aging/page.tsx
"use client";

import React, { useState } from "react";
import { AgingTable, InvoiceRecord } from "@/components/aging/aging-table";
import { DisputeModal } from "@/components/aging/dispute-modal";

export default function AgingPage() {
  const [invoices, setInvoices] = useState<InvoiceRecord[]>([
    {
      id: "inv-001",
      vendorName: "Precision Components Ltd",
      udyamCategory: "MICRO",
      isTrader: false,
      invoiceReference: "INV/2026/0891",
      billDate: "2026-08-10",
      agreedDays: 30,
      statutoryDueDate: "2026-09-09",
      overdueDays: 3,
      taxableAmount: 423728,
      grossAmount: 500000,
      taxExposure: 106644,
      status: "UNPAID",
    },
    {
      id: "inv-002",
      vendorName: "Apex Wholesale Trading Corp",
      udyamCategory: "SMALL",
      isTrader: true,
      invoiceReference: "TC-2026-112",
      billDate: "2026-08-15",
      agreedDays: 60,
      statutoryDueDate: "2026-09-29",
      overdueDays: 0,
      taxableAmount: 1016949,
      grossAmount: 1200000,
      taxExposure: 0,
      status: "UNPAID",
    },
    {
      id: "inv-003",
      vendorName: "BioTech Solutions LLP",
      udyamCategory: "SMALL",
      isTrader: false,
      invoiceReference: "BTS/2026/401",
      billDate: "2026-08-25",
      agreedDays: 0,
      statutoryDueDate: "2026-09-09",
      overdueDays: 3,
      taxableAmount: 720338,
      grossAmount: 850000,
      taxExposure: 181294,
      status: "UNPAID",
    },
  ]);

  const [selectedInvoice, setSelectedInvoice] = useState<InvoiceRecord | null>(
    null
  );

  const handleConfirmDispute = async (details: {
    voucherId: string;
    objectionDate: string;
    channel: string;
    trackingRef: string;
    category: string;
    notes: string;
  }) => {
    setInvoices((prev) =>
      prev.map((item) =>
        item.id === details.voucherId
          ? { ...item, status: "DISPUTED_HOLD", taxExposure: 0, overdueDays: 0 }
          : item
      )
    );
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          15/45-Day Rolling Statutory Aging Matrix
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Detailed statutory credit clocks, Udyam classifications, and Section
          43B(h) disallowance exposures
        </p>
      </div>

      <AgingTable
        invoices={invoices}
        onOpenDispute={(inv) => setSelectedInvoice(inv)}
      />

      <DisputeModal
        isOpen={Boolean(selectedInvoice)}
        invoice={selectedInvoice}
        onClose={() => setSelectedInvoice(null)}
        onConfirmDispute={handleConfirmDispute}
      />
    </div>
  );
}
