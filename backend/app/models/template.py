from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from app.models.usage import Base
from datetime import datetime


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text)
    version = Column(Integer, default=1)
    variables_schema = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    created_by = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TemplateVersion(Base):
    __tablename__ = "template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, index=True)
    version = Column(Integer)
    content = Column(Text)
    variables_schema = Column(JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TemplateDeployment(Base):
    __tablename__ = "template_deployments"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, index=True)
    version = Column(Integer)
    alias = Column(String, default="production")
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    template_id = Column(Integer, index=True)
    variants = Column(JSON)
    status = Column(String, default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
