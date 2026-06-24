import litellm
from sqlalchemy import text
from app.db.session import async_session
from app.core.config import settings
from app.core.query_classifier import classify_query, get_strategy, extract_keywords
from datetime import datetime, timedelta

EMBEDDING_MODEL = settings.EMBEDDING_MODEL

async def get_embedding(text: str):
    response = await litellm.aembedding(
        model=EMBEDDING_MODEL,
        input=[text]
    )
    return response.data[0].embedding

def _adaptive_threshold(prompt: str, base_threshold: float) -> float:
    word_count = len(prompt.split())
    if word_count <= 5:
        return min(base_threshold + 0.04, 0.99)
    elif word_count <= 15:
        return min(base_threshold + 0.02, 0.98)
    elif word_count >= 50:
        return max(base_threshold - 0.05, 0.75)
    return base_threshold

async def find_semantic_cache(prompt: str, model: str | None = None):
    query_type = classify_query(prompt)
    strategy = get_strategy(query_type)
    base_threshold = strategy["threshold"]
    threshold = _adaptive_threshold(prompt, base_threshold)
    keywords = extract_keywords(prompt)
    embedding = await get_embedding(prompt)

    async with async_session() as session:
        stage = "vector"
        row = None

        if keywords and strategy["use_keyword_fallback"]:
            stage = "keyword"
            kw_filter = text("""
                SELECT response_text, 1 - (embedding <=> :embedding) as similarity
                FROM semantic_cache
                WHERE model = :model
                  AND keywords && :keywords
                  AND (expires_at IS NULL OR expires_at > NOW())
                  AND 1 - (embedding <=> :embedding) > :threshold
                ORDER BY similarity DESC
                LIMIT 1
            """)
            result = await session.execute(kw_filter, {
                "embedding": str(embedding),
                "model": model or "",
                "keywords": keywords,
                "threshold": threshold - 0.05,
            })
            row = result.fetchone()

        if not row:
            stage = "vector"
            vec_query = text("""
                SELECT response_text, 1 - (embedding <=> :embedding) as similarity
                FROM semantic_cache
                WHERE model = :model
                  AND query_type = :query_type
                  AND (expires_at IS NULL OR expires_at > NOW())
                  AND 1 - (embedding <=> :embedding) > :threshold
                ORDER BY similarity DESC
                LIMIT 1
            """)
            result = await session.execute(vec_query, {
                "embedding": str(embedding),
                "model": model or "",
                "query_type": query_type,
                "threshold": threshold,
            })
            row = result.fetchone()

        if not row and query_type != "factual":
            vec_query = text("""
                SELECT response_text, 1 - (embedding <=> :embedding) as similarity
                FROM semantic_cache
                WHERE model = :model
                  AND (expires_at IS NULL OR expires_at > NOW())
                  AND 1 - (embedding <=> :embedding) > :threshold
                ORDER BY similarity DESC
                LIMIT 1
            """)
            result = await session.execute(vec_query, {
                "embedding": str(embedding),
                "model": model or "",
                "threshold": max(threshold - 0.10, 0.70),
            })
            row = result.fetchone()
            if row:
                stage = "vector_fallback"

        if row:
            await session.execute(
                text("UPDATE semantic_cache SET hit_count = hit_count + 1 WHERE response_text = :response"),
                {"response": row[0]}
            )
            await session.commit()
            return row[0]

    return None

async def save_to_semantic_cache(prompt: str, response: str, model: str):
    query_type = classify_query(prompt)
    strategy = get_strategy(query_type)
    threshold = _adaptive_threshold(prompt, strategy["threshold"])
    keywords = extract_keywords(prompt)
    embedding = await get_embedding(prompt)
    ttl = strategy["ttl_seconds"]
    expires_at = datetime.utcnow() + timedelta(seconds=ttl)

    async with async_session() as session:
        # Use raw text query for vector column, ORM for typed columns
        cache_entry = text("""
            INSERT INTO semantic_cache
                (prompt_text, response_text, model, query_type, keywords,
                 similarity_threshold, ttl_seconds, embedding, created_at, expires_at)
            VALUES
                (:prompt, :response, :model, :query_type, :keywords::text[],
                 :threshold, :ttl, :embedding, NOW(), :expires_at)
        """)
        await session.execute(cache_entry, {
            "prompt": prompt,
            "response": response,
            "model": model,
            "query_type": query_type,
            "keywords": keywords,
            "threshold": threshold,
            "ttl": ttl,
            "embedding": str(embedding),
            "expires_at": expires_at,
        })
        await session.commit()

async def get_cache_stats() -> dict:
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT
                query_type,
                COUNT(*) as total,
                SUM(hit_count) as total_hits,
                AVG(similarity_threshold) as avg_threshold,
                MAX(created_at) as newest,
                MIN(created_at) as oldest
            FROM semantic_cache
            GROUP BY query_type
            ORDER BY total DESC
        """))
        rows = result.fetchall()
    stats = {}
    for row in rows:
        stats[row[0]] = {
            "entries": row[1],
            "total_hits": row[2] or 0,
            "avg_threshold": round(float(row[3] or 0), 3),
        }
    return stats
