"use client";

import { FormEvent, useState } from "react";

import { MetaImageUpload } from "@/components/MetaImageUpload";
import { createLink, createLinksBulk } from "@/lib/api";
import {
  AVAILABLE_DOMAINS,
  STATIC_SHORT_DOMAIN,
  domainForApi,
  normalizeInputUrl,
  previewShortLink,
} from "@/lib/domain";
import type { LinkItem } from "@/lib/types";

type ShortenPanelProps = {
  onCreated: (links: LinkItem[]) => void;
};

type Mode = "single" | "bulk";

const CHANNELS = ["Không có", "Facebook", "Zalo", "TikTok", "YouTube", "Khác"];

export function ShortenPanel({ onCreated }: ShortenPanelProps) {
  const [mode, setMode] = useState<Mode>("single");
  const [url, setUrl] = useState("");
  const [bulkUrls, setBulkUrls] = useState("");
  const [domain, setDomain] = useState(STATIC_SHORT_DOMAIN);
  const [customCode, setCustomCode] = useState("");
  const [redirectType, setRedirectType] = useState("direct");
  const [channel, setChannel] = useState("Không có");
  const [password, setPassword] = useState("");
  const [description, setDescription] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [metaTitle, setMetaTitle] = useState("");
  const [metaDescription, setMetaDescription] = useState("");
  const [metaImageUrl, setMetaImageUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const previewCode = customCode.trim() || "abcxyz";

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const apiDomain = domainForApi(domain);
      const channelValue = channel === "Không có" ? undefined : channel;

      if (mode === "bulk") {
        const urls = bulkUrls
          .split("\n")
          .map((line) => normalizeInputUrl(line))
          .filter(Boolean);

        if (urls.length === 0) {
          throw new Error("Nhập ít nhất một link");
        }

        const links = await createLinksBulk({
          urls,
          domain: apiDomain,
          redirect_type: "direct",
          channel: channelValue,
          description: description.trim() || undefined,
        });
        onCreated(links);
        setBulkUrls("");
      } else {
        const link = await createLink({
          url: normalizeInputUrl(url),
          domain: apiDomain,
          custom_code: customCode.trim() || undefined,
          redirect_type: redirectType as "direct",
          description: description.trim() || undefined,
          channel: channelValue,
          password: password.trim() || undefined,
          meta_title: metaTitle.trim() || undefined,
          meta_description: metaDescription.trim() || undefined,
          meta_image_url: metaImageUrl.trim() || undefined,
        });
        onCreated([link]);
        setUrl("");
        setCustomCode("");
        setPassword("");
        setMetaTitle("");
        setMetaDescription("");
        setMetaImageUrl("");
      }

      setDescription("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể rút gọn link");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="card mx-auto w-full max-w-4xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* URL + nút rút gọn */}
        <div className="flex flex-col gap-3 sm:flex-row">
          {mode === "single" ? (
            <input
              type="text"
              required
              placeholder="Dán một liên kết dài"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="input flex-1"
            />
          ) : (
            <textarea
              required
              placeholder="Mỗi dòng một link (tối đa 20)"
              value={bulkUrls}
              onChange={(e) => setBulkUrls(e.target.value)}
              className="input min-h-[100px] flex-1 resize-y"
            />
          )}
          <button type="submit" disabled={isLoading} className="btn-primary sm:self-start">
            {isLoading ? "Đang xử lý..." : "Rút ngắn"}
          </button>
        </div>

        {/* Đơn / Nhiều */}
        <div className="flex items-center justify-center gap-6 text-sm">
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="radio"
              name="mode"
              checked={mode === "single"}
              onChange={() => setMode("single")}
              className="accent-blue-600"
            />
            Đơn
          </label>
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="radio"
              name="mode"
              checked={mode === "bulk"}
              onChange={() => setMode("bulk")}
              className="accent-blue-600"
            />
            Nhiều
          </label>
        </div>

        {/* Domain */}
        <div>
          <label className="label" htmlFor="domain">
            CHÚ Ý: Chọn tên miền phù hợp với nội dung
          </label>
          <select
            id="domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="select"
          >
            {AVAILABLE_DOMAINS.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <p className="hint mt-2 font-mono text-blue-700">
            Link rút gọn: {previewShortLink(domain, previewCode)}
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="redirect">
              Chuyển hướng
            </label>
            <select
              id="redirect"
              value={redirectType}
              onChange={(e) => setRedirectType(e.target.value)}
              className="select"
            >
              <option value="direct">Trực tiếp</option>
            </select>
          </div>

          {mode === "single" && (
            <div>
              <label className="label" htmlFor="custom_code">
                Custom Link
              </label>
              <p className="hint mb-2">
                Bạn có thể nhập bí danh tùy chỉnh cho link rút gọn của mình.
              </p>
              <input
                id="custom_code"
                type="text"
                placeholder="Nhập bí danh tùy chỉnh của bạn vào đây"
                value={customCode}
                onChange={(e) => setCustomCode(e.target.value)}
                className="input"
                pattern="[A-Za-z0-9_-]*"
              />
            </div>
          )}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="channel">
              Kênh
            </label>
            <select
              id="channel"
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="select"
            >
              {CHANNELS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>

          {mode === "single" && (
            <div>
              <label className="label" htmlFor="password">
                Mật khẩu bảo vệ
              </label>
              <input
                id="password"
                type="password"
                placeholder="Nhập mật khẩu của bạn vào đây"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
              />
            </div>
          )}
        </div>

        <div>
          <label className="label" htmlFor="description">
            Sự miêu tả
          </label>
          <p className="hint mb-2">
            Bạn có thể sử dụng trường này để xác định URL và xem thống kê sau này.
          </p>
          <input
            id="description"
            type="text"
            placeholder="Nhập mô tả của bạn ở đây"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input"
          />
        </div>

        {mode === "single" && (
          <MetaImageUpload
            value={metaImageUrl}
            onChange={setMetaImageUrl}
            onError={setError}
          />
        )}

        {mode === "single" && (
          <>
            <button
              type="button"
              onClick={() => setShowAdvanced((value) => !value)}
              className="btn-expand"
            >
              <span>⚙</span> Tùy chỉnh tiêu đề / mô tả
            </button>

            {showAdvanced && (
              <div className="space-y-4 rounded-xl border border-blue-100 bg-blue-50/50 p-4">
                <h3 className="text-center text-sm font-semibold text-slate-700">
                  Thẻ meta
                </h3>
                <div>
                  <label className="label">Tiêu đề meta</label>
                  <input
                    type="text"
                    placeholder="Nhập tiêu đề meta tùy chỉnh của bạn"
                    value={metaTitle}
                    onChange={(e) => setMetaTitle(e.target.value)}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Mô tả Meta</label>
                  <input
                    type="text"
                    placeholder="Nhập mô tả meta tùy chỉnh của bạn"
                    value={metaDescription}
                    onChange={(e) => setMetaDescription(e.target.value)}
                    className="input"
                  />
                </div>
              </div>
            )}
          </>
        )}

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
      </form>
    </div>
  );
}
