"""Proxy redirect + ảnh upload → backend. Tunnel phanmemcongnghevip.online → port này."""

import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
PORT = int(os.getenv("PORT", "9004"))

app = FastAPI(title="ShortenLink Redirect", docs_url=None, redoc_url=None)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "role": "redirect", "backend": BACKEND_URL}


async def _proxy_to_backend(path: str, request: Request) -> Response:
    headers: dict[str, str] = {}
    user_agent = request.headers.get("user-agent")
    if user_agent:
        headers["user-agent"] = user_agent
    query = str(request.url.query)
    url = f"{BACKEND_URL}{path}"
    if query:
        url = f"{url}?{query}"

    async with httpx.AsyncClient(follow_redirects=False, timeout=15.0) as client:
        upstream = await client.get(url, headers=headers)

    location = upstream.headers.get("location")
    if location and 300 <= upstream.status_code < 400:
        return RedirectResponse(
            url=location,
            status_code=upstream.status_code,
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )

    out_headers: dict[str, str] = {}
    if location:
        out_headers["location"] = location

    content_type = upstream.headers.get("content-type")
    media_type = content_type.split(";")[0].strip() if content_type else None

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=out_headers,
        media_type=media_type,
    )


@app.get("/uploads/{filename:path}")
async def proxy_uploads(filename: str, request: Request) -> Response:
    return await _proxy_to_backend(f"/uploads/{filename}", request)


@app.get("/{code}")
async def proxy_redirect(code: str, request: Request) -> Response:
    if code in {"health", "favicon.ico", "robots.txt"}:
        return Response(status_code=404)
    return await _proxy_to_backend(f"/{code}", request)
