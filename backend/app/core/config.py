import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "demo"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aicte_fdr.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "demo-secret-key-change-in-production-never-commit-secrets")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    FROZEN_DEMO_CLOCK: str = "2026-10-26T04:30:00Z"
    DISPLAY_TIMEZONE: str = "Asia/Kolkata"
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage_private")
    MOCK_BANK_SERVICE_URL: str = os.getenv("MOCK_BANK_SERVICE_URL", "http://127.0.0.1:8001")
    BANK_SERVICE_TOKEN: str = os.getenv("BANK_SERVICE_TOKEN", "demo-bank-s2s-token-secure-394872190")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
