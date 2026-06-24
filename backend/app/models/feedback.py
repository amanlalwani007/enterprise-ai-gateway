from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON
from app.models.usage import Base
from datetime import datetime


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, index=True, nullable=True)
    user_id = Column(String, index=True, nullable=True)
    score = Column(Integer)
    comment = Column(Text, nullable=True)
    model = Column(String, nullable=True)
    latency_ms = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
