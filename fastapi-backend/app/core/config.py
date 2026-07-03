"""Application configuration settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = Field(default="房屋安全鉴定系统", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/house_safety",
        alias="DATABASE_URL",
    )

    # JWT
    secret_key: str = Field(
        default="your-secret-key-change-in-production", alias="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=10080, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    algorithm: str = "HS256"
    refresh_token_expire_days: int = Field(
        default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Ollama
    ollama_base_url: str = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(default="qwen2.5:7b", alias="OLLAMA_MODEL")

    # WeChat
    wechat_app_id: str = Field(default="your-app-id", alias="WECHAT_APP_ID")
    wechat_app_secret: str = Field(
        default="your-app-secret", alias="WECHAT_APP_SECRET"
    )

    # Aliyun OSS
    oss_access_key_id: str = Field(default="your-key-id", alias="OSS_ACCESS_KEY_ID")
    oss_access_key_secret: str = Field(
        default="your-key-secret", alias="OSS_ACCESS_KEY_SECRET"
    )
    oss_endpoint: str = Field(
        default="oss-cn-hangzhou.aliyuncs.com", alias="OSS_ENDPOINT"
    )
    oss_bucket_name: str = Field(default="your-bucket", alias="OSS_BUCKET_NAME")
    oss_bucket_url: str = Field(default="", alias="OSS_BUCKET_URL")

    # Aliyun SMS
    aliyun_access_key_id: str = Field(
        default="your-key-id", alias="ALIYUN_ACCESS_KEY_ID"
    )
    aliyun_access_key_secret: str = Field(
        default="your-key-secret", alias="ALIYUN_ACCESS_KEY_SECRET"
    )
    aliyun_sms_sign_name: str = Field(
        default="your-sign", alias="ALIYUN_SMS_SIGN_NAME"
    )
    aliyun_sms_template_code: str = Field(
        default="SMS_123456789", alias="ALIYUN_SMS_TEMPLATE_CODE"
    )

    # Email SMTP
    smtp_host: str = Field(default="smtp.qq.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="your-email@qq.com", alias="SMTP_USER")
    smtp_password: str = Field(default="your-auth-code", alias="SMTP_PASSWORD")
    smtp_tls: bool = Field(default=True, alias="SMTP_TLS")
    smtp_from: str = Field(default="", alias="SMTP_FROM")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
