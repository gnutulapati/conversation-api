from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "AI Conversation API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database (Supabase)
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL: str  # Creating asyncpg connection string if needed directly, or rely on supabase-py

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM Provider (Default: Groq)
    GROQ_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    
    # Cors
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

settings = Settings()
