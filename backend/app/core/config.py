from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@db:5432/gateway"
    REDIS_URL: str = "redis://redis:6379/0"
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
