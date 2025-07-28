"""
Document Service
Handles document retrieval and management
"""

import os
from loguru import logger
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.financial_doc import FinancialDoc
from app.services.pdf_processor import PDFProcessor


class DocumentService:
    """Service for managing and retrieving documents"""
    
    def __init__(self, db: Session):
        self.db = db
        self.pdf_processor = PDFProcessor()
        self.base_path = Path("data/financial_docs")
    
    def extract_company_from_question(self, question: str) -> Optional[str]:
        """Extract company name from user question"""
        # List of known companies
        companies = ["마인이스", "우나스텔라", "설로인"]
        
        question_lower = question.lower()
        for company in companies:
            if company.lower() in question_lower:
                return company
        
        # Try variations
        variations = {
            "마인": "마인이스",
            "우나": "우나스텔라",
            "스텔라": "우나스텔라"
        }
        
        for variant, company in variations.items():
            if variant in question_lower:
                return company
        
        return None
    
    def extract_year_from_question(self, question: str) -> Optional[int]:
        """Extract year from user question"""
        import re
        
        # Pattern for 4-digit year
        year_match = re.search(r'20\d{2}', question)
        if year_match:
            return int(year_match.group())
        
        # Pattern for 2-digit year with 년
        year_match = re.search(r'(\d{2})년', question)
        if year_match:
            year = int(year_match.group(1))
            return 2000 + year if year < 50 else 1900 + year
        
        # Keywords for recent/last year
        if "최근" in question or "최신" in question:
            return 2024
        elif "작년" in question or "지난해" in question:
            return 2023
        
        return None
    
    def find_relevant_documents(
        self, 
        company: str, 
        year: Optional[int] = None,
        doc_type: Optional[str] = None
    ) -> List[FinancialDoc]:
        """Find relevant documents based on criteria"""
        query = self.db.query(FinancialDoc).filter(
            FinancialDoc.company_name == company
        )
        
        if year:
            query = query.filter(FinancialDoc.year == year)
        
        if doc_type:
            query = query.filter(FinancialDoc.doc_type == doc_type)
        
        # Order by year descending to get most recent first
        documents = query.order_by(FinancialDoc.year.desc()).all()
        
        # If no documents found with specific year, get most recent
        if not documents and year:
            documents = self.db.query(FinancialDoc).filter(
                FinancialDoc.company_name == company
            ).order_by(FinancialDoc.year.desc()).limit(1).all()
        
        return documents
    
    def read_pdf_content(self, file_path: str) -> bytes:
        """Read PDF file content"""
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = Path.cwd() / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"PDF file not found: {full_path}")
        
        with open(full_path, 'rb') as f:
            return f.read()
    
    def get_document_for_question(self, question: str) -> Tuple[Optional[FinancialDoc], Optional[bytes]]:
        """
        Get the most relevant document for a user question
        
        Returns:
            Tuple of (document metadata, PDF content)
        """
        # Extract company and year from question
        company = self.extract_company_from_question(question)
        if not company:
            logger.warning(f"No company found in question: {question}")
            return None, None
        
        year = self.extract_year_from_question(question)
        
        # Find relevant documents
        documents = self.find_relevant_documents(company, year)
        
        if not documents:
            logger.warning(f"No documents found for company: {company}, year: {year}")
            return None, None
        
        # Use the first (most recent) document
        document = documents[0]
        
        try:
            # Read PDF content
            pdf_content = self.read_pdf_content(document.file_path)
            
            # Check if optimization is needed
            if len(pdf_content) > 10 * 1024 * 1024:  # 10MB
                logger.info(f"Optimizing large PDF: {document.file_path}")
                pdf_content, metadata = self.pdf_processor.optimize_pdf(pdf_content)
                logger.info(f"PDF optimized: {metadata}")
            
            return document, pdf_content
            
        except Exception as e:
            logger.error(f"Error reading PDF {document.file_path}: {e}")
            return document, None
    
    def get_all_company_documents(self, company: str) -> List[Dict]:
        """Get all documents for a specific company"""
        documents = self.db.query(FinancialDoc).filter(
            FinancialDoc.company_name == company
        ).order_by(FinancialDoc.year.desc()).all()
        
        return [
            {
                "id": doc.id,
                "year": doc.year,
                "doc_type": doc.doc_type,
                "file_path": doc.file_path,
                "file_size": doc.file_size,
                "created_at": doc.created_at
            }
            for doc in documents
        ]
    
    def search_documents(
        self,
        company_name: str,
        year: Optional[int] = None,
        doc_type: Optional[str] = None,
        limit: int = 10,
        db: Session = None
    ) -> List[Dict]:
        """Search for documents based on criteria"""
        if db:
            self.db = db
            
        query = self.db.query(FinancialDoc)
        
        # Apply filters
        query = query.filter(FinancialDoc.company_name == company_name)
        
        if year:
            query = query.filter(FinancialDoc.year == year)
        
        if doc_type:
            query = query.filter(FinancialDoc.doc_type == doc_type)
        
        # Order by year descending and limit
        documents = query.order_by(FinancialDoc.year.desc()).limit(limit).all()
        
        return [
            {
                "id": doc.id,
                "company_name": doc.company_name,
                "year": doc.year,
                "doc_type": doc.doc_type,
                "quarter": doc.quarter,
                "file_path": doc.file_path,
                "file_size": doc.file_size,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at
            }
            for doc in documents
        ]
    
    def get_document_by_id(self, document_id: int, db: Session = None) -> Optional[Dict]:
        """Get a document by ID"""
        if db:
            self.db = db
            
        doc = self.db.query(FinancialDoc).filter(FinancialDoc.id == document_id).first()
        
        if not doc:
            return None
        
        return {
            "id": doc.id,
            "company_name": doc.company_name,
            "year": doc.year,
            "doc_type": doc.doc_type,
            "quarter": doc.quarter,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at
        }