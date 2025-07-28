#!/usr/bin/env python3
"""
Script to add 설로인 financial documents to database
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.models.financial_doc import FinancialDoc
from loguru import logger

def add_selloin_documents():
    """Add 설로인 financial documents to database"""
    db = SessionLocal()
    
    try:
        # Check if 설로인 2024 document already exists
        existing = db.query(FinancialDoc).filter_by(
            company_name="설로인",
            year=2024
        ).first()
        
        if existing:
            logger.info("설로인 2024 document already exists in database")
            return
        
        # Add 설로인 2024 재무제표
        pdf_path = "data/financial_docs/설로인/2024/설로인_2024_재무제표.pdf"
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            
            doc = FinancialDoc(
                company_name="설로인",
                doc_type="재무제표",
                year=2024,
                file_path=pdf_path,
                file_size=file_size
            )
            
            db.add(doc)
            db.commit()
            logger.info(f"Added 설로인 2024 재무제표 (size: {file_size/1024:.2f}KB)")
        else:
            logger.error(f"File not found: {pdf_path}")
        
        # Also add 2023 document if it doesn't exist
        existing_2023 = db.query(FinancialDoc).filter_by(
            company_name="설로인",
            year=2023
        ).first()
        
        if not existing_2023:
            pdf_path_2023 = "data/financial_docs/설로인/2023/설로인_2023_재무제표.pdf"
            if os.path.exists(pdf_path_2023):
                file_size_2023 = os.path.getsize(pdf_path_2023)
                
                doc_2023 = FinancialDoc(
                    company_name="설로인",
                    doc_type="재무제표",
                    year=2023,
                    file_path=pdf_path_2023,
                    file_size=file_size_2023
                )
                
                db.add(doc_2023)
                db.commit()
                logger.info(f"Added 설로인 2023 재무제표 (size: {file_size_2023/1024:.2f}KB)")
        
        # Show all documents in database
        all_docs = db.query(FinancialDoc).all()
        logger.info(f"\nTotal documents in database: {len(all_docs)}")
        for doc in all_docs:
            logger.info(f"- {doc.company_name} {doc.year} {doc.doc_type}")
            
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_selloin_documents()