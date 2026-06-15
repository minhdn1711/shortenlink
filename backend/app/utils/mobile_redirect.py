import json
import re
from urllib.parse import quote, urlparse

MOBILE_UA_PATTERN = re.compile(
    r"android|iphone|ipad|ipod|mobile|webos|blackberry|iemobile|opera mini",
    re.IGNORECASE,
)

ANDROID_UA_PATTERN = re.compile(r"android", re.IGNORECASE)
IOS_UA_PATTERN = re.compile(r"iphone|ipad|ipod", re.IGNORECASE)

CRAWLER_UA_PATTERN = re.compile(
    r"facebookexternalhit|facebot|meta-externalfetcher|meta-externalagent|"
    r"twitterbot|linkedinbot|slackbot|discordbot|whatsapp|telegrambot|"
    r"googlebot|bingbot|applebot|embedly|pinterest|vkshare|"
    r"preview|bot|crawler|spider",
    re.IGNORECASE,
)

# Trình duyệt trong app (FB, Zalo, Messenger…) — không dùng shopeevn:// / intent://
# vì sẽ hiện popup "Rời khỏi Facebook?". Redirect HTTPS → Universal Link mở app mượt hơn.
IN_APP_SOCIAL_BROWSER_PATTERN = re.compile(
    r"FBAN|FBAV|FB_IAB|FBIOS|FB4A|Messenger|Instagram|Line/|MicroMessenger|"
    r"Zalo|Twitter|LinkedInApp|BytedanceWebview|TikTok",
    re.IGNORECASE,
)

APP_RULES: list[dict[str, object]] = [
    {
        "id": "shopee",
        "hosts": (
            "shopee.vn",
            "www.shopee.vn",
            "shopee.com",
            "www.shopee.com",
            "shp.ee",
            "s.shopee.vn",
        ),
        "android_package": "com.shopee.vn",
        "ios_app_store_id": "959840394",
        "title": "Shopee",
        "color": "#f53d2d",
    },
    {
        "id": "tiktok",
        "hosts": (
            "tiktok.com",
            "www.tiktok.com",
            "vm.tiktok.com",
            "vt.tiktok.com",
            "v.tiktok.com",
            "m.tiktok.com",
            "tiktokv.com",
        ),
        "android_package": "com.zhiliaoapp.musically",
        "ios_app_store_id": "835599320",
        "title": "TikTok",
        "color": "#010101",
    },
]


def is_mobile_user_agent(user_agent: str) -> bool:
    return bool(user_agent and MOBILE_UA_PATTERN.search(user_agent))


def is_android_user_agent(user_agent: str) -> bool:
    return bool(user_agent and ANDROID_UA_PATTERN.search(user_agent))


def is_ios_user_agent(user_agent: str) -> bool:
    return bool(user_agent and IOS_UA_PATTERN.search(user_agent))


def is_social_crawler(user_agent: str) -> bool:
    return bool(user_agent and CRAWLER_UA_PATTERN.search(user_agent))


def is_in_app_social_browser(user_agent: str) -> bool:
    return bool(user_agent and IN_APP_SOCIAL_BROWSER_PATTERN.search(user_agent))


def _host_matches(url: str, hosts: tuple[str, ...]) -> bool:
    try:
        host = urlparse(url).netloc.lower().removeprefix("www.")
        allowed = {h.removeprefix("www.") for h in hosts}
        return host in allowed or any(host.endswith(f".{h}") for h in allowed)
    except Exception:
        return False


def detect_app_target(url: str) -> dict[str, object] | None:
    for rule in APP_RULES:
        hosts = rule["hosts"]
        if isinstance(hosts, tuple) and _host_matches(url, hosts):
            return rule
    return None


def should_serve_crawler_preview(
    target_url: str, has_custom_og: bool, user_agent: str
) -> bool:
    """Facebook bot: OG + App Links cho Shopee/TikTok (kể cả chưa upload ảnh meta)."""
    if not is_social_crawler(user_agent):
        return False
    return has_custom_og or detect_app_target(target_url) is not None


