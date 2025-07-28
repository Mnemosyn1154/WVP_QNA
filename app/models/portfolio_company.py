"""
Portfolio Company model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.db.session import Base


class PortfolioCompany(Base):
    """Portfolio company model"""
    
    __tablename__ = "portfolio_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    industry = Column(String(100))
    description = Column(Text)
    website = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())