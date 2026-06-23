from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@db:5432/gateway"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # LLM Providers
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Admin
    ADMIN_API_KEY: str = "admin-secret-change-me"

    # Budget & Cost Limiting
    BUDGET_ENABLED: bool = True
    DEFAULT_BUDGET: float = 1000.0
    DEFAULT_COST_PER_REQUEST: float = 0.001

    # Rate Limiting (optional, disabled by default)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Semantic Cache
    CACHE_ENABLED: bool = True
    CACHE_SIMILARITY_THRESHOLD: float = 0.95

    # PII Masking
    PII_MASKING_ENABLED: bool = True

    # Model Routing
    MODEL_ROUTES: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
