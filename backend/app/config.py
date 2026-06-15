from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./shortenlink.db"
    short_base_url: str = "https://shortlink.miliwebseo.com"
    cors_origins: str = (
        "https://shortlink.miliwebseo.com,"
        "https://www.shortlink.miliwebseo.com,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )
    cors_origin_regex: str = (
        r"https?://(.*\.)?shortlink\.miliwebseo\.com(:\d+)?"
        r"|https?://localhost(:\d+)?"
        r"|https?://127\.0\.0\.1(:\d+)?"
    )
    code_length: int = 6
    max_custom_code_length: int = 32
    default_domain: str = "shortlink.miliwebseo.com"
    upload_dir: str = "uploads"
    max_upload_bytes: int = 512_000
    public_asset_base_url: str = "https://shortlink.miliwebseo.com"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
