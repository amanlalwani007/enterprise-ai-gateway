from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.session import async_session


async def check_latency_drift() -> list[dict]:
    async with async_session() as session:
        result = await session.execute(text("""
            WITH weekly AS (
                SELECT
                    DATE_TRUNC('week', created_at) as week,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY
                        CASE WHEN metadata->>'latency_ms' IS NOT NULL
                             THEN (metadata->>'latency_ms')::float
                             ELSE NULL END
                    ) as p95_latency
                FROM request_logs
                WHERE created_at >= NOW() - INTERVAL '14 days'
                  AND metadata IS NOT NULL
                GROUP BY DATE_TRUNC('week', created_at)
                ORDER BY week DESC
                LIMIT 2
            )
            SELECT * FROM weekly
        """))
        weeks = [dict(r._mapping) for r in result]
        if len(weeks) == 2:
            current = weeks[0]["p95_latency"] or 0
            previous = weeks[1]["p95_latency"] or 1
            change_pct = ((current - previous) / previous) * 100
            if change_pct > 20:
                return [{
                    "type": "latency_drift",
                    "current_p95": round(current, 2),
                    "previous_p95": round(previous, 2),
                    "change_pct": round(change_pct, 1),
                    "severity": "warning" if change_pct < 50 else "critical",
                }]
    return []


async def check_error_drift() -> list[dict]:
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN response_data->>'error' IS NOT NULL THEN 1 ELSE 0 END) as errors
            FROM request_logs
            WHERE created_at >= NOW() - INTERVAL '48 hours'
            GROUP BY DATE(created_at)
            ORDER BY date
        """))
        rows = [dict(r._mapping) for r in result]
        alerts = []
        for row in rows:
            total = row["total"] or 1
            errors = row["errors"] or 0
            error_rate = (errors / total) * 100
            if error_rate > 5:
                alerts.append({
                    "type": "error_drift",
                    "date": str(row["date"]),
                    "error_rate_pct": round(error_rate, 1),
                    "total_requests": total,
                    "severity": "critical" if error_rate > 10 else "warning",
                })
        return alerts
