from app.db.session import async_session
from app.core.redis_utils import redis_client
from sqlalchemy import text
from datetime import datetime

async def check_database() -> dict:
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "error": None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis() -> dict:
    try:
        await redis_client.ping()
        return {"status": "healthy", "error": None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def get_health_status() -> dict:
    db_status = await check_database()
    redis_status = await check_redis()
    all_healthy = db_status["status"] == "healthy" and redis_status["status"] == "healthy"
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "redis": redis_status,
        }
    }
