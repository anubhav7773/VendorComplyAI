// apps/web/app/(dashboard)/layout.tsx
import React from "react";
import Link from "next/link";
import {
  LayoutDashboard,
  Clock,
  Send,
  Users,
  FileCheck2,
  Settings,
  Shield,
  Building2,
} from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const navItems = [
    { href: "/", label: "Exposure Radar", icon: LayoutDashboard },
    { href: "/aging", label: "15/45-Day Matrix", icon: Clock },
    { href: "/payouts", label: "Monday Batch Runs", icon: Send },
    { href: "/vendors", label: "Sundry Creditors", icon: Users },
    { href: "/audit-3cd", label: "Form 3CD Clause 22", icon: FileCheck2 },
    { href: "/settings", label: "Agent & Banking", icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden font-sans">
      {/* 240px Fixed Dark Sidebar */}
      <aside className="w-60 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Brand Header */}
          <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center font-bold text-white text-base shadow-sm">
              V
            </div>
            <div>
              <div className="font-bold text-sm text-white tracking-tight">
                VendorComply <span className="text-emerald-400">AI</span>
              </div>
              <div className="text-[10px] text-slate-400">by asiverticals.me</div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-900 hover:text-white transition-colors"
              >
                <item.icon className="w-4 h-4 text-slate-400" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Security / Tenant Isolation Footprint */}
        <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mb-1">
            <Shield className="w-3.5 h-3.5" /> SOC2 / RLS Active
          </div>
          <div>Tenant ID: aws-ap-south-1</div>
        </div>
      </aside>

      {/* Main Content Viewport */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-slate-100 rounded-lg text-slate-700">
              <Building2 className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-sm text-slate-800">
                ACME Discrete Manufacturing Pvt Ltd
              </span>
              <span className="ml-2 text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
                GST: 27AABCP1234K1Z5
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* March 31 Statutory Cutoff Countdown Badge */}
            <div className="px-3 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-1.5 animate-pulse">
              <Clock className="w-3.5 h-3.5" /> March 31 Cutoff: 200 Days Left
            </div>

            {/* CFO Profile Avatar */}
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
              CF
            </div>
          </div>
        </header>

        {/* Scrollable Viewport */}
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
