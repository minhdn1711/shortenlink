from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./shortenlink.db"
    short_base_url: str = "https://phanmemcongnghevip.online"
    cors_origins: str = (
        "https://adminphanmemvip.xyz,"
        "https://www.adminphanmemvip.xyz,"
        "http://adminphanmemvip.xyz,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )
    cors_origin_regex: str = (
        r"https?://(.*\.)?phanmemcongnghevip\.online(:\d+)?"
        r"|https?://(.*\.)?adminphanmemvip\.xyz(:\d+)?"
        r"|https?://localhost(:\d+)?"
        r"|https?://127\.0\.0\.1(:\d+)?"
    )
    code_length: int = 6
    max_custom_code_length: int = 32
    default_domain: str = "phanmemcongnghevip.online"
    upload_dir: str = "uploads"
    max_upload_bytes: int = 512_000
    # Ảnh OG: dùng API domain (cùng backend :8000) để Facebook luôn tải được
    public_asset_base_url: str = "https://api.adminphanmemvip.xyz"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