def should_use_direct_app_redirect(url: str, user_agent: str) -> bool:
    """
    Mobile + Shopee/TikTok: chỉ 302 sang link HTTPS gốc.
    App mở qua Universal Link — kể cả khi bấm từ Facebook, không cần shopeevn://.
    """
    if not is_mobile_user_agent(user_agent) or is_social_crawler(user_agent):
        return False
    return detect_app_target(url) is not None


def should_use_app_bridge(url: str, user_agent: str) -> bool:
    """Không dùng trang trung gian intent/scheme — gây popup Facebook."""
    return False


def _build_android_intent(target_url: str, package: str) -> str:
    parsed = urlparse(target_url)
    path_with_query = parsed.path or "/"
    if parsed.query:
        path_with_query += f"?{parsed.query}"
    return (
        f"intent://{parsed.netloc}{path_with_query}"
        f"#Intent;scheme=https;package={package};"
        f"S.browser_fallback_url={quote(target_url, safe='')};end"
    )


def _build_ios_app_url(target_url: str, app_id: str) -> str:
    encoded = quote(target_url, safe="")
    if app_id == "shopee":
        return f"shopeevn://home?navRoute={encoded}"
    if app_id == "tiktok":
        return f"snssdk1233://webview?url={encoded}"
    return f"{app_id}://open?url={encoded}"


def build_app_bridge_html(target_url: str, user_agent: str) -> str:
    rule = detect_app_target(target_url) or APP_RULES[0]
    app_id = str(rule["id"])
    title = str(rule["title"])
    color = str(rule["color"])
    android_package = str(rule["android_package"])

    intent_url = _build_android_intent(target_url, android_package)
    ios_app_url = _build_ios_app_url(target_url, app_id)

    safe_web = json.dumps(target_url)
    safe_intent = json.dumps(intent_url)
    safe_ios = json.dumps(ios_app_url)
    escaped_intent = intent_url.replace("&", "&amp;").replace('"', "&quot;")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Đang mở {title}...</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      background: {color};
      color: #fff;
      display: flex;
      min-height: 100vh;
      align-items: center;
      justify-content: center;
      margin: 0;
      text-align: center;
      padding: 24px;
    }}
    .btn {{
      display: inline-block;
      margin-top: 16px;
      padding: 14px 28px;
      background: #fff;
      color: #111;
      font-weight: 700;
      border-radius: 12px;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div>
    <p>Đang mở app {title}...</p>
    <a id="open-app" class="btn" href="{escaped_intent}">Mở app {title}</a>
    <p style="margin-top:12px;font-size:13px;opacity:0.9">
      <a id="open-web" style="color:#fff">Mở trên web</a>
    </p>
  </div>
  <script>
    (function() {{
      const webUrl = {safe_web};
      const intentUrl = {safe_intent};
      const iosAppUrl = {safe_ios};
      const isAndroid = /android/i.test(navigator.userAgent);
      const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
      const appUrl = isIOS ? iosAppUrl : intentUrl;

      document.getElementById("open-web").href = webUrl;
      const appBtn = document.getElementById("open-app");
      appBtn.href = isAndroid ? intentUrl : (isIOS ? iosAppUrl : webUrl);

      function openApp() {{
        if (isIOS) {{
          const iframe = document.createElement("iframe");
          iframe.style.cssText = "display:none;width:0;height:0;border:0";
          iframe.src = iosAppUrl;
          document.body.appendChild(iframe);
        }}
        window.location.href = appUrl;
      }}

      openApp();
      setTimeout(function() {{
        if (document.visibilityState !== "hidden") {{
          window.location.replace(webUrl);
        }}
      }}, 2500);
    }})();
  </script>
</body>
</html>"""


def should_use_shopee_app_bridge(url: str, user_agent: str) -> bool:
    return should_use_app_bridge(url, user_agent)


def build_shopee_bridge_html(target_url: str) -> str:
    return build_app_bridge_html(target_url, "Mozilla/5.0 (Linux; Android 14)")
