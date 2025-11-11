from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

	# API
	API_TITLE: str = "Maryland Data Engineering API"
	API_VERSION: str = "1.0.0"

	# Database
	DATABASE_URL: Optional[str] = None  # e.g. postgresql+psycopg://user:pass@host:5432/dbname
	POSTGRES_HOST: str = "postgres"
	POSTGRES_PORT: int = 5432
	POSTGRES_DB: str = "datawarehouse"
	POSTGRES_USER: str = "postgres"
	POSTGRES_PASSWORD: str = "postgres"

	# CORS (open by default for internal use)
	ALLOW_ORIGINS: str = "*"
	ALLOW_HEADERS: str = "*"
	ALLOW_METHODS: str = "*"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()


