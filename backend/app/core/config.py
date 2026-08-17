import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Resolve backend/.env by absolute path so config loads correctly regardless of the
# process's current working directory (the documented startup command runs uvicorn
# from the project root via --app-dir backend, not from inside backend/ itself).
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Sales Analytics Dashboard"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./sales_dashboard.db",
        description="PostgreSQL / Supabase connection string or SQLite fallback"
    )

    # Security & JWT
    JWT_SECRET: str = Field(
        default="super-secret-jwt-key-for-cse4104-dashboard-development-2026",
        description="Secret key for JWT token encoding/decoding"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # AI Configuration
    AI_PROVIDER: str = "grounded"  # "gemini", "openai", or "grounded"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"
    OPENAI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origin_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="allow")


settings = Settings()
