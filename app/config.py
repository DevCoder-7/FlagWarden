from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven application settings.

    Optional platform credentials intentionally default to missing so the app can run in
    local/test mode without Telegram or Meta credentials.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "FlagWarden"
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./ctf_bot.db"
    challenge_data_path: str = "data/challenges.json"
    bot_test_mode: bool = True

    telegram_bot_token: SecretStr | None = None

    whatsapp_verify_token: SecretStr | None = None
    whatsapp_access_token: SecretStr | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_api_version: str = "v20.0"

    llm_provider: str = "none"
    llm_api_key: SecretStr | None = None

    input_max_length: int = Field(default=2000, ge=1, le=10_000)
    answer_rate_limit_count: int = Field(default=5, ge=1, le=100)
    answer_rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)

    @field_validator(
        "telegram_bot_token",
        "whatsapp_verify_token",
        "whatsapp_access_token",
        "whatsapp_phone_number_id",
        "llm_api_key",
        mode="before",
    )
    @classmethod
    def blank_strings_are_missing(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def telegram_enabled(self) -> bool:
        return self.telegram_bot_token is not None

    @property
    def whatsapp_enabled(self) -> bool:
        return all(
            [
                self.whatsapp_verify_token,
                self.whatsapp_access_token,
                self.whatsapp_phone_number_id,
            ]
        )

    @property
    def llm_enabled(self) -> bool:
        return self.llm_provider.lower() != "none" and self.llm_api_key is not None

    def secret_value(self, secret: SecretStr | str | None) -> str | None:
        if isinstance(secret, SecretStr):
            return secret.get_secret_value()
        return secret

    def missing_whatsapp_vars(self) -> list[str]:
        missing: list[str] = []
        if not self.whatsapp_verify_token:
            missing.append("WHATSAPP_VERIFY_TOKEN")
        if not self.whatsapp_access_token:
            missing.append("WHATSAPP_ACCESS_TOKEN")
        if not self.whatsapp_phone_number_id:
            missing.append("WHATSAPP_PHONE_NUMBER_ID")
        return missing

    def redacted_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        for key in list(data):
            if "token" in key or "key" in key:
                data[key] = "***redacted***" if data[key] else None
        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
