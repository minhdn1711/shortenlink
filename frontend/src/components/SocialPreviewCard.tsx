import { resolveMetaImageUrl } from "@/lib/assets";
import type { LinkItem } from "@/lib/types";

type SocialPreviewCardProps = {
  link: LinkItem;
};

function displayHost(link: LinkItem): string {
  try {
    const host = new URL(link.short_url).hostname;
    return host.replace(/^www\./, "").toUpperCase();
  } catch {
    return "PHANMEMCONGNGHEVIP.ONLINE";
  }
}

export function SocialPreviewCard({ link }: SocialPreviewCardProps) {
  const title = link.meta_title?.trim() || link.description?.trim() || displayHost(link);
  const description =
    link.meta_description?.trim() || link.short_url.replace(/^https?:\/\//, "");
  const image = resolveMetaImageUrl(link.meta_image_url);
  const hasPreview = Boolean(image || link.meta_title || link.meta_description);

  if (!hasPreview) {
    return (
      <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
        Chưa có ảnh preview cho Facebook/Zalo. Lần sau bấm <strong>Tùy chỉnh</strong> → tải
        biểu ngữ + tiêu đề trước khi rút gọn.
      </div>
    );
  }

  return (
    <div className="mt-3 overflow-hidden rounded-lg border border-slate-200 bg-white">
      <p className="border-b border-slate-100 px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-slate-500">
        Xem trước khi dán lên Facebook / Zalo
      </p>
      <div className="flex gap-0">
        {image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={image}
            alt=""
            className="h-24 w-24 shrink-0 object-cover sm:h-28 sm:w-28"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
        ) : (
          <div className="flex h-24 w-24 shrink-0 items-center justify-center bg-slate-100 text-2xl text-slate-400 sm:h-28 sm:w-28">
            🖼
          </div>
        )}
        <div className="min-w-0 flex-1 border-l border-slate-100 p-2">
          <p className="truncate text-[11px] font-medium uppercase text-slate-500">
            {displayHost(link)}
          </p>
          <p className="line-clamp-2 text-sm font-semibold text-slate-900">{title}</p>
          <p className="mt-0.5 line-clamp-2 text-xs text-slate-600">{description}</p>
        </div>
      </div>
    </div>
  );
}
