from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "Pure Lioraa API"
    APP_ENV: str = "local"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = []

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "lioraa"
    POSTGRES_PASSWORD: str = "change-me"
    POSTGRES_DB: str = "lioraa"
    DATABASE_POOL_SIZE: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # AWS / Bedrock
    AWS_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BEDROCK_CHAT_MODEL_ID: str = "amazon.nova-lite-v1:0"
    BEDROCK_EMBEDDING_MODEL_ID: str = "amazon.titan-embed-text-v2:0"
    BEDROCK_GUARDRAIL_ID: str = ""
    BEDROCK_GUARDRAIL_VERSION: str = ""

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "Pure Lioraa <no-reply@purelioraa.com>"

    # Observability
    LOG_LEVEL: str = "INFO"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "pure-lioraa-chatbot"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
