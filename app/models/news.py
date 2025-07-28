"""
News model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index

from app.models.base import Base


class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text)
    content_url = Column(Text)
    source = Column(String(100))
    published_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_news_company_date', 'company_name', 'published_date'),
    )