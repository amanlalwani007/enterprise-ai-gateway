from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select
from app.db.session import async_session
from app.models.canary import CanaryConfig, EvalResult, RollbackEvent
from app.api.v1.admin import verify_admin
from datetime import datetime

router = APIRouter()


@router.post("/canary/configs")
async def create_canary_config(
    model_alias: str = Query(...),
    default_version: str = Query(...),
    canary_version: str = Query(...),
    canary_percent: int = Query(0, ge=0, le=100),
    quality_gates: str | None = Query(None),
    admin: str = Depends(verify_admin),
):
    import json
    async with async_session() as session:
        existing = await session.execute(select(CanaryConfig).where(CanaryConfig.model_alias == model_alias))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Canary config already exists")
        cfg = CanaryConfig(
            model_alias=model_alias,
            default_version=default_version,
            canary_version=canary_version,
            canary_percent=canary_percent,
            quality_gates=json.loads(quality_gates) if quality_gates else None,
        )
        session.add(cfg)
        await session.commit()
        await session.refresh(cfg)
    return {
        "id": cfg.id,
        "model_alias": model_alias,
        "canary_percent": canary_percent,
        "status": cfg.status,
    }


@router.get("/canary/configs")
async def list_canary_configs(admin: str = Depends(verify_admin)):
    async with async_session() as session:
        result = await session.execute(select(CanaryConfig).order_by(CanaryConfig.model_alias))
        configs = result.scalars().all()
    return [
        {
            "id": c.id,
            "model_alias": c.model_alias,
            "default_version": c.default_version,
            "canary_version": c.canary_version,
            "canary_percent": c.canary_percent,
            "status": c.status,
        }
        for c in configs
    ]


@router.post("/canary/configs/{config_id}/promote")
async def promote_canary(config_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        cfg = await session.execute(select(CanaryConfig).where(CanaryConfig.id == config_id))
        cfg = cfg.scalar_one_or_none()
        if not cfg:
            raise HTTPException(status_code=404, detail="Canary config not found")
        cfg.default_version = cfg.canary_version
        cfg.canary_percent = 0
        cfg.status = "inactive"
        await session.commit()
    return {"message": "Canary promoted to default", "model_alias": cfg.model_alias}


@router.get("/canary/eval-results")
async def eval_results(
    model_alias: str | None = Query(None),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        query = select(EvalResult).order_by(EvalResult.created_at.desc()).limit(50)
        if model_alias:
            query = query.where(EvalResult.model_alias == model_alias)
        result = await session.execute(query)
        evals = result.scalars().all()
    return [
        {
            "id": e.id,
            "model_alias": e.model_alias,
            "version": e.version,
            "eval_name": e.eval_name,
            "score": e.score,
            "passed": e.passed,
            "latency_p95": e.latency_p95,
            "error_rate": e.error_rate,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in evals
    ]


@router.get("/canary/rollbacks")
async def rollback_history(
    model_alias: str | None = Query(None),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        query = select(RollbackEvent).order_by(RollbackEvent.created_at.desc()).limit(50)
        if model_alias:
            query = query.where(RollbackEvent.model_alias == model_alias)
        result = await session.execute(query)
        events = result.scalars().all()
    return [
        {
            "id": r.id,
            "model_alias": r.model_alias,
            "from_version": r.from_version,
            "to_version": r.to_version,
            "reason": r.reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in events
    ]
