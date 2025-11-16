from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://alfa_user:alfa_pass@localhost:5432/alfa_db"
    
    # Security
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBAPP_URL: str = "http://localhost:3000/tg-app"

    # Superuser
    SUPERUSER_EMAIL: str = "admin@example.com"
    SUPERUSER_PASSWORD: str = "admin123"
    SUPERUSER_TELEGRAM_ID: Optional[int] = None

    # LLM - LLM7.io API (Free LLM gateway)
    LLM7_API_KEY: str = ""  # Get free token from https://token.llm7.io
    LLM7_BASE_URL: str = "https://api.llm7.io/v1"
    LLM7_MODEL: str = "gpt-4o-mini"  # Default model

    # Autonomous Features
    ENABLE_AUTONOMOUS_ACTIONS: bool = True
    MORNING_BRIEFING_TIME: str = "06:00"
    DECISION_THRESHOLD_AMOUNT: int = 10000

    # Memory
    CHROMADB_PATH: str = "./chroma_data"
    MAX_CONTEXT_TOKENS: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()