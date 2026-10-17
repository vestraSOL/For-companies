from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "study-crm-python-backend"
    app_env: Literal["local", "dev", "test", "prod"] = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_prefix: str = "/api/v1"
    debug: bool = True

    database_url: str = Field(
        default="postgresql+asyncpg://study:study@localhost:5432/study_python_backend",
    )
    sql_echo: bool = False

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24

    cors_allow_origins: str = "*"
    admin_title: str = "Study CRM Admin"
    admin_base_url: str = "/admin"
    admin_session_secret: str = ""
    admin_allowed_emails: str = ""
    bootstrap_admin_email: str = "admin@example.com"
    bootstrap_admin_password: str = "admin"

    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BROKERS: str = "localhost:9092"
    enable_metrics: bool = False

    create_reserved_catalogs_on_company_create: bool = False


@lru_cache
def get_settings() -> Settings:
    """Возвращает кэшированный объект настроек"""

    return Settings()
