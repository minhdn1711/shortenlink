from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

RedirectType = Literal["direct"]


class CreateLinkRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = Field(default=None, max_length=64)
    domain: str | None = Field(default=None, max_length=255)
    redirect_type: RedirectType = "direct"
    description: str | None = Field(default=None, max_length=500)
    channel: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, max_length=128)
    meta_title: str | None = Field(default=None, max_length=200)
    meta_description: str | None = Field(default=None, max_length=500)
    meta_image_url: str | None = Field(default=None, max_length=2048)

    @field_validator("url", mode="before")
    @classmethod
    def normalize_url(cls, value: object) -> object:
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed and not trimmed.startswith(("http://", "https://")):
                return f"https://{trimmed}"
        return value

    @field_validator("domain", "description", "channel", "meta_title", "meta_description", "meta_image_url")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        code = value.strip()
        if not code:
            return None
        if not code.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Custom code may only contain letters, numbers, hyphens, and underscores")
        return code


class BulkCreateLinkRequest(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1, max_length=20)
    domain: str | None = None
    redirect_type: RedirectType = "direct"
    channel: str | None = None
    description: str | None = None


class LinkResponse(BaseModel):
    code: str
    original_url: str
    short_url: str
    short_domain: str | None = None
    redirect_type: str
    description: str | None = None
    channel: str | None = None
    has_password: bool = False
    meta_title: str | None = None
    meta_description: str | None = None
    meta_image_url: str | None = None
    click_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LinkListResponse(BaseModel):
    items: list[LinkResponse]
    total: int
