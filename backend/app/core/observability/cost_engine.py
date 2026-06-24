from datetime import datetime, timedelta
from sqlalchemy import text, select, func
from app.db.session import async_session
from app.models.usage import RequestLog


async def get_cost_summary(team: str | None = None, from_date: str | None = None, to_date: str | None = None) -> dict:
    async with async_session() as session:
        conditions = ["1=1"]
        params: dict = {}

        if from_date:
            conditions.append("created_at >= :from_date")
            params["from_date"] = datetime.fromisoformat(from_date)
        if to_date:
            conditions.append("created_at <= :to_date")
            params["to_date"] = datetime.fromisoformat(to_date)

        where_clause = " AND ".join(conditions)

        result = await session.execute(text(f"""
            SELECT
                COALESCE(SUM(cost), 0) as total_cost,
                COALESCE(SUM(total_tokens), 0) as total_tokens,
                COALESCE(SUM(prompt_tokens), 0) as total_prompt_tokens,
                COALESCE(SUM(completion_tokens), 0) as total_completion_tokens,
                COUNT(*) as total_requests,
                COUNT(DISTINCT model) as unique_models,
                COUNT(DISTINCT user_id) as unique_users
            FROM request_logs
            WHERE {where_clause}
        """), params)
        row = result.fetchone()

        by_model = await session.execute(text(f"""
            SELECT model,
                   COUNT(*) as requests,
                   COALESCE(SUM(cost), 0) as cost,
                   COALESCE(SUM(total_tokens), 0) as tokens,
                   AVG(cost) as avg_cost
            FROM request_logs
            WHERE {where_clause}
            GROUP BY model
            ORDER BY cost DESC
            LIMIT 20
        """), params)
        models = [dict(r._mapping) for r in by_model]

        daily = await session.execute(text(f"""
            SELECT DATE(created_at) as date,
                   COALESCE(SUM(cost), 0) as cost,
                   COALESCE(SUM(total_tokens), 0) as tokens,
                   COUNT(*) as requests
            FROM request_logs
            WHERE {where_clause}
            GROUP BY DATE(created_at)
            ORDER BY date
        """), params)
        daily_spend = [dict(r._mapping) for r in daily]

    return {
        "summary": dict(row._mapping),
        "by_model": models,
        "daily": daily_spend,
    }


async def get_cost_anomalies() -> list[dict]:
    async with async_session() as session:
        result = await session.execute(text("""
            WITH daily_stats AS (
                SELECT DATE(created_at) as date,
                       COALESCE(SUM(cost), 0) as daily_cost
                FROM request_logs
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
            ),
            stats AS (
                SELECT AVG(daily_cost) as mean,
                       STDDEV(daily_cost) as stddev
                FROM daily_stats
            )
            SELECT ds.date, ds.daily_cost,
                   (ds.daily_cost - s.mean) / NULLIF(s.stddev, 0) as z_score
            FROM daily_stats ds, stats s
            WHERE ABS((ds.daily_cost - s.mean) / NULLIF(s.stddev, 0)) > 2.0
            ORDER BY ds.date DESC
        """))
        return [dict(r._mapping) for r in result]


async def get_cost_forecast() -> dict:
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT
                COALESCE(SUM(cost), 0) as total_cost,
                MIN(DATE(created_at)) as first_date,
                MAX(DATE(created_at)) as last_date
            FROM request_logs
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """))
        row = result.fetchone()
        total = float(row._mapping["total_cost"])
        days = max((row._mapping["last_date"] - row._mapping["first_date"]).days, 1)
        daily_burn = total / days
        return {
            "daily_burn_rate": round(daily_burn, 4),
            "weekly_trend": round(total, 2),
            "estimated_monthly": round(daily_burn * 30, 2),
        }


async def get_cache_savings() -> dict:
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT
                COUNT(*) as cache_entries,
                COALESCE(SUM(hit_count), 0) as total_hits,
                AVG(similarity_threshold) as avg_threshold
            FROM semantic_cache
        """))
        row = result.fetchone()
        entries = int(row._mapping["cache_entries"])
        hits = int(row._mapping["total_hits"])
        estimated_savings = hits * 0.001
        return {
            "cache_entries": entries,
            "total_hits": hits,
            "avg_threshold": round(float(row._mapping["avg_threshold"] or 0), 3),
            "estimated_savings_usd": round(estimated_savings, 2),
        }
