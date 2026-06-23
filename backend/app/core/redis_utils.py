import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def check_budget_cache(user_api_key: str):
    """
    Check if user has remaining budget in Redis.
    If not in Redis, this would trigger a DB lookup and populate the cache.
    """
    # Key format: budget:{api_key}
    remaining = await redis_client.get(f"budget:{user_api_key}")
    if remaining is None:
        # For Phase 2 MVP, we'll assume they have budget if not in Redis
        # In a real system, we'd fetch from DB here
        return True, 1000.0 
    
    return float(remaining) > 0, float(remaining)

async def update_budget_cache(user_api_key: str, cost: float):
    """
    Atomically decrement budget in Redis.
    """
    await redis_client.decrby(f"budget:{user_api_key}", cost)

async def check_rate_limit(user_api_key: str, limit: int = 60):
    """
    Simple sliding window rate limiter in Redis.
    """
    key = f"ratelimit:{user_api_key}"
    requests = await redis_client.incr(key)
    if requests == 1:
        await redis_client.expire(key, 60) # 1 minute window
    
    return requests <= limit
