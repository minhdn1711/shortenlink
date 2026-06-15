"use client";

import { useEffect, useState } from "react";

import { uploadMetaImage } from "@/lib/api";
import { resolveMetaImageUrl } from "@/lib/assets";

type MetaImageUploadProps = {
  value: string;
  onChange: (url: string) => void;
  onError?: (message: string) => void;
};

const MAX_BYTES = 500 * 1024;

export function MetaImageUpload({ value, onChange, onError }: MetaImageUploadProps) {
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [fileName, setFileName] = useState("");

  const displaySrc = localPreview || resolveMetaImageUrl(value) || null;

  useEffect(() => {
    return () => {
      if (localPreview) URL.revokeObjectURL(localPreview);
    };
  }, [localPreview]);

  async function handleFile(file: File | null) {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      onError?.("Chỉ chấp nhận file ảnh jpg, png, jpeg");
      return;
    }
    if (file.size > MAX_BYTES) {
      onError?.("Ảnh phải nhỏ hơn 500 KB");
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    if (localPreview) URL.revokeObjectURL(localPreview);
    setLocalPreview(objectUrl);
    setFileName(file.name);
    setIsUploading(true);

    try {
      const { url } = await uploadMetaImage(file);
      onChange(url);
    } catch (err) {
      onError?.(err instanceof Error ? err.message : "Không tải được ảnh");
      URL.revokeObjectURL(objectUrl);
      setLocalPreview(null);
      setFileName("");
      onChange("");
    } finally {
      setIsUploading(false);
    }
  }

  function clearImage() {
    if (localPreview) URL.revokeObjectURL(localPreview);
    setLocalPreview(null);
    setFileName("");
    onChange("");
  }

  return (
    <div className="rounded-xl border border-blue-100 bg-blue-50/40 p-4">
      <label className="label mb-1" htmlFor="meta-image-file">
        Tải lên biểu ngữ tùy chỉnh
      </label>
      <p className="hint mb-3">
        Chọn ảnh <strong>từ máy tính / điện thoại</strong> — jpg, png, jpeg, nhỏ hơn 500KB.
      </p>

      <input
        id="meta-image-file"
        type="file"
        accept="image/jpeg,image/png,image/jpg,image/webp,image/*"
        disabled={isUploading}
        className="file-input-native"
        onChange={(e) => {
          void handleFile(e.target.files?.[0] ?? null);
        }}
      />

      {isUploading && (
        <p className="mt-2 flex items-center gap-2 text-sm font-medium text-blue-700">
          <span className="upload-spinner inline-block h-4 w-4" />
          Đang tải ảnh lên server...
        </p>
      )}

      {!isUploading && value && (
        <p className="mt-2 text-sm font-medium text-green-700">✓ Đã tải ảnh lên thành công</p>
      )}

      {displaySrc && (
        <div className="mt-3 overflow-hidden rounded-lg border border-slate-200 bg-white p-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={displaySrc}
            alt="Xem trước biểu ngữ"
            className="mx-auto max-h-48 w-full rounded-md object-contain"
          />
          {fileName && (
            <p className="mt-2 truncate text-center text-xs text-slate-500">{fileName}</p>
          )}
          <button
            type="button"
            onClick={clearImage}
            disabled={isUploading}
            className="mt-2 w-full rounded-lg border border-red-200 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
          >
            Xóa ảnh
          </button>
        </div>
      )}
    </div>
  );
}
