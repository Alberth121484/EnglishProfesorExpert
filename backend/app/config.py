from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "English Profesor Expert"
    debug: bool = False
    secret_key: str = "change-this-secret-key"
    api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/english_tutor"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Telegram
    telegram_bot_token: str = ""
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    
    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "kC1WIuSSgwH2T8iOV4iJ"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
