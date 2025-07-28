"""
Populate test data for development
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.models.financial_doc import FinancialDoc
from loguru import logger

def populate_test_documents():
    """Populate test documents in database"""
    db = SessionLocal()
    
    try:
        # Check if documents already exist
        existing_count = db.query(FinancialDoc).count()
        if existing_count > 0:
            logger.info(f"Database already has {existing_count} documents")
            return
        
        # Test documents
        test_docs = [
            {
                "company_name": "마인이스",
                "doc_type": "사업보고서",
                "year": 2024,
                "file_path": "data/financial_docs/마인이스_2024_사업보고서.pdf",
                "file_size": 1024000
            },
            {
                "company_name": "우나스텔라",
                "doc_type": "사업보고서", 
                "year": 2024,
                "file_path": "data/financial_docs/우나스텔라_2024_사업보고서.pdf",
                "file_size": 2048000
            },
            {
                "company_name": "설로인",
                "doc_type": "사업보고서",
                "year": 2024,
                "file_path": "data/financial_docs/설로인_2024_사업보고서.pdf",
                "file_size": 1536000
            }
        ]
        
        # Insert test documents
        for doc_data in test_docs:
            doc = FinancialDoc(**doc_data)
            db.add(doc)
        
        db.commit()
        logger.info(f"Successfully added {len(test_docs)} test documents")
        
    except Exception as e:
        logger.error(f"Error populating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_test_documents()