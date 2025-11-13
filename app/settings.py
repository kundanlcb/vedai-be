# settings.py
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database/Redis
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    APP_NAME: str = "vedai"

    # Api keys (optional in dev)
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # LLM and embeddings providers
    LLM_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    EMBEDDINGS_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Security
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        """
        Return the DB URL to use. If DATABASE_URL env is empty or None,
        fall back to a local sqlite file for quick local dev.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # local dev fallback
        return "sqlite+aiosqlite:///./local_dev.db"

# single exported settings instance for whole app
settings = Settings()
