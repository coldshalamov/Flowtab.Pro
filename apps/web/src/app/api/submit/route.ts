import { NextResponse } from "next/server";

export const runtime = "nodejs";

const API_BASE =
  process.env.API_BASE ??
  process.env.NEXT_PUBLIC_API_BASE ??
  "http://localhost:8000";

const ADMIN_KEY = process.env.ADMIN_KEY;
const IS_PROD = process.env.NODE_ENV === "production";

export async function POST(req: Request) {
  if (!ADMIN_KEY) {
    if (IS_PROD) {
      return NextResponse.json(
        { error: "Service unavailable", message: "Missing ADMIN_KEY" },
        { status: 503 }
      );
    }

    return NextResponse.json({ ok: true, mocked: true }, { status: 200 });
  }

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: "Bad request", message: "Invalid JSON body" },
      { status: 400 }
    );
  }

  const upstream = await fetch(`${API_BASE}/v1/prompts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": ADMIN_KEY,
      Accept: "application/json",
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  const contentType = upstream.headers.get("content-type") ?? "application/json";
  const text = await upstream.text();

  return new NextResponse(text, {
    status: upstream.status,
    headers: {
      "Content-Type": contentType,
    },
  });
}
