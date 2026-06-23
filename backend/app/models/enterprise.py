from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.models.usage import Base
from datetime import datetime

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    teams = relationship("Team", back_populates="tenant")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    # Budgeting
    budget_limit = Column(Float, default=100.0)  # in USD
    current_spend = Column(Float, default=0.0)
    hard_limit = Column(Boolean, default=True)   # If True, block requests when budget exceeded
    
    tenant = relationship("Tenant", back_populates="teams")
    users = relationship("User", back_populates="team")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    is_active = Column(Boolean, default=True)
    
    # User-level overrides
    individual_budget_limit = Column(Float, nullable=True) 
    individual_current_spend = Column(Float, default=0.0)
    
    team = relationship("Team", back_populates="users")
