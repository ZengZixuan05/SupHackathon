from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    max_iterations: int = 5
    generated_dir: Path = Path("generated")


settings = Settings()
settings.generated_dir.mkdir(parents=True, exist_ok=True)
