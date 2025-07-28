"""
Chat history model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Index, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Optional user ID
    question = Column(Text, nullable=False)
    answer = Column(Text)
    context = Column(JSON)  # Store search document info
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_chat_history_created', 'created_at'),
    )