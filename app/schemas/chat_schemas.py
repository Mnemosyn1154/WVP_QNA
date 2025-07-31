"""
Chat-related Pydantic schemas
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Source(BaseModel):
    """Source information model"""
    type: Literal["file", "news"] = Field(..., description="Type of source")
    name: Optional[str] = Field(None, description="File name for file sources")
    title: Optional[str] = Field(None, description="News title for news sources")
    url: str = Field(..., description="URL for the source")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "type": "file",
                    "name": "2024_annual_report.pdf",
                    "url": "/api/documents/download/123"
                },
                {
                    "type": "news", 
                    "title": "기업 인수 발표",
                    "url": "https://news.example.com/article/123"
                }
            ]
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source documents used")
    charts: Optional[List[Dict[str, Any]]] = Field(None, description="Chart data if applicable")
    processing_time: Optional[float] = Field(None, description="Time taken to process (seconds)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (model, usage, cost)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "A기업의 2024년 매출은 1,234억원입니다.",
                "sources": [
                    {
                        "type": "file",
                        "name": "A기업_2024_사업보고서.pdf",
                        "url": "/api/documents/download/123"
                    }
                ],
                "charts": None,
                "processing_time": 2.5,
                "metadata": {
                    "model_used": "claude-3-sonnet",
                    "token_usage": {"input_tokens": 1000, "output_tokens": 500},
                    "estimated_cost": 0.025
                }
            }
        }


class ChatHistoryItem(BaseModel):
    """Chat history item model"""
    id: int
    user_id: Optional[int]
    question: str
    answer: Optional[str]
    context: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True