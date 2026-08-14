from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./flagwarden.db"
    telegram_bot_token: str = "development-bot-token"
    telegram_webhook_secret: str = "development-webhook-secret"
    answer_pepper: str = "development-only-change-me"
    miniapp_auth_max_age_seconds: int = 300
    admin_telegram_ids: str = ""
    reviewer_telegram_ids: str = ""
    author_telegram_ids: str = ""
    allow_debug_auth: bool = False
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    miniapp_url: str = "http://127.0.0.1:8000/app/"
    challenge_pack_root: str = "challenge_packs"
    rate_limit_backend: str = "memory"
    redis_url: str = "redis://redis:6379/0"
    otel_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @staticmethod
    def _parse_ids(raw: str) -> set[int]:
        return {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}

    @property
    def admin_ids(self) -> set[int]:
        return self._parse_ids(self.admin_telegram_ids)

    @property
    def reviewer_ids(self) -> set[int]:
        return self._parse_ids(self.reviewer_telegram_ids)

    @property
    def author_ids(self) -> set[int]:
        return self._parse_ids(self.author_telegram_ids)


@lru_cache
def get_settings() -> Settings:
    return Settings()
