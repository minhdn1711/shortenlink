export const STATIC_SHORT_DOMAIN =
  process.env.NEXT_PUBLIC_SHORT_DOMAIN || "phanmemcongnghevip.online";

export const AVAILABLE_DOMAINS = [
  {
    label: `https://${STATIC_SHORT_DOMAIN}`,
    value: STATIC_SHORT_DOMAIN,
  },
] as const;

export function displayDomain(domain: string): string {
  return domain.replace(/^https?:\/\//, "").replace(/\/$/, "");
}

export function previewShortLink(domain: string, code: string): string {
  return `${displayDomain(domain)}/${code}`;
}

export function domainForApi(domain: string): string {
  return displayDomain(domain) || STATIC_SHORT_DOMAIN;
}

export function normalizeInputUrl(url: string): string {
  const trimmed = url.trim();
  if (!trimmed) return trimmed;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
}
