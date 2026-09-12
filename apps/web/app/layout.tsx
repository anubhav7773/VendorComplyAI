// apps/web/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VendorComply AI | Section 43B(h) Statutory Compliance",
  description:
    "Autonomous B2B AP Compliance Platform for MSMED Section 15/16 & Section 43B(h) by asiverticals.me",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-emerald-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
