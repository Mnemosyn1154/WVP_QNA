#!/usr/bin/env python3
"""
Initialize the SQLite database with tables and sample data
"""

import sys
import os
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.db.session import Base, engine
from app.models.financial_doc import FinancialDoc
from app.models.chat_history import ChatHistory
from app.models.portfolio_company import PortfolioCompany
from app.models.news_article import NewsArticle
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with tables"""
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        logger.info(f"Creating database at: {settings.DATABASE_URL}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully!")
        
        # Add sample portfolio companies
        from sqlalchemy.orm import Session
        
        with Session(engine) as session:
            # Check if companies already exist
            existing = session.query(PortfolioCompany).first()
            if not existing:
                companies = [
                    PortfolioCompany(
                        name="마인이스",
                        industry="제조업",
                        description="첨단 소재 제조 기업",
                        website="https://mines.co.kr"
                    ),
                    PortfolioCompany(
                        name="우나스텔라",
                        industry="IT/소프트웨어",
                        description="AI 및 빅데이터 솔루션 기업",
                        website="https://unastella.com"
                    ),
                    PortfolioCompany(
                        name="설로인",
                        industry="바이오/헬스케어",
                        description="바이오 신약 개발 기업",
                        website="https://sulloin.com"
                    )
                ]
                
                session.add_all(companies)
                session.commit()
                logger.info(f"Added {len(companies)} portfolio companies")
            
            # Scan and add financial documents
            docs_path = Path("data/financial_docs")
            if docs_path.exists():
                added_docs = 0
                for company_dir in docs_path.iterdir():
                    if company_dir.is_dir():
                        company_name = company_dir.name
                        
                        for pdf_file in company_dir.glob("*.pdf"):
                            # Check if document already exists
                            existing_doc = session.query(FinancialDoc).filter_by(
                                file_path=str(pdf_file)
                            ).first()
                            
                            if not existing_doc:
                                # Parse filename to extract year and doc type
                                filename = pdf_file.stem
                                parts = filename.split("_")
                                
                                if len(parts) >= 3:
                                    year = int(parts[1])
                                    doc_type = parts[2]
                                else:
                                    # Fallback parsing
                                    year = 2024
                                    doc_type = "재무제표"
                                
                                doc = FinancialDoc(
                                    company_name=company_name,
                                    year=year,
                                    doc_type=doc_type,
                                    file_path=str(pdf_file),
                                    file_size=pdf_file.stat().st_size
                                )
                                session.add(doc)
                                added_docs += 1
                
                session.commit()
                if added_docs > 0:
                    logger.info(f"Added {added_docs} financial documents")
        
        logger.info("Database initialization completed!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    init_database()