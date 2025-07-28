"""
Document-related Pydantic schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document model"""
    company_name: str = Field(..., max_length=100)
    doc_type: Optional[str] = Field(None, max_length=50, description="사업보고서, 반기보고서, 분기보고서")
    year: int = Field(..., ge=2000, le=2030)
    quarter: Optional[int] = Field(None, ge=1, le=4)


class DocumentCreate(DocumentBase):
    """Document creation model"""
    file_path: str = Field(..., description="Path to the document file")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")


class DocumentResponse(DocumentBase):
    """Document response model"""
    id: int
    file_path: str
    file_size: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "company_name": "삼성전자",
                "doc_type": "사업보고서",
                "year": 2024,
                "quarter": None,
                "file_path": "/data/financial_docs/삼성전자/2024/annual_report_2024.pdf",
                "file_size": 5242880,
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T10:30:00"
            }
        }


class DocumentSearchQuery(BaseModel):
    """Document search query model"""
    company_name: str
    year: Optional[int] = None
    doc_type: Optional[str] = None
    limit: int = Field(10, ge=1, le=100)