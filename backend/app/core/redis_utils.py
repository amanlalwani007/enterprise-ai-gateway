import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def check_budget_cache(user_api_key: str):
    if not settings.BUDGET_ENABLED:
        return True, None

    remaining = await redis_client.get(f"budget:{user_api_key}")
    if remaining is None:
        return True, settings.DEFAULT_BUDGET

    return float(remaining) > 0, float(remaining)

async def update_budget_cache(user_api_key: str, cost: float):
    if not settings.BUDGET_ENABLED:
        return
    await redis_client.decrbyfloat(f"budget:{user_api_key}", cost)

async def check_rate_limit(user_api_key: str):
    if not settings.RATE_LIMIT_ENABLED:
        return True

    key = f"ratelimit:{user_api_key}"
    requests = await redis_client.incr(key)
    if requests == 1:
        await redis_client.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)

    return requests <= settings.RATE_LIMIT_REQUESTS
