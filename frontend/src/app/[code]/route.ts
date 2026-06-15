import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = (process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const RESERVED = new Set(["api", "_next", "favicon.ico", "robots.txt", "sitemap.xml"]);

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ code: string }> },
) {
  const { code } = await context.params;

  if (!code || RESERVED.has(code) || code.includes(".")) {
    return NextResponse.next();
  }

  const userAgent = request.headers.get("user-agent") ?? "ShortenLink";

  try {
    const response = await fetch(`${BACKEND_URL}/${encodeURIComponent(code)}`, {
      redirect: "manual",
      headers: { "user-agent": userAgent },
    });

    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (location) {
        return NextResponse.redirect(location, 307);
      }
    }

    const contentType = response.headers.get("content-type") ?? "";
    if (response.ok && contentType.includes("text/html")) {
      const html = await response.text();
      return new NextResponse(html, {
        status: 200,
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }

    if (response.status === 404) {
      return NextResponse.redirect(new URL("/", request.url));
    }
  } catch {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.redirect(new URL("/", request.url));
}
