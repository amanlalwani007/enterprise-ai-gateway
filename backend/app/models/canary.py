from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from app.models.usage import Base
from datetime import datetime


class CanaryConfig(Base):
    __tablename__ = "canary_configs"

    id = Column(Integer, primary_key=True, index=True)
    model_alias = Column(String, unique=True, index=True)
    default_version = Column(String)
    canary_version = Column(String)
    canary_percent = Column(Integer, default=0)
    status = Column(String, default="inactive")
    quality_gates = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(Integer, primary_key=True, index=True)
    model_alias = Column(String, index=True)
    version = Column(String, index=True)
    eval_name = Column(String)
    score = Column(Float)
    passed = Column(Boolean)
    latency_p95 = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    refusal_rate = Column(Float, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RollbackEvent(Base):
    __tablename__ = "rollback_events"

    id = Column(Integer, primary_key=True, index=True)
    model_alias = Column(String, index=True)
    from_version = Column(String)
    to_version = Column(String)
    reason = Column(Text)
    triggered_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
