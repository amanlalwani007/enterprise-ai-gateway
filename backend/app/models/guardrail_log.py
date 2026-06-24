from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from app.models.usage import Base
from datetime import datetime


class GuardrailLog(Base):
    __tablename__ = "guardrail_logs"

    id = Column(Integer, primary_key=True, index=True)
    guardrail_name = Column(String, index=True)
    side = Column(String, nullable=True)
    action_taken = Column(String)
    reason = Column(Text, nullable=True)
    matched_pattern = Column(String, nullable=True)
    score = Column(String, nullable=True)
    request_id = Column(String, index=True, nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
