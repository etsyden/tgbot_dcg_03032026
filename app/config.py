import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = ""
    WEBHOOK_SECRET: str = ""
    WEBHOOK_URL: str = ""
    ADMIN_CHAT_ID: int = 0

    DATABASE_URL: str = ""

    BITRIX24_URL: str = ""
    BITRIX24_WEBHOOK: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = ""

    CLINIC_PHONE: str = "+7 (999) 123-45-67"
    CLINIC_ADDRESS: str = "г. Москва, ул. Примерная, д. 10"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
