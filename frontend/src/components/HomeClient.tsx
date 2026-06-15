"use client";

import { useState } from "react";

import { LinkHistory } from "@/components/LinkHistory";
import { ResultCard } from "@/components/ResultCard";
import { ShortenPanel } from "@/components/ShortenPanel";
import type { LinkItem } from "@/lib/types";

export function HomeClient() {
  const [latestLinks, setLatestLinks] = useState<LinkItem[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);

  function handleCreated(links: LinkItem[]) {
    setLatestLinks(links);
    setRefreshKey((key) => key + 1);
  }

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-6 sm:py-10">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-slate-800 sm:text-4xl">
          Rút gọn link
        </h1>
        <p className="mt-2 text-slate-600">
          Link ngắn: <span className="font-mono font-semibold text-blue-700">/mã-của-bạn</span>
        </p>
      </header>

      <ShortenPanel onCreated={handleCreated} />

      {latestLinks.length > 0 && (
        <section className="mt-8 space-y-3">
          <h2 className="text-lg font-semibold text-slate-800">Kết quả vừa tạo</h2>
          {latestLinks.map((link) => (
            <ResultCard key={link.code} link={link} />
          ))}
        </section>
      )}

      <LinkHistory refreshKey={refreshKey} prepend={latestLinks} />
    </main>
  );
}
