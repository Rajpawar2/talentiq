import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentIQ"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database: Supports SQLite (zero-config local dev) or PostgreSQL (production/docker)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./talentiq.db")
    
    # Redis (Optional in local mock mode, used for task caching/pubsub)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "talentiq-super-secret-key-production-grade-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI Engine Configuration
    AI_MOCK_MODE: bool = os.getenv("AI_MOCK_MODE", "true").lower() in ("true", "1", "yes")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")  # mock | openai | gemini
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    
    # Speech-to-Text Configuration
    STT_PROVIDER: str = os.getenv("STT_PROVIDER", "mock")  # mock | openai_whisper | browser
    STT_API_KEY: str = os.getenv("STT_API_KEY", "")
    
    # File uploads
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads/resumes")
    
    # Email Service Configuration
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "smtp")
    EMAIL_MOCK_MODE: bool = os.getenv("EMAIL_MOCK_MODE", "true").lower() in ("true", "1", "yes")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@talentiq.dev")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "TalentIQ")

    # OTP Security Configuration
    OTP_EXPIRE_MINUTES: int = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
    OTP_RESEND_COOLDOWN_SECONDS: int = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "60"))
    OTP_MAX_ATTEMPTS: int = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:80",
        "http://localhost",
    ]

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"
    }

settings = Settings()
