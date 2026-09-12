// apps/web/components/aging/dispute-modal.tsx
"use client";

import React, { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { InvoiceRecord } from "./aging-table";

export function DisputeModal({
  invoice,
  isOpen,
  onClose,
  onConfirmDispute,
}: {
  invoice: InvoiceRecord | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmDispute: (details: {
    voucherId: string;
    objectionDate: string;
    channel: string;
    trackingRef: string;
    category: string;
    notes: string;
  }) => Promise<void>;
}) {
  const [objectionDate, setObjectionDate] = useState("");
  const [channel, setChannel] = useState("EMAIL");
  const [trackingRef, setTrackingRef] = useState("");
  const [category, setCategory] = useState("DEFECTIVE_MATERIAL");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen || !invoice) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onConfirmDispute({
      voucherId: invoice.id,
      objectionDate,
      channel,
      trackingRef,
      category,
      notes,
    });
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            Log Statutory Dispute (Section 15 MSMED Act)
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-slate-500 mt-3">
          Under Section 2(b) of the MSMED Act, lodging a written objection
          within 15 days of delivery suspends deemed acceptance and freezes
          Section 16 penal interest.
        </p>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Invoice Reference
            </label>
            <input
              disabled
              value={`${invoice.invoiceReference} (${invoice.vendorName})`}
              className="w-full bg-slate-100 border border-slate-200 rounded-lg p-2 font-mono text-slate-600"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Date Objection Delivered *
              </label>
              <input
                type="date"
                required
                value={objectionDate}
                onChange={(e) => setObjectionDate(e.target.value)}
                className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Delivery Channel *
              </label>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
              >
                <option value="EMAIL">Email</option>
                <option value="REGISTERED_POST">Registered Speed Post</option>
                <option value="WHATSAPP">WhatsApp Business</option>
                <option value="WRITTEN_MEMO">Physical Written Memo</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Objection Tracking Ref / Message ID *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Email Message-ID or SpeedPost Tracking No."
              value={trackingRef}
              onChange={(e) => setTrackingRef(e.target.value)}
              className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Dispute Category *
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
            >
              <option value="DEFECTIVE_MATERIAL">
                Defective Goods / Quality Rejection
              </option>
              <option value="SHORT_DELIVERY">
                Short Delivery / Quantity Mismatch
              </option>
              <option value="RATE_DISCREPANCY">
                Invoiced Rate Higher than PO
              </option>
              <option value="TDS_DISPUTE">
                Incorrect GST / TDS Line Classification
              </option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Audit Scrutiny Notes
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Provide factual audit notes for CA review..."
              className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 outline-none"
            />
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-lg font-semibold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-sm"
            >
              {loading ? "Locking..." : "Freeze Statutory Clock"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
