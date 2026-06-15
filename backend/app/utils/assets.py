from app.config import settings


def public_upload_url(filename: str) -> str:
    return f"{settings.public_asset_base_url.rstrip('/')}/uploads/{filename}"


def normalize_meta_image_url(image_url: str | None) -> str | None:
    if not image_url:
        return None

    raw = image_url.strip()
    if not raw:
        return None

    if "/uploads/" in raw:
        filename = raw.split("/uploads/", 1)[1].split("?")[0].strip("/")
        if filename:
            return public_upload_url(filename)

    return raw
