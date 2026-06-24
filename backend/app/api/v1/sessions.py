from fastapi import APIRouter, HTTPException, Header, Depends, Query
from sqlalchemy import select
from app.db.session import async_session
from app.models.session import Session, ToolCall, Approval
from app.api.v1.admin import verify_admin
from datetime import datetime

router = APIRouter()


@router.get("/sessions")
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        result = await session.execute(
            select(Session).order_by(Session.started_at.desc()).limit(limit)
        )
        sessions = result.scalars().all()
    return [
        {
            "session_id": s.session_id,
            "user_id": s.user_id,
            "status": s.status,
            "total_cost": s.total_cost,
            "total_tokens": s.total_tokens,
            "turn_count": s.turn_count,
            "model_chain": s.model_chain,
            "started_at": s.started_at.isoformat() if s.started_at else None,
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        result = await session.execute(
            select(Session).where(Session.session_id == session_id)
        )
        s = result.scalar_one_or_none()
        if not s:
            raise HTTPException(status_code=404, detail="Session not found")

        tools = await session.execute(
            select(ToolCall).where(ToolCall.session_id == session_id).order_by(ToolCall.created_at)
        )
        tool_calls = tools.scalars().all()

    return {
        "session_id": s.session_id,
        "user_id": s.user_id,
        "status": s.status,
        "total_cost": s.total_cost,
        "total_tokens": s.total_tokens,
        "turn_count": s.turn_count,
        "model_chain": s.model_chain,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "tool_calls": [
            {
                "tool_name": t.tool_name,
                "arguments": t.arguments,
                "result": t.result,
                "latency_ms": t.latency_ms,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tool_calls
        ],
    }


@router.get("/tools/logs")
async def tool_logs(
    limit: int = Query(20, ge=1, le=100),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        result = await session.execute(
            select(ToolCall).order_by(ToolCall.created_at.desc()).limit(limit)
        )
        calls = result.scalars().all()
    return [
        {
            "id": t.id,
            "session_id": t.session_id,
            "user_id": t.user_id,
            "tool_name": t.tool_name,
            "arguments": t.arguments,
            "result": t.result,
            "latency_ms": t.latency_ms,
            "status": t.status,
        }
        for t in calls
    ]


@router.get("/approvals")
async def list_approvals(
    status: str | None = Query(None),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        query = select(Approval).order_by(Approval.created_at.desc())
        if status:
            query = query.where(Approval.status == status)
        result = await session.execute(query)
        approvals = result.scalars().all()
    return [
        {
            "id": a.id,
            "session_id": a.session_id,
            "step_description": a.step_description,
            "cost_threshold": a.cost_threshold,
            "actual_cost": a.actual_cost,
            "status": a.status,
        }
        for a in approvals
    ]


@router.post("/approvals/{approval_id}/approve")
async def approve_step(approval_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        a = await session.execute(select(Approval).where(Approval.id == approval_id))
        a = a.scalar_one_or_none()
        if not a:
            raise HTTPException(status_code=404, detail="Approval not found")
        a.status = "approved"
        a.approved_by = admin
        await session.commit()
    return {"message": "Approved", "id": approval_id}


@router.post("/approvals/{approval_id}/reject")
async def reject_step(approval_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        a = await session.execute(select(Approval).where(Approval.id == approval_id))
        a = a.scalar_one_or_none()
        if not a:
            raise HTTPException(status_code=404, detail="Approval not found")
        a.status = "rejected"
        a.approved_by = admin
        await session.commit()
    return {"message": "Rejected", "id": approval_id}
