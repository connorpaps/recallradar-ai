from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


PORTFOLIO_FRONTEND_ORIGIN = "https://recallradar-ai.vercel.app"


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./recallradar.db"
    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    openfda_api_key: str | None = None
    openfda_food_enforcement_url: str = "https://api.fda.gov/food/enforcement.json"
    openfda_refresh_minutes: int = 30
    max_upload_mb: int = 2
    max_csv_rows: int = 5000
    max_upload_errors: int = 25
    rate_limit_window_seconds: int = 60
    rate_limit_read_per_window: int = 120
    rate_limit_action_per_window: int = 12
    rate_limit_upload_per_window: int = 5
    ai_provider: str = "local"
    hf_api_token: str | None = None
    hf_provider: str = "hf-inference"
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    hf_summary_model: str = "facebook/bart-large-cnn"
    enable_semantic_matching: bool = False
    enable_ai_summaries: bool = False
    enable_demo_recall_seed: bool = False

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        configured = [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]
        if PORTFOLIO_FRONTEND_ORIGIN not in configured:
            configured.append(PORTFOLIO_FRONTEND_ORIGIN)
        return configured

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def rate_limit_per_window(self) -> dict[str, int]:
        return {
            "read": self.rate_limit_read_per_window,
            "action": self.rate_limit_action_per_window,
            "upload": self.rate_limit_upload_per_window,
        }

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
