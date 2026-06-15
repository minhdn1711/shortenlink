import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const SHORT_DOMAIN = (
  process.env.NEXT_PUBLIC_SHORT_DOMAIN ?? ""
).toLowerCase();

const WEB_ORIGIN = (
  process.env.NEXT_PUBLIC_WEB_ORIGIN ?? "https://adminphanmemvip.xyz"
).replace(/\/$/, "");

const RESERVED = new Set(["api", "_next", "favicon.ico", "robots.txt", "sitemap.xml"]);

function isShortLinkHost(host: string): boolean {
  const bare = host.split(":")[0]?.toLowerCase() ?? "";
  return bare === SHORT_DOMAIN || bare === `www.${SHORT_DOMAIN}`;
}

function isShortCodePath(pathname: string): boolean {
  const segment = pathname.replace(/^\//, "").split("/")[0];
  if (!segment || segment.includes(".")) return false;
  return !RESERVED.has(segment);
}

export function proxy(request: NextRequest) {
  const host = request.headers.get("host") ?? "";
  if (!isShortLinkHost(host)) return NextResponse.next();

  const { pathname } = request.nextUrl;
  if (isShortCodePath(pathname)) return NextResponse.next();

  if (pathname === "/" || pathname === "") {
    const webHost = new URL(WEB_ORIGIN).hostname.toLowerCase();
    const currentHost = host.split(":")[0]?.toLowerCase() ?? "";
    if (webHost !== currentHost) {
      return NextResponse.redirect(WEB_ORIGIN);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
