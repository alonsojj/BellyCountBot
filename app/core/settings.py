from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    GROQ_API_KEY: str
    SERVER_URL: str
    INSTANCE_ID: Optional[str] = None
    AUTHENTICATION_API_KEY: str
    BOT_USERNAME: str
    BOT_PASSWORD: str
    ACCESS_CONTROL_MODE: str = "DISABLE"
    EMAIL_SENDER_ADDRESS: str
    EMAIL_SENDER_PASSWORD: str

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()
