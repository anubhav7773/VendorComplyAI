"use client";

import React from "react";
import { Check, Zap, ShieldCheck } from "lucide-react";
import { QuotaBanner } from "@/components/billing/quota-banner";

export default function BillingPage() {
  const plans = [
    {
      name: "Starter Annual",
      price: "₹3,000",
      cadence: "/ month (₹36,000 billed annually)",
      description: "For small manufacturing units processing up to 250 bills/month.",
      quota: "Up to 250 Invoices / mo",
      features: [
        "Tally Prime Desktop Sync Agent (.exe)",
        "Section 43B(h) Countdown Radar",
        "Section 15 Dispute Freeze Logging",
        "Excel Payout Export (Standard)",
        "Email Support",
      ],
      ctaText: "Select Starter",
      highlighted: false,
    },
    {
      name: "Growth Annual",
      price: "₹6,500",
      cadence: "/ month (₹78,000 billed annually)",
      description: "For growing enterprises with active connected banking and CA audits.",
      quota: "Up to 1,000 Invoices / mo",
      features: [
        "1-Click ICICI CIB & HDFC ENet CSV File Generators",
        "Form 3CD Clause 22 Certified Excel Working Pack",
        "Promoter / CFO WhatsApp Approval OTP & Alerts",
        "Support for up to 3 Corporate GSTINs",
        "Priority WhatsApp & CA Audit Hotline",
      ],
      ctaText: "Upgrade to Growth (Recommended)",
      highlighted: true,
    },
    {
      name: "Enterprise Annual",
      price: "₹14,000",
      cadence: "/ month (₹1,68,000 billed annually)",
      description: "For large industrial conglomerates with multi-branch Tally servers.",
      quota: "Unlimited Invoices / mo",
      features: [
        "Multi-Branch / Multi-Server Tally Synchronization",
        "Custom ERP & SAP API Connectors",
        "Unlimited Corporate GSTINs & Subsidiaries",
        "Dedicated Chartered Accountant Account Manager",
        "Custom Bank Host-to-Host (H2H) Protocol Integration",
      ],
      ctaText: "Contact Enterprise Sales",
      highlighted: false,
    },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Soft Usage Banner */}
      <QuotaBanner
        processedCount={84}
        quotaLimit={100}
        tierName="EVALUATION_TRIAL"
      />

      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Subscription Plans & Entitlements
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Scale your Section 43B(h) compliance and unlock automated banking rails with transparent annual billing
        </p>
      </div>

      {/* Pricing Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((p, idx) => (
          <div
            key={idx}
            className={`rounded-2xl p-6 border flex flex-col justify-between transition-all ${
              p.highlighted
                ? "border-emerald-500 bg-white shadow-xl ring-2 ring-emerald-500/20 relative"
                : "border-slate-200 bg-white shadow-sm"
            }`}
          >
            {p.highlighted && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-emerald-600 text-white text-[10px] font-bold uppercase tracking-wider">
                Most Popular
              </div>
            )}

            <div>
              <div className="text-sm font-bold text-slate-900">{p.name}</div>
              <p className="text-xs text-slate-500 mt-1 min-h-[32px]">
                {p.description}
              </p>

              <div className="mt-4 pt-4 border-t border-slate-100">
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-black font-mono text-slate-900">
                    {p.price}
                  </span>
                  <span className="text-xs text-slate-500">{p.cadence}</span>
                </div>
              </div>

              <div className="mt-4 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold">
                <Zap className="w-3.5 h-3.5 text-emerald-600" />
                {p.quota}
              </div>

              <div className="mt-6 space-y-2.5 text-xs text-slate-600">
                {p.features.map((f, fIdx) => (
                  <div key={fIdx} className="flex items-start gap-2">
                    <div className="p-0.5 rounded-full bg-emerald-100 text-emerald-700 mt-0.5 shrink-0">
                      <Check className="w-3 h-3" />
                    </div>
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8 pt-4 border-t border-slate-100">
              <button
                className={`w-full py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                  p.highlighted
                    ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-md"
                    : "bg-slate-100 hover:bg-slate-200 text-slate-800"
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                {p.ctaText}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center text-xs text-slate-400">
        All plans are billed annually upfront and include official GST input credit tax invoices issued by <strong>asiverticals.me</strong>.
      </div>
    </div>
  );
}
