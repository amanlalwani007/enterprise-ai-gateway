from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.models.usage import Base
from datetime import datetime

# Note: We will use a raw SQL command to add the vector column 
# because pgvector support in SQLAlchemy requires specific extensions
# or using the 'Vector' type from pgvector's python package.

class SemanticCache(Base):
    __tablename__ = "semantic_cache"

    id = Column(Integer, primary_key=True, index=True)
    prompt_text = Column(Text, index=True)
    response_text = Column(Text)
    model = Column(String)
    # We will handle the 'embedding' column via raw SQL or specialized types
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB, nullable=True)
