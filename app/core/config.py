from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI AML Investigation Assistant"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+psycopg://aml:aml@localhost:5432/aml_assistant", alias="DATABASE_URL"
    )

    openai_api_key: str = Field(default="test-key", alias="OPENAI_API_KEY")
    openai_model_analysis: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL_ANALYSIS")
    openai_model_reports: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL_REPORTS")
    openai_request_timeout_seconds: float = Field(
        default=30.0, alias="OPENAI_REQUEST_TIMEOUT_SECONDS"
    )

    payload_max_transactions: int = 5000
    save_raw_case_json: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
