#!/usr/bin/env python3
"""
Database initialization script
Creates tables and sample data for testing
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.financial_doc import FinancialDoc
from app.models.news import News
from app.models.chat_history import ChatHistory
from app.core.config import get_settings
from app.core.security import get_password_hash

settings = get_settings()

# Sample company names
SAMPLE_COMPANIES = [
    "마인이스", "우나스텔라", "설로인"
]

# Document types
DOC_TYPES = ["사업보고서", "반기보고서", "분기보고서"]


def create_database():
    """Create database if it doesn't exist"""
    # Create engine without database name
    engine_url = settings.DATABASE_URL.rsplit('/', 1)[0]
    engine = create_engine(engine_url)
    
    try:
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'portfolio_qa'")
            )
            if not result.fetchone():
                # Create database
                conn.execute(text("COMMIT"))
                conn.execute(text("CREATE DATABASE portfolio_qa"))
                print("✅ Database 'portfolio_qa' created")
            else:
                print("ℹ️  Database 'portfolio_qa' already exists")
    except Exception as e:
        print(f"⚠️  Could not create database: {e}")
        print("   Please ensure PostgreSQL is running")


def init_tables():
    """Initialize all tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")
    
    return engine


def create_sample_data(engine):
    """Create sample data for testing"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if data already exists
        if session.query(User).count() > 0:
            print("ℹ️  Sample data already exists. Skipping...")
            return
        
        # 1. Create sample users
        print("Creating sample users...")
        users = [
            User(
                email="admin@example.com",
                name="관리자",
                password_hash=get_password_hash("admin123"),
                is_active=True
            ),
            User(
                email="user@example.com",
                name="일반사용자",
                password_hash=get_password_hash("user123"),
                is_active=True
            )
        ]
        session.add_all(users)
        session.commit()
        print(f"✅ Created {len(users)} users")
        
        # 2. Create sample financial documents
        print("Creating sample financial documents...")
        docs = []
        for company in SAMPLE_COMPANIES:  # All companies
            for year in [2023, 2024]:
                for doc_type in DOC_TYPES:
                    if doc_type == "사업보고서":
                        # Annual report - no quarter
                        doc = FinancialDoc(
                            company_name=company,
                            doc_type=doc_type,
                            year=year,
                            file_path=f"data/financial_docs/{company}/{year}/{company}_{doc_type}_{year}.pdf",
                            file_size=random.randint(1000000, 10000000)  # 1-10MB
                        )
                        docs.append(doc)
                    else:
                        # Quarterly reports
                        for quarter in [1, 2]:
                            doc = FinancialDoc(
                                company_name=company,
                                doc_type=doc_type,
                                year=year,
                                quarter=quarter,
                                file_path=f"data/financial_docs/{company}/{year}/{company}_{doc_type}_{year}_Q{quarter}.pdf",
                                file_size=random.randint(500000, 5000000)  # 0.5-5MB
                            )
                            docs.append(doc)
        
        session.add_all(docs)
        session.commit()
        print(f"✅ Created {len(docs)} financial documents")
        
        # 3. Create sample news
        print("Creating sample news articles...")
        news_items = []
        news_titles = [
            "{company}, 역대 최대 실적 달성",
            "{company}, 신규 사업 진출 발표",
            "{company}, 해외 시장 공략 본격화",
            "{company}, ESG 경영 강화 선언",
            "{company}, 기술 혁신으로 시장 선도"
        ]
        
        for company in SAMPLE_COMPANIES:
            for i in range(10):  # 10 news per company
                days_ago = random.randint(1, 30)
                news = News(
                    company_name=company,
                    title=random.choice(news_titles).format(company=company),
                    content=f"{company}의 최근 소식입니다. 상세 내용은 다음과 같습니다...",
                    content_url=f"https://news.example.com/{company}/{i}",
                    source=random.choice(["한국경제", "매일경제", "조선일보", "연합뉴스"]),
                    published_date=datetime.now() - timedelta(days=days_ago)
                )
                news_items.append(news)
        
        session.add_all(news_items)
        session.commit()
        print(f"✅ Created {len(news_items)} news articles")
        
        # 4. Create sample chat history
        print("Creating sample chat history...")
        sample_questions = [
            "마인이스의 2024년 매출은 얼마인가요?",
            "우나스텔라의 최근 실적은 어떤가요?",
            "설로인의 주요 사업은 무엇인가요?",
            "마인이스의 성장 전략은?",
            "우나스텔라의 ESG 활동 내역을 알려주세요"
        ]
        
        chats = []
        for i, question in enumerate(sample_questions):
            chat = ChatHistory(
                user_id=users[0].id,  # Admin user
                question=question,
                answer=f"이것은 '{question}'에 대한 샘플 답변입니다.",
                context={
                    "sources": ["sample_doc_1.pdf", "sample_doc_2.pdf"],
                    "confidence": 0.85
                }
            )
            chats.append(chat)
        
        session.add_all(chats)
        session.commit()
        print(f"✅ Created {len(chats)} chat history entries")
        
        print("\n✅ All sample data created successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating sample data: {e}")
        raise
    finally:
        session.close()


def create_directory_structure():
    """Create directory structure for sample companies"""
    print("\nCreating directory structure...")
    
    for company in SAMPLE_COMPANIES:
        for year in [2023, 2024]:
            dir_path = Path(f"data/financial_docs/{company}/{year}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")


def main():
    """Main initialization function"""
    print("🚀 Starting database initialization...\n")
    
    # Create database
    create_database()
    
    # Initialize tables
    engine = init_tables()
    
    # Create sample data
    create_sample_data(engine)
    
    # Create directory structure
    create_directory_structure()
    
    print("\n✅ Database initialization completed!")
    print("\n📌 Next steps:")
    print("1. Place your PDF files in: data/financial_docs/{company}/{year}/")
    print("2. Run the document indexing script: python scripts/index_documents.py")
    print("3. Start the backend server: python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()