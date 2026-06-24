from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from app.models.usage import Base
from datetime import datetime


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    status = Column(String, default="active")
    total_cost = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    model_chain = Column(JSON, nullable=True)
    turn_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=True)
    user_id = Column(String, index=True)
    tool_name = Column(String, index=True)
    arguments = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    latency_ms = Column(Float, nullable=True)
    status = Column(String, default="success")
    created_at = Column(DateTime, default=datetime.utcnow)


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    step_description = Column(Text)
    cost_threshold = Column(Float)
    actual_cost = Column(Float)
    status = Column(String, default="pending")
    approved_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
