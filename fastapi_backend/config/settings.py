"""Application settings and configuration."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "OpenStates FastAPI Backend"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, validation_alias="DEBUG")

    # Server
    host: str = "0.0.0.0"
    port: int = 8001

    # Django Backend
    django_backend_url: str = "http://django:8000"

    # OpenTelemetry
    otel_enabled: bool = True
    otel_service_name: str = "openstates-fastapi"
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_exporter_otlp_insecure: bool = True

    # Prometheus
    prometheus_enabled: bool = True
    prometheus_port: int = 9090

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # CORS
    cors_origins: list[str] = ["*"]

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )


# Global settings instance
settings = Settings()
