"use client";

import { useState } from "react";

import { SocialPreviewCard } from "@/components/SocialPreviewCard";
import { previewShortLink } from "@/lib/domain";
import type { LinkItem } from "@/lib/types";

type ResultCardProps = {
  link: LinkItem;
};

function displayShortLink(link: LinkItem): string {
  if (link.short_domain) {
    return previewShortLink(link.short_domain, link.code);
  }
  return link.short_url.replace(/^https?:\/\//, "");
}

export function ResultCard({ link }: ResultCardProps) {
  const [copied, setCopied] = useState(false);
  const displayUrl = displayShortLink(link);

  async function copyShortUrl() {
    await navigator.clipboard.writeText(`https://${displayUrl}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="rounded-xl border border-green-200 bg-green-50 p-4">
      <p className="text-sm font-medium text-green-800">Link đã rút gọn</p>
      <a
        href={link.short_url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-1 block break-all font-mono text-lg font-semibold text-green-900 hover:underline"
      >
        {displayUrl}
      </a>
      <p className="mt-2 truncate text-sm text-slate-600" title={link.original_url}>
        → {link.original_url}
      </p>
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
        {link.has_password && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-amber-800">Có mật khẩu</span>
        )}
        {link.channel && <span>Kênh: {link.channel}</span>}
        {link.description && <span>{link.description}</span>}
      </div>
      <SocialPreviewCard link={link} />
      <div className="mt-3 flex gap-2">
        <button type="button" onClick={copyShortUrl} className="btn-secondary text-sm">
          {copied ? "Đã sao chép!" : "Sao chép"}
        </button>
        <a href={link.short_url} target="_blank" rel="noopener noreferrer" className="btn-secondary text-sm">
          Mở link
        </a>
      </div>
    </div>
  );
}
