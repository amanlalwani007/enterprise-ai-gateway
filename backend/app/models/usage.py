from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    model = Column(String)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost = Column(Integer)  # in micro-cents or similar
    request_data = Column(JSON)
    response_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
