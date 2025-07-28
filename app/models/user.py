"""
User model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100))
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)