import litellm
from pgvector.sqlalchemy import Vector
from sqlalchemy import select, text
from app.db.session import async_session
from app.models.cache import SemanticCache

from app.core.config import settings

EMBEDDING_MODEL = settings.EMBEDDING_MODEL
SIMILARITY_THRESHOLD = settings.CACHE_SIMILARITY_THRESHOLD

async def get_embedding(text: str):
    """
    Generate embedding for a given text using LiteLLM.
    """
    response = await litellm.aembedding(
        model=EMBEDDING_MODEL,
        input=[text]
    )
    return response.data[0].embedding

async def find_semantic_cache(prompt: str):
    """
    Look for a semantically similar prompt in the database.
    """
    embedding = await get_embedding(prompt)
    
    async with async_session() as session:
        # Use pgvector's cosine distance operator <=>
        # 1 - (embedding <=> column) = cosine similarity
        query = text(f"""
            SELECT response_text, 1 - (embedding <=> :embedding) as similarity
            FROM semantic_cache
            WHERE 1 - (embedding <=> :embedding) > :threshold
            ORDER BY similarity DESC
            LIMIT 1
        """)
        
        result = await session.execute(query, {
            "embedding": str(embedding),
            "threshold": SIMILARITY_THRESHOLD
        })
        
        row = result.fetchone()
        if row:
            return row[0] # Return the cached response_text
            
    return None

async def save_to_semantic_cache(prompt: str, response: str, model: str):
    """
    Save a new prompt-response pair to the semantic cache.
    """
    embedding = await get_embedding(prompt)
    
    async with async_session() as session:
        cache_entry = text("""
            INSERT INTO semantic_cache (prompt_text, response_text, model, embedding, created_at)
            VALUES (:prompt, :response, :model, :embedding, NOW())
        """)
        
        await session.execute(cache_entry, {
            "prompt": prompt,
            "response": response,
            "model": model,
            "embedding": str(embedding)
        })
        await session.commit()
