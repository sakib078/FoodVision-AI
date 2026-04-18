import { NextResponse } from "next/server";

const DEFAULT_TIMEOUT_MS = 15000;

function resolveBackendBaseUrl(): string | null {

  const url = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (url) return url;

  return null;
}

export async function GET(request: Request) {
  const expectedSecret = process.env.CRON_SECRET;
  const authHeader = request.headers.get("authorization");

  if (!expectedSecret) {
    return NextResponse.json(
      { ok: false, error: "CRON_SECRET is not configured" },
      { status: 500 }
    );
  }

  if (authHeader !== `Bearer ${expectedSecret}`) {
    return NextResponse.json({ ok: false, error: "Unauthorized" }, { status: 401 });
  }

  const backendBaseUrl = resolveBackendBaseUrl();
  if (!backendBaseUrl) {
    return NextResponse.json(
      { ok: false, error: "NEXT_PUBLIC_API_BASE_URL is not configured" },
      { status: 500 }
    );
  }

  const healthUrl = `${backendBaseUrl.replace(/\/$/, "")}/health`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, DEFAULT_TIMEOUT_MS);

  try {
    const res = await fetch(healthUrl, {
      method: "GET",
      cache: "no-store",
      signal: controller.signal,
    });

    const bodyText = await res.text();
    return NextResponse.json(
      {
        ok: res.ok,
        upstreamStatus: res.status,
        healthUrl,
        body: bodyText.slice(0, 500),
      },
      { status: res.ok ? 200 : 502 }
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { ok: false, error: "Health check request failed", details: message, healthUrl },
      { status: 502 }
    );
  } finally {
    clearTimeout(timeoutId);
  }
}