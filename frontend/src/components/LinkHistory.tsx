"use client";

import { useCallback, useEffect, useState } from "react";

import { deleteLink, fetchLinks } from "@/lib/api";
import type { LinkItem } from "@/lib/types";

type LinkHistoryProps = {
  refreshKey: number;
  prepend?: LinkItem[];
};

export function LinkHistory({ refreshKey, prepend = [] }: LinkHistoryProps) {
  const [links, setLinks] = useState<LinkItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hiddenCodes, setHiddenCodes] = useState<Set<string>>(new Set());

  const loadLinks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchLinks();
      setLinks(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không tải được danh sách");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLinks();
  }, [loadLinks, refreshKey]);

  function handleDeleted(code: string) {
    setHiddenCodes((prev) => new Set(prev).add(code));
    setLinks((prev) => prev.filter((item) => item.code !== code));
  }

  const prependCodes = new Set(prepend.map((item) => item.code));
  const displayLinks = [
    ...prepend.filter((item) => !hiddenCodes.has(item.code)),
    ...links.filter((item) => !prependCodes.has(item.code) && !hiddenCodes.has(item.code)),
  ];

  return (
    <section className="card mt-8">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-800">Lịch sử link</h2>
        <button type="button" onClick={loadLinks} className="btn-secondary text-sm">
          Làm mới
        </button>
      </div>

      {isLoading && !error && <p className="text-sm text-slate-500">Đang tải...</p>}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {!isLoading && !error && displayLinks.length === 0 && (
        <p className="text-sm text-slate-500">Chưa có link nào.</p>
      )}

      <ul className="space-y-3">
        {displayLinks.map((link) => (
          <li
            key={link.code}
            className="rounded-xl border border-slate-100 bg-slate-50/80 p-4 transition hover:border-blue-200"
          >
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0 flex-1">
                <a
                  href={link.short_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block truncate font-mono font-medium text-blue-700 hover:underline"
                >
                  {link.short_url.replace(/^https?:\/\//, "")}
                </a>
                <p className="mt-1 truncate text-sm text-slate-500" title={link.original_url}>
                  {link.original_url}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <span className="text-xs text-slate-500">{link.click_count} click</span>
                <CopyButton text={link.short_url} />
                <DeleteButton
                  code={link.code}
                  shortUrl={link.short_url}
                  onDeleted={handleDeleted}
                />
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <button type="button" onClick={handleCopy} className="btn-secondary px-2 py-1 text-xs">
      {copied ? "OK" : "Copy"}
    </button>
  );
}

function DeleteButton({
  code,
  shortUrl,
  onDeleted,
}: {
  code: string;
  shortUrl: string;
  onDeleted: (code: string) => void;
}) {
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleDelete() {
    const label = shortUrl.replace(/^https?:\/\//, "");
    if (!window.confirm(`Xóa link ${label}?`)) return;

    setIsDeleting(true);
    try {
      await deleteLink(code);
      onDeleted(code);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : "Không xóa được link");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <button
      type="button"
      onClick={handleDelete}
      disabled={isDeleting}
      className="rounded-lg border border-red-200 bg-white px-2 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:opacity-50"
    >
      {isDeleting ? "..." : "Xóa"}
    </button>
  );
}
