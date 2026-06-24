import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.models.usage import Base
from app.models.enterprise import Tenant, Team, User
from app.models.cache import SemanticCache
from app.models.guardrail_log import GuardrailLog
from app.core.config import settings

EMBEDDING_DIMS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}

async def init_db():
    dim = EMBEDDING_DIMS.get(settings.EMBEDDING_MODEL, 1536)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text(f"ALTER TABLE semantic_cache ADD COLUMN IF NOT EXISTS embedding vector({dim})"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_semantic_cache_embedding ON semantic_cache USING hnsw (embedding vector_cosine_ops)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_semantic_cache_query_type ON semantic_cache (query_type)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_semantic_cache_expires ON semantic_cache (expires_at)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_semantic_cache_keywords ON semantic_cache USING gin (keywords)"))
        except Exception as e:
            print(f"Schema setup warning: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
