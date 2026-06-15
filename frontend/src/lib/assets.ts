const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");

/** Ảnh upload luôn hiển thị qua API domain (Facebook + preview web). */
export function resolveMetaImageUrl(url: string | null | undefined): string {
  if (!url?.trim()) return "";

  const trimmed = url.trim();
  if (!API_BASE) return trimmed;

  if (trimmed.includes("/uploads/")) {
    const filename = trimmed.split("/uploads/")[1]?.split("?")[0]?.trim();
    if (filename) return `${API_BASE}/uploads/${filename}`;
  }

  return trimmed;
}
