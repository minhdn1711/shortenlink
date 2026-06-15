import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Link
from app.schemas import BulkCreateLinkRequest, CreateLinkRequest, LinkResponse
from app.utils.assets import normalize_meta_image_url
from app.utils.domain import normalize_domain
from app.utils.security import hash_password

ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int | None = None) -> str:
    size = length or settings.code_length
    return "".join(secrets.choice(ALPHABET) for _ in range(size))


def build_short_url(code: str, custom_domain: str | None = None) -> str:
    base = (custom_domain or settings.short_base_url).rstrip("/")
    return f"{base}/{code}"


def resolve_custom_domain(domain: str | None) -> str:
    if domain:
        return normalize_domain(domain)
    return settings.short_base_url


def to_link_response(link: Link) -> LinkResponse:
    return LinkResponse(
        code=link.code,
        original_url=link.original_url,
        short_url=build_short_url(link.code, link.custom_domain),
        short_domain=link.custom_domain,
        redirect_type=link.redirect_type,
        description=link.description,
        channel=link.channel,
        has_password=bool(link.password_hash),
        meta_title=link.meta_title,
        meta_description=link.meta_description,
        meta_image_url=normalize_meta_image_url(link.meta_image_url),
        click_count=link.click_count,
        created_at=link.created_at,
    )


def _link_from_payload(payload: CreateLinkRequest, code: str, custom_domain: str) -> Link:
    return Link(
        code=code,
        original_url=str(payload.url),
        custom_domain=custom_domain,
        redirect_type=payload.redirect_type,
        description=payload.description,
        channel=payload.channel,
        password_hash=hash_password(payload.password) if payload.password else None,
        meta_title=payload.meta_title,
        meta_description=payload.meta_description,
        meta_image_url=payload.meta_image_url,
    )


async def get_link_by_code(db: AsyncSession, code: str) -> Link | None:
    result = await db.execute(select(Link).where(Link.code == code))
    return result.scalar_one_or_none()


async def create_link(db: AsyncSession, payload: CreateLinkRequest) -> LinkResponse:
    custom_domain = resolve_custom_domain(payload.domain)

    if payload.custom_code:
        existing = await get_link_by_code(db, payload.custom_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom code is already taken",
            )
        code = payload.custom_code
    else:
        code = await _generate_unique_code(db)

    link = _link_from_payload(payload, code, custom_domain)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return to_link_response(link)


async def create_links_bulk(db: AsyncSession, payload: BulkCreateLinkRequest) -> list[LinkResponse]:
    custom_domain = resolve_custom_domain(payload.domain)
    created: list[Link] = []

    for url in payload.urls:
        code = await _generate_unique_code(db)
        item = CreateLinkRequest(
            url=url,
            domain=payload.domain,
            redirect_type=payload.redirect_type,
            description=payload.description,
            channel=payload.channel,
        )
        link = _link_from_payload(item, code, custom_domain)
        db.add(link)
        created.append(link)

    await db.commit()
    for link in created:
        await db.refresh(link)

    return [to_link_response(link) for link in created]


async def _generate_unique_code(db: AsyncSession) -> str:
    for _ in range(10):
        code = generate_code()
        if await get_link_by_code(db, code) is None:
            return code
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not generate a unique short code",
    )


async def list_links(db: AsyncSession, limit: int = 20, offset: int = 0) -> tuple[list[LinkResponse], int]:
    count_result = await db.execute(select(func.count()).select_from(Link))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Link).order_by(Link.created_at.desc()).limit(limit).offset(offset)
    )
    links = result.scalars().all()
    return [to_link_response(link) for link in links], total


async def increment_click_count(db: AsyncSession, link: Link) -> None:
    link.click_count += 1
    await db.commit()


async def delete_link(db: AsyncSession, code: str) -> None:
    link = await get_link_by_code(db, code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    await db.delete(link)
    await db.commit()
