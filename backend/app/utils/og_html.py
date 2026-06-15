import html
import json
from urllib.parse import urlparse

from app.models import Link
from app.utils.assets import normalize_meta_image_url
from app.utils.mobile_redirect import detect_app_target


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _build_app_link_tags(target_url: str) -> str:
    """Facebook App Links — giúp bấm từ feed mở app Shopee/TikTok, không qua webview."""
    rule = detect_app_target(target_url)
    if rule is None:
        return ""

    title = str(rule["title"])
    android_package = str(rule["android_package"])
    ios_store_id = str(rule["ios_app_store_id"])
    safe_url = _esc(target_url)

    return f"""
  <meta property="al:android:url" content="{safe_url}" />
  <meta property="al:android:package" content="{_esc(android_package)}" />
  <meta property="al:android:app_name" content="{_esc(title)}" />
  <meta property="al:ios:url" content="{safe_url}" />
  <meta property="al:ios:app_store_id" content="{_esc(ios_store_id)}" />
  <meta property="al:ios:app_name" content="{_esc(title)}" />
  <meta property="al:web:url" content="{safe_url}" />"""


def build_og_preview_html(link: Link, short_url: str, _asset_base: str = "") -> str:
    app_rule = detect_app_target(link.original_url)
    app_label = str(app_rule["title"]) if app_rule else None

    title = (link.meta_title or link.description or app_label or link.code or "ShortenLink").strip()
    description = (
        link.meta_description
        or link.description
        or (f"Mở trên {app_label}" if app_label else title)
    ).strip()
    image = normalize_meta_image_url(link.meta_image_url) or ""
    site_name = urlparse(short_url).netloc or ""
    app_link_tags = _build_app_link_tags(link.original_url)

    og_image_tags = ""
    if image:
        og_image_tags = f"""
  <meta property="og:image" content="{_esc(image)}" />
  <meta property="og:image:secure_url" content="{_esc(image)}" />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:image" content="{_esc(image)}" />"""

    return f"""<!DOCTYPE html>
<html lang="vi" prefix="og: https://ogp.me/ns#">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_esc(title)}</title>
  <meta name="description" content="{_esc(description)}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{_esc(short_url)}" />
  <meta property="og:title" content="{_esc(title)}" />
  <meta property="og:description" content="{_esc(description)}" />
  <meta property="og:site_name" content="{_esc(site_name)}" />{og_image_tags}{app_link_tags}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{_esc(title)}" />
  <meta name="twitter:description" content="{_esc(description)}" />
  <link rel="image_src" href="{_esc(image)}" />
</head>
<body>
  <p>{_esc(title)}</p>
  {f'<img src="{_esc(image)}" alt="" />' if image else ""}
  <script>window.location.replace({json.dumps(link.original_url)});</script>
  <noscript><meta http-equiv="refresh" content="0; url={_esc(link.original_url)}" /></noscript>
</body>
</html>"""
