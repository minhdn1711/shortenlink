from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

_NEW_COLUMNS: dict[str, str] = {
    "custom_domain": "VARCHAR(255)",
    "redirect_type": "VARCHAR(32) DEFAULT 'direct'",
    "description": "VARCHAR(500)",
    "channel": "VARCHAR(100)",
    "password_hash": "VARCHAR(64)",
    "meta_title": "VARCHAR(200)",
    "meta_description": "VARCHAR(500)",
    "meta_image_url": "VARCHAR(2048)",
}


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_link_columns(conn)


async def _ensure_link_columns(conn) -> None:
    if conn.dialect.name != "sqlite":
        return
    result = await conn.execute(text("PRAGMA table_info(links)"))
    columns = {row[1] for row in result.fetchall()}
    for name, sql_type in _NEW_COLUMNS.items():
        if name not in columns:
            await conn.execute(text(f"ALTER TABLE links ADD COLUMN {name} {sql_type}"))
