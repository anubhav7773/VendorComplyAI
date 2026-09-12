// cloudflare/worker.js

export default {
  // 1. Scheduled Cron Trigger (Runs every 10 minutes: */10 * * * *)
  // Prevents Render Free Tier web service from spinning down after 15m inactivity
  async scheduled(event, env, ctx) {
    const healthEndpoint = env.BACKEND_ORIGIN 
      ? `${env.BACKEND_ORIGIN.replace(/\/$/, "")}/api/v1/health`
      : "https://api-vendorcomply.onrender.com/api/v1/health";

    try {
      const pingResponse = await fetch(healthEndpoint, {
        method: "GET",
        headers: {
          "User-Agent": "VendorComply-Edge-KeepAlive/1.0 (+https://asiverticals.me)",
          "Accept": "application/json",
        },
      });

      console.log(
        `[CRON KEEP-ALIVE] Ping to ${healthEndpoint} executed at ${new Date().toISOString()}. Status: ${pingResponse.status}`
      );
    } catch (err) {
      console.error(`[CRON ERROR] Keep-alive ping failed: ${err.message}`);
    }
  },

  // 2. HTTP Request Fetch Handler (Edge Gateway & Reverse Proxy)
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const backendOrigin = env.BACKEND_ORIGIN || "https://api-vendorcomply.onrender.com";

    // Route /api/* directly to the FastAPI Backend
    if (url.pathname.startsWith("/api/")) {
      const targetUrl = `${backendOrigin.replace(/\/$/, "")}${url.pathname}${url.search}`;

      // Clone original request headers, ensuring Host matches backend
      const forwardHeaders = new Headers(request.headers);
      forwardHeaders.set("X-Forwarded-Host", url.hostname);
      forwardHeaders.set("X-Forwarded-Proto", url.protocol.replace(":", ""));
      forwardHeaders.set("X-Parent-Domain", "asiverticals.me");

      const backendRequest = new Request(targetUrl, {
        method: request.method,
        headers: forwardHeaders,
        body: request.body,
        redirect: "follow",
      });

      try {
        const response = await fetch(backendRequest);

        // Mutate response to inject edge security headers
        const edgeHeaders = new Headers(response.headers);
        edgeHeaders.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload");
        edgeHeaders.set("X-Content-Type-Options", "nosniff");
        edgeHeaders.set("X-Frame-Options", "DENY");
        edgeHeaders.set("X-Edge-Origin", "asiverticals.me");

        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: edgeHeaders,
        });
      } catch (err) {
        return new Response(
          JSON.stringify({
            error: "BAD_GATEWAY",
            message: "Unable to connect to upstream statutory API.",
            detail: err.message,
          }),
          {
            status: 502,
            headers: { "Content-Type": "application/json" },
          }
        );
      }
    }

    // Default 404 for non-API routes hitting worker directly
    return new Response(
      JSON.stringify({ error: "NOT_FOUND", message: "Edge route undefined." }),
      { status: 404, headers: { "Content-Type": "application/json" } }
    );
  },
};
