"""Módulo de configurações centrais da aplicação."""
import os
from pydantic import BaseModel


class Settings(BaseModel):
    """Configurações da aplicação."""
    PROJECT_NAME: str = "Gestão de Patrimônio e Suporte"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-1234567890")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./internal_management.db"
    )
    RATE_LIMIT_MAX_ATTEMPTS: int = 10
    RATE_LIMIT_WINDOW_MINUTES: int = 15


settings = Settings()
