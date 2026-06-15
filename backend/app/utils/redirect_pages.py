import json

from app.models import Link
from app.utils.security import verify_password


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


