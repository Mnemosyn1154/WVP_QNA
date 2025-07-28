#!/usr/bin/env python3
"""
Simple document indexing script for financial documents
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.financial_doc import FinancialDoc


def parse_filename(filename):
    """Parse company name, year, and doc type from filename"""
    # Example: 마인이스_2024_재무제표.pdf
    parts = filename.replace('.pdf', '').split('_')
    if len(parts) >= 3:
        return {
            'company_name': parts[0],
            'year': int(parts[1]) if parts[1].isdigit() else None,
            'doc_type': parts[2]
        }
    return None


def index_documents():
    """Index all PDF documents in the financial_docs directory"""
    financial_docs_path = Path("data/financial_docs")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    indexed_count = 0
    error_count = 0
    
    try:
        # Clear existing entries to avoid duplicates
        db.query(FinancialDoc).delete()
        db.commit()
        
        # Walk through all PDF files
        for company_dir in financial_docs_path.iterdir():
            if not company_dir.is_dir():
                continue
                
            company_name = company_dir.name
            
            for year_dir in company_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                    
                for pdf_file in year_dir.glob("*.pdf"):
                    try:
                        # Parse filename
                        file_info = parse_filename(pdf_file.name)
                        if not file_info:
                            print(f"⚠️  Could not parse: {pdf_file.name}")
                            error_count += 1
                            continue
                        
                        # Create document record
                        doc = FinancialDoc(
                            company_name=file_info['company_name'],
                            doc_type=file_info['doc_type'],
                            year=file_info['year'],
                            file_path=str(pdf_file),
                            file_size=pdf_file.stat().st_size
                        )
                        
                        db.add(doc)
                        indexed_count += 1
                        print(f"✅ Indexed: {company_name} - {file_info['year']} - {file_info['doc_type']}")
                        
                    except Exception as e:
                        print(f"❌ Error indexing {pdf_file}: {e}")
                        error_count += 1
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()
    
    print(f"\n📊 Indexing Summary:")
    print(f"   Total indexed: {indexed_count}")
    print(f"   Errors: {error_count}")
    
    return indexed_count, error_count


def verify_indexed():
    """Verify indexed documents"""
    db = SessionLocal()
    
    try:
        # Get all documents
        docs = db.query(FinancialDoc).all()
        
        print("\n📚 Indexed Documents:")
        print("-" * 60)
        
        # Group by company
        companies = {}
        for doc in docs:
            if doc.company_name not in companies:
                companies[doc.company_name] = []
            companies[doc.company_name].append(doc)
        
        # Print by company
        for company, company_docs in companies.items():
            print(f"\n🏢 {company}:")
            for doc in sorted(company_docs, key=lambda x: (x.year, x.doc_type)):
                print(f"   - {doc.year} {doc.doc_type} ({doc.file_size:,} bytes)")
        
        print(f"\n📈 Total documents: {len(docs)}")
        
    except Exception as e:
        print(f"❌ Error verifying: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify_indexed()
    else:
        index_documents()
        verify_indexed()