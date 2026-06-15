import type {
  BulkCreatePayload,
  CreateLinkPayload,
  LinkItem,
  LinkListResponse,
} from "./types";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");
const FETCH_TIMEOUT_MS = 15_000;

function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

async function fetchWithTimeout(
  input: string,
  init?: RequestInit,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
      mode: "cors",
    });
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("API không phản hồi. Kiểm tra backend đang chạy.");
    }
    throw new Error(
      API_BASE
        ? `Không gọi được ${API_BASE}`
        : "Không gọi được API. Chạy backend port 8000.",
    );
  } finally {
    clearTimeout(timer);
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as {
      detail?: string | Array<{ msg?: string; message?: string }>;
    };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      const first = data.detail[0];
      return first?.msg ?? first?.message ?? "Request failed";
    }
  } catch {
    /* ignore */
  }
  return `Lỗi API (${response.status})`;
}

export async function createLink(payload: CreateLinkPayload): Promise<LinkItem> {
  const response = await fetchWithTimeout(apiUrl("/api/links"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error(await parseError(response));
  return response.json();
}

export async function createLinksBulk(
  payload: BulkCreatePayload,
): Promise<LinkItem[]> {
  const response = await fetchWithTimeout(apiUrl("/api/links/bulk"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error(await parseError(response));
  const data = (await response.json()) as LinkListResponse;
  return data.items;
}

export async function uploadMetaImage(file: File): Promise<{ url: string }> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetchWithTimeout(apiUrl("/api/uploads/meta-image"), {
    method: "POST",
    body: form,
  });

  if (!response.ok) throw new Error(await parseError(response));
  return response.json();
}

export async function fetchLinks(limit = 20): Promise<LinkListResponse> {
  const response = await fetchWithTimeout(apiUrl(`/api/links?limit=${limit}`), {
    cache: "no-store",
  });

  if (!response.ok) throw new Error(await parseError(response));
  return response.json();
}

export async function deleteLink(code: string): Promise<void> {
  const response = await fetchWithTimeout(apiUrl(`/api/links/${encodeURIComponent(code)}`), {
    method: "DELETE",
  });

  if (!response.ok) throw new Error(await parseError(response));
}
