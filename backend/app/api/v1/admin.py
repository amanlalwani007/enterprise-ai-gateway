import csv
import hashlib
import io
import secrets
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from app.db.session import async_session
from app.models.enterprise import User
from app.models.usage import RequestLog
from app.core.config import settings

router = APIRouter()

def verify_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    key = authorization.split(" ")[1]
    if key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: admin access required")
    return key

def generate_api_key() -> tuple[str, str]:
    raw = f"eag_{secrets.token_hex(24)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed

@router.post("/keys")
async def create_api_key(
    email: str,
    team_id: int | None = None,
    budget_limit: float | None = None,
    admin: str = Depends(verify_admin)
):
    raw_key, hashed_key = generate_api_key()
    async with async_session() as session:
        existing = await session.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="User with this email already exists")
        user = User(
            email=email,
            api_key=hashed_key,
            team_id=team_id,
            individual_budget_limit=budget_limit,
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "api_key": raw_key,
        "team_id": user.team_id,
        "budget_limit": user.individual_budget_limit,
        "is_active": user.is_active,
        "warning": "Store this key securely. It will not be shown again."
    }

@router.get("/keys")
async def list_api_keys(admin: str = Depends(verify_admin)):
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "team_id": u.team_id,
            "is_active": u.is_active,
            "budget_limit": u.individual_budget_limit,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]

@router.delete("/keys/{user_id}")
async def revoke_api_key(user_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = False
        await session.commit()
    return {"message": f"API key for user {user_id} revoked"}

@router.post("/keys/{user_id}/rotate")
async def rotate_api_key(user_id: int, admin: str = Depends(verify_admin)):
    raw_key, hashed_key = generate_api_key()
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.api_key = hashed_key
        user.is_active = True
        await session.commit()
    return {
        "id": user_id,
        "api_key": raw_key,
        "warning": "Store this key securely. It will not be shown again."
    }

@router.get("/logs/export")
async def export_logs(
    format: str = Query("json", regex="^(csv|json)$"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    admin: str = Depends(verify_admin)
):
    query = select(RequestLog).order_by(RequestLog.created_at.desc())
    if from_date:
        query = query.where(RequestLog.created_at >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.where(RequestLog.created_at <= datetime.fromisoformat(to_date))

    async with async_session() as session:
        result = await session.execute(query)
        logs = result.scalars().all()

    if format == "json":
        data = [
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
        import json
        return StreamingResponse(
            iter([json.dumps(data, indent=2)]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=audit_logs.json"}
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "model", "prompt_tokens", "completion_tokens", "total_tokens", "cost", "created_at"])
    for log in logs:
        writer.writerow([log.id, log.user_id, log.model, log.prompt_tokens, log.completion_tokens, log.total_tokens, log.cost, log.created_at.isoformat() if log.created_at else ""])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
    )
