from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    original_url: Mapped[str] = mapped_column(String(2048))
    custom_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    redirect_type: Mapped[str] = mapped_column(String(32), default="direct")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    channel: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meta_image_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
