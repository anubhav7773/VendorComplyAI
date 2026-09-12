// apps/web/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", // Generates pure static HTML/JS output for Cloudflare Pages
  trailingSlash: false,
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    unoptimized: true, // Cloudflare Pages Edge serves static images directly
  },
  env: {
    NEXT_PUBLIC_PARENT_DOMAIN: "asiverticals.me",
    NEXT_PUBLIC_APP_SUBDOMAIN: "vendorcomply.asiverticals.me",
  },
};

export default nextConfig;
