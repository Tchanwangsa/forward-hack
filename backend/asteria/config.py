"""Settings, loaded from the environment (.env at repo root). See ../../.env.example."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = "postgresql+psycopg://asteria:asteria@localhost:5433/asteria"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-5"

    mock_company_dir: str = "mock-company"

    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    @property
    def mock_company_path(self) -> Path:
        return REPO_ROOT / self.mock_company_dir

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
