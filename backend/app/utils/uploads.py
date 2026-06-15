import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

ALLOWED_CONTENT_TYPES = frozenset(
    {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }
)

EXTENSION_BY_TYPE = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


async def save_meta_image(
    file: UploadFile,
    upload_dir: Path,
    max_bytes: int,
) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận ảnh jpg, png, jpeg, webp",
        )

    data = await file.read()
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ảnh tối đa {max_bytes // 1024}KB",
        )

    if len(data) < 32:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ảnh không hợp lệ",
        )

    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = EXTENSION_BY_TYPE.get(file.content_type, ".jpg")
    filename = f"{secrets.token_urlsafe(12)}{ext}"
    path = upload_dir / filename
    path.write_bytes(data)
    return filename
