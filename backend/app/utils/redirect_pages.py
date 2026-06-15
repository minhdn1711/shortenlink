import html
import json

from app.models import Link
from app.utils.security import verify_password


def build_tiktok_landing_html(link: "Link", target_url: str) -> str:
    """Landing page dùng khi user click từ Facebook in-app browser.
    Tránh TikTok web tự mở app ngay → FB hiện 'Rời khỏi Facebook?'.
    """
    title = html.escape((link.meta_title or link.description or "Sản phẩm TikTok Shop").strip())
    description = html.escape((link.meta_description or link.description or "").strip())
    image = html.escape((link.meta_image_url or "").strip())
    safe_url = json.dumps(target_url)

    image_html = (
        f'<img src="{image}" alt="" onerror="this.style.display=\'none\'" />'
        if image
        else ""
    )
    desc_html = f'<p class="desc">{description}</p>' if description else ""

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: #f5f5f5;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }}
    .card {{
      background: #fff;
      border-radius: 16px;
      overflow: hidden;
      width: 100%;
      max-width: 440px;
      box-shadow: 0 4px 24px rgba(0,0,0,.12);
    }}
    .card img {{
      width: 100%;
      aspect-ratio: 1/1;
      object-fit: cover;
      display: block;
    }}
    .body {{ padding: 20px; }}
    h1 {{ font-size: 1.05rem; font-weight: 700; color: #111; line-height: 1.4; margin-bottom: 8px; }}
    .desc {{ font-size: 0.875rem; color: #555; margin-bottom: 16px; line-height: 1.5; }}
    .badge {{
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 0.75rem; color: #888; margin-bottom: 16px;
    }}
    .tiktok-icon {{
      width: 18px; height: 18px; fill: #010101;
    }}
    .btn {{
      display: block;
      width: 100%;
      padding: 14px;
      background: #fe2c55;
      color: #fff;
      font-size: 1rem;
      font-weight: 700;
      text-align: center;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      text-decoration: none;
    }}
    .hint {{ font-size: 0.75rem; color: #aaa; text-align: center; margin-top: 10px; }}
  </style>
</head>
<body>
  <div class="card">
    {image_html}
    <div class="body">
      <div class="badge">
        <svg class="tiktok-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.32 6.32 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.75a8.15 8.15 0 0 0 4.77 1.52V6.82a4.85 4.85 0 0 1-1-.13z"/>
        </svg>
        TikTok Shop
      </div>
      <h1>{title}</h1>
      {desc_html}
      <button class="btn" onclick="openTikTok()">Xem &amp; Mua ngay</button>
      <p class="hint">Sẽ mở TikTok để mua hàng</p>
    </div>
  </div>
  <script>
    function openTikTok() {{
      const url = {safe_url};
      window.location.href = url;
    }}
  </script>
</body>
</html>"""


def build_password_gate_html(link: Link, error: str | None = None) -> str:
    error_html = f'<p class="error">{error}</p>' if error else ""
    safe_code = json.dumps(link.code)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Link được bảo vệ</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      background: #f0f7ff;
      display: flex;
      min-height: 100vh;
      align-items: center;
      justify-content: center;
      margin: 0;
      padding: 24px;
    }}
    .card {{
      background: #fff;
      border-radius: 16px;
      padding: 32px;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 8px 30px rgba(37, 99, 235, 0.12);
    }}
    h1 {{ font-size: 1.25rem; margin: 0 0 8px; color: #1e3a5f; }}
    p {{ color: #64748b; margin: 0 0 16px; }}
    input {{
      width: 100%;
      padding: 12px 14px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      font-size: 1rem;
      box-sizing: border-box;
    }}
    button {{
      margin-top: 12px;
      width: 100%;
      padding: 12px;
      background: #2563eb;
      color: #fff;
      border: none;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
    }}
    .error {{ color: #dc2626; font-size: 0.875rem; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Link được bảo vệ mật khẩu</h1>
    <p>Nhập mật khẩu để tiếp tục tới đích.</p>
    {error_html}
    <form method="get">
      <input type="password" name="password" placeholder="Mật khẩu" required autofocus />
      <button type="submit">Tiếp tục</button>
    </form>
  </div>
</body>
</html>"""


