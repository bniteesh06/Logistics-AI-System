"""
Centralized, environment-driven configuration.
All tunables live here — nothing else in the codebase should read os.environ directly.
"""
import os
from functools import lru_cache


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings:
    # ── App metadata ────────────────────────────────────────────────────
    app_name: str = os.getenv("APP_NAME", "AI Logistics Optimization System")
    app_version: str = os.getenv("APP_VERSION", "2.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")  # development | staging | production

    # ── CORS ─────────────────────────────────────────────────────────────
    # In production, set ALLOWED_ORIGINS to a comma-separated list, e.g.
    # "https://app.example.com,https://staging.example.com"
    allowed_origins: list[str] = _split_csv(os.getenv("ALLOWED_ORIGINS", "*"))

    # ── Logging ──────────────────────────────────────────────────────────
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_json: bool = os.getenv("LOG_JSON", "false").lower() == "true"

    # ── Data generation ──────────────────────────────────────────────────
    history_days: int = int(os.getenv("HISTORY_DAYS", "120"))
    data_seed: int = int(os.getenv("DATA_SEED", "42"))

    # ── Request limits ───────────────────────────────────────────────────
    max_forecast_horizon: int = int(os.getenv("MAX_FORECAST_HORIZON", "30"))
    min_forecast_horizon: int = int(os.getenv("MIN_FORECAST_HORIZON", "3"))
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() is constructed once per process."""
    return Settings()
