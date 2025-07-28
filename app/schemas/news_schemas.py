"""
News-related Pydantic schemas
"""

from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, HttpUrl


class NewsBase(BaseModel):
    """Base news model"""
    company_name: str = Field(..., max_length=100)
    title: str = Field(..., min_length=1)
    content: Optional[str] = None
    content_url: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)
    published_date: Optional[datetime] = None


class NewsCreate(NewsBase):
    """News creation model"""
    pass


class NewsResponse(NewsBase):
    """News response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "company_name": "LG전자",
                "title": "LG전자, 2024년 4분기 실적 발표",
                "content": "LG전자가 2024년 4분기 매출 20조원을 기록했다...",
                "content_url": "https://news.example.com/lg-q4-2024",
                "source": "경제신문",
                "published_date": "2025-01-20T09:00:00",
                "created_at": "2025-01-20T10:00:00",
                "updated_at": "2025-01-20T10:00:00"
            }
        }


class NewsSearchQuery(BaseModel):
    """News search query model"""
    company_name: str
    keyword: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    limit: int = Field(20, ge=1, le=100)