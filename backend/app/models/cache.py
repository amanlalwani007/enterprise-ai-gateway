from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from app.models.usage import Base
from datetime import datetime

class SemanticCache(Base):
    __tablename__ = "semantic_cache"

    id = Column(Integer, primary_key=True, index=True)
    prompt_text = Column(Text, index=True)
    response_text = Column(Text)
    model = Column(String, index=True)
    query_type = Column(String(32), default="factual", index=True)
    keywords = Column(ARRAY(String), nullable=True)
    similarity_threshold = Column(Float, default=0.95)
    ttl_seconds = Column(Integer, default=604800)
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSONB, nullable=True)
