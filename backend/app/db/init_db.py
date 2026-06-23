import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.models.usage import Base
from app.models.enterprise import Tenant, Team, User
from app.models.cache import SemanticCache

async def init_db():
    async with engine.begin() as conn:
        # 1. Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # 2. Create tables
        # Base.metadata.create_all is sync, so we use run_sync
        await conn.run_sync(Base.metadata.create_all)
        
        # 3. Add vector column manually to avoid SQLAlchemy Vector type issues in early setup
        try:
            await conn.execute(text("ALTER TABLE semantic_cache ADD COLUMN embedding vector(1536)"))
            await conn.execute(text("CREATE INDEX ON semantic_cache USING hnsw (embedding vector_cosine_ops)"))
        except Exception as e:
            print(f"Embedding column might already exist: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
