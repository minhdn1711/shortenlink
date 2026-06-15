from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db, init_db
from app.routers import links, uploads
from app.services import link_service
from app.utils.mobile_redirect import (
    should_serve_crawler_preview,
    should_use_direct_app_redirect,
)
from app.utils.og_html import build_og_preview_html
from app.utils.redirect_pages import build_password_gate_html
from app.utils.security import verify_password

api_prefix = "/api/links"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="ShortenLink API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
    expose_headers=["*"],
    max_age=600,
)

app.include_router(links.router, prefix=api_prefix, tags=["links"])
app.include_router(uploads.router, prefix="/api")

upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/{code}", response_model=None)
async def redirect_short_link(
    code: str,
    request: Request,
    password: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if code in {"health", "docs", "openapi.json", "redoc"} or code.startswith("api"):
        raise HTTPException(status_code=404, detail="Not found")

    link = await link_service.get_link_by_code(db, code)
    if link is None:
        raise HTTPException(status_code=404, detail="Short link not found")

    short_url = link_service.build_short_url(link.code, link.custom_domain)

    if link.password_hash:
        if not password or not verify_password(password, link.password_hash):
            return HTMLResponse(
                content=build_password_gate_html(
                    link,
                    error="Mật khẩu không đúng" if password else None,
                ),
                status_code=200,
            )

    target_url = link.original_url
    user_agent = request.headers.get("user-agent", "")
    has_custom_og = bool(link.meta_title or link.meta_description or link.meta_image_url)

    if should_serve_crawler_preview(target_url, has_custom_og, user_agent):
        return HTMLResponse(
            content=build_og_preview_html(
                link,
                short_url,
                settings.public_asset_base_url,
            ),
            status_code=200,
            headers={"Cache-Control": "public, max-age=300"},
        )

    await link_service.increment_click_count(db, link)

    if should_use_direct_app_redirect(target_url, user_agent):
        return RedirectResponse(
            url=target_url,
            status_code=302,
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )

    return RedirectResponse(
        url=target_url,
        status_code=307,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )
