"""
API Dependencies for dependency injection
"""

from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.session import get_db
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.claude_service import ClaudeService
from app.services.pdf_processor import PDFProcessor


# Services
def get_chat_service(
    db: Session = Depends(get_db)
) -> ChatService:
    """Get chat service instance"""
    return ChatService(db=db)


def get_document_service(
    db: Session = Depends(get_db)
) -> DocumentService:
    """Get document service instance"""
    return DocumentService(db=db)


def get_claude_service() -> ClaudeService:
    """Get Claude service instance"""
    return ClaudeService()


def get_pdf_processor() -> PDFProcessor:
    """Get PDF processor instance"""
    return PDFProcessor()