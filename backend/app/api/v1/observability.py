import json
from fastapi import APIRouter, HTTPException, Header, Query, Depends
from app.db.session import async_session
from app.models.feedback import Feedback
from app.models.usage import RequestLog
from app.core.observability.cost_engine import get_cost_summary, get_cost_anomalies, get_cost_forecast, get_cache_savings
from app.core.drift import check_latency_drift, check_error_drift
from app.api.v1.admin import verify_admin
from datetime import datetime

router = APIRouter()


@router.get("/costs/summary")
async def cost_summary(
    team: str | None = Query(None),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    admin: str = Depends(verify_admin),
):
    return await get_cost_summary(team=team, from_date=from_date, to_date=to_date)


@router.get("/costs/anomalies")
async def cost_anomalies(admin: str = Depends(verify_admin)):
    return {"anomalies": await get_cost_anomalies()}


@router.get("/costs/forecast")
async def cost_forecast(admin: str = Depends(verify_admin)):
    return await get_cost_forecast()


@router.get("/cache/savings")
async def cache_savings(admin: str = Depends(verify_admin)):
    return await get_cache_savings()


@router.get("/drift")
async def drift_detection(admin: str = Depends(verify_admin)):
    latency = await check_latency_drift()
    errors = await check_error_drift()
    return {"alerts": latency + errors}


@router.get("/logs/recent")
async def recent_logs(
    limit: int = Query(10, ge=1, le=100),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(RequestLog).order_by(RequestLog.created_at.desc()).limit(limit)
        )
        logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "model": log.model,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "total_tokens": log.total_tokens,
            "cost": log.cost,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.post("/feedback")
async def submit_feedback(
    message_id: str = Query(...),
    score: int = Query(..., ge=-1, le=1),
    comment: str | None = Query(None),
):
    async with async_session() as session:
        fb = Feedback(
            message_id=message_id,
            score=score,
            comment=comment,
        )
        session.add(fb)
        await session.commit()
    return {"status": "ok", "message_id": message_id}
