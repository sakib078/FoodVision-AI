"use client";

import { useEffect } from "react";

const DEFAULT_INTERVAL_MS = 14 * 60 * 1000;
const MIN_INTERVAL_MS = 60 * 1000;

export default function KeepAlivePing() {
  useEffect(() => {
    const enabled = (process.env.NEXT_PUBLIC_KEEP_ALIVE_ENABLED ?? "false").toLowerCase() === "true";
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL;

    if (!enabled || !apiBase || process.env.NODE_ENV !== "production") {
      return;
    }

    const parsedInterval = Number(process.env.NEXT_PUBLIC_KEEP_ALIVE_INTERVAL_MS ?? DEFAULT_INTERVAL_MS);
    const intervalMs = Number.isFinite(parsedInterval)
      ? Math.max(parsedInterval, MIN_INTERVAL_MS)
      : DEFAULT_INTERVAL_MS;

    const healthUrl = `${apiBase.replace(/\/$/, "")}/health`;

    const ping = async () => {
      try {
        await fetch(healthUrl, {
          method: "GET",
          cache: "no-store",
          keepalive: true,
        });
      } catch {
        // Keep-alive is best effort and should never affect user UI.
      }
    };

    // Delay the first ping slightly to avoid competing with initial page load.
    const timeoutId = window.setTimeout(() => {
      ping();
    }, 20000);

    const intervalId = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        ping();
      }
    }, intervalMs);

    return () => {
      window.clearTimeout(timeoutId);
      window.clearInterval(intervalId);
    };
  }, []);

  return null;
}
