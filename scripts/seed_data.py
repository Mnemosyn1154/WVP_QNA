#!/usr/bin/env python3
"""
Seed database with sample data for development and testing
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.financial_doc import FinancialDoc
from app.models.news import News
from app.models.portfolio_company import PortfolioCompany
from app.models.chat_history import ChatHistory
from sqlalchemy import select
import os
from loguru import logger


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0


def seed_portfolio_companies():
    """Seed portfolio companies"""
    companies = [
        {
            "name": "마인이스",
            "industry": "IT/소프트웨어",
            "description": "AI 기반 빅데이터 분석 솔루션 전문 기업",
            "website": "https://mineis.com"
        },
        {
            "name": "설로인",
            "industry": "식품/유통",
            "description": "프리미엄 한우 유통 및 레스토랑 프랜차이즈",
            "website": "https://sulloin.com"
        },
        {
            "name": "우나스텔라",
            "industry": "헬스케어",
            "description": "디지털 헬스케어 플랫폼 및 원격의료 서비스",
            "website": "https://unastella.com"
        }
    ]
    
    db = SessionLocal()
    try:
        # Check if companies already exist
        existing = db.query(PortfolioCompany).all()
        if existing:
            logger.info(f"Portfolio companies already exist: {len(existing)}")
            return
        
        # Add companies
        for company_data in companies:
            company = PortfolioCompany(**company_data)
            db.add(company)
        
        db.commit()
        logger.info(f"Added {len(companies)} portfolio companies")
        
    except Exception as e:
        logger.error(f"Error seeding portfolio companies: {e}")
        db.rollback()
    finally:
        db.close()


def seed_financial_documents():
    """Seed financial documents based on actual files"""
    db = SessionLocal()
    
    try:
        # Check if documents already exist
        existing_count = db.query(FinancialDoc).count()
        if existing_count > 0:
            logger.info(f"Financial documents already exist: {existing_count}")
            return
        
        # Base path for documents
        base_path = Path("data/financial_docs")
        
        # Find all PDF files
        documents = []
        for company_dir in base_path.iterdir():
            if company_dir.is_dir():
                company_name = company_dir.name
                for year_dir in company_dir.iterdir():
                    if year_dir.is_dir():
                        year = year_dir.name
                        for pdf_file in year_dir.glob("*.pdf"):
                            # Determine document type from filename
                            doc_type = "재무제표"
                            if "사업보고서" in pdf_file.name:
                                doc_type = "사업보고서"
                            elif "반기보고서" in pdf_file.name:
                                doc_type = "반기보고서"
                            
                            doc = FinancialDoc(
                                company_name=company_name,
                                doc_type=doc_type,
                                year=int(year),
                                file_path=str(pdf_file),
                                file_size=get_file_size(pdf_file)
                            )
                            documents.append(doc)
                            db.add(doc)
        
        db.commit()
        logger.info(f"Added {len(documents)} financial documents")
        
        # Log details
        for doc in documents:
            logger.debug(f"  - {doc.company_name} {doc.year} {doc.doc_type}: {doc.file_path}")
        
    except Exception as e:
        logger.error(f"Error seeding financial documents: {e}")
        db.rollback()
    finally:
        db.close()


def seed_news_articles():
    """Seed sample news articles"""
    db = SessionLocal()
    
    try:
        # Check if news already exist
        existing_count = db.query(News).count()
        if existing_count > 0:
            logger.info(f"News articles already exist: {existing_count}")
            return
        
        # Sample news data
        news_templates = [
            # 마인이스 뉴스
            {
                "company_name": "마인이스",
                "title": "마인이스, AI 빅데이터 플랫폼 2.0 출시",
                "content": "마인이스가 차세대 AI 빅데이터 분석 플랫폼 2.0을 출시했다. 이번 플랫폼은 실시간 데이터 처리 속도를 기존 대비 3배 향상시켰으며, 자연어 처리 기능을 대폭 강화했다.",
                "source": "테크뉴스",
                "published_date": datetime.now() - timedelta(days=5)
            },
            {
                "company_name": "마인이스",
                "title": "마인이스, 글로벌 AI 기업과 전략적 파트너십 체결",
                "content": "마인이스가 글로벌 AI 선도 기업과 전략적 파트너십을 체결했다. 이번 협력을 통해 양사는 AI 기술 공동 개발 및 해외 시장 진출을 가속화할 예정이다.",
                "source": "비즈니스타임즈",
                "published_date": datetime.now() - timedelta(days=15)
            },
            {
                "company_name": "마인이스",
                "title": "마인이스, 2024년 매출 30% 성장 전망",
                "content": "마인이스가 2024년 매출 목표를 전년 대비 30% 성장으로 설정했다. 신규 고객 확보와 기존 제품 업그레이드를 통해 시장 점유율을 확대할 계획이다.",
                "source": "경제일보",
                "published_date": datetime.now() - timedelta(days=30)
            },
            
            # 설로인 뉴스
            {
                "company_name": "설로인",
                "title": "설로인, 프리미엄 한우 레스토랑 10호점 오픈",
                "content": "프리미엄 한우 전문 기업 설로인이 강남구에 10호점을 오픈했다. 이번 매장은 플래그십 스토어로 와인 셀러와 프라이빗 다이닝룸을 갖추고 있다.",
                "source": "식품저널",
                "published_date": datetime.now() - timedelta(days=7)
            },
            {
                "company_name": "설로인",
                "title": "설로인, 온라인 정육 플랫폼 '설로인몰' 런칭",
                "content": "설로인이 프리미엄 한우를 온라인으로 구매할 수 있는 '설로인몰'을 런칭했다. 당일 도축한 신선한 한우를 익일 배송하는 서비스를 제공한다.",
                "source": "유통신문",
                "published_date": datetime.now() - timedelta(days=20)
            },
            {
                "company_name": "설로인",
                "title": "설로인, ESG 경영 우수기업 선정",
                "content": "설로인이 축산업계 ESG 경영 우수기업으로 선정됐다. 친환경 사육 시스템과 지역 농가와의 상생 협력이 높은 평가를 받았다.",
                "source": "ESG경제",
                "published_date": datetime.now() - timedelta(days=45)
            },
            
            # 우나스텔라 뉴스
            {
                "company_name": "우나스텔라",
                "title": "우나스텔라, 원격진료 플랫폼 이용자 100만 돌파",
                "content": "디지털 헬스케어 기업 우나스텔라의 원격진료 플랫폼 이용자가 100만 명을 돌파했다. 코로나19 이후 비대면 의료 서비스 수요가 급증하며 빠른 성장세를 보이고 있다.",
                "source": "헬스조선",
                "published_date": datetime.now() - timedelta(days=3)
            },
            {
                "company_name": "우나스텔라",
                "title": "우나스텔라, AI 진단 보조 시스템 FDA 승인",
                "content": "우나스텔라가 개발한 AI 기반 진단 보조 시스템이 미국 FDA 승인을 받았다. 이 시스템은 의료 영상을 분석해 질병을 조기에 발견하는 데 도움을 준다.",
                "source": "메디컬투데이",
                "published_date": datetime.now() - timedelta(days=10)
            },
            {
                "company_name": "우나스텔라",
                "title": "우나스텔라, 대형 병원과 디지털 헬스케어 MOU 체결",
                "content": "우나스텔라가 국내 대형 병원들과 디지털 헬스케어 협력을 위한 MOU를 체결했다. 이번 협약을 통해 병원의 디지털 전환을 지원할 예정이다.",
                "source": "의료신문",
                "published_date": datetime.now() - timedelta(days=25)
            }
        ]
        
        # Add news articles
        for news_data in news_templates:
            news = News(**news_data)
            db.add(news)
        
        db.commit()
        logger.info(f"Added {len(news_templates)} news articles")
        
    except Exception as e:
        logger.error(f"Error seeding news articles: {e}")
        db.rollback()
    finally:
        db.close()


def seed_sample_chat_history():
    """Seed sample chat history"""
    db = SessionLocal()
    
    try:
        # Check if chat history already exists
        existing_count = db.query(ChatHistory).count()
        if existing_count > 0:
            logger.info(f"Chat history already exists: {existing_count}")
            return
        
        # Sample chat history
        chats = [
            {
                "question": "마인이스의 2024년 매출은 얼마인가요?",
                "answer": "마인이스의 2024년 매출액은 29억 7,635만원입니다. 이는 전년 대비 약 15% 성장한 수치입니다.",
                "context": {"company": "마인이스", "year": 2024, "doc_type": "재무제표"}
            },
            {
                "question": "설로인의 주요 사업은 무엇인가요?",
                "answer": "설로인은 프리미엄 한우 유통 및 레스토랑 프랜차이즈를 운영하는 기업입니다. 주요 사업은 한우 직영 레스토랑 운영과 프리미엄 정육 유통입니다.",
                "context": {"company": "설로인", "source": "company_info"}
            },
            {
                "question": "우나스텔라의 최근 뉴스를 알려주세요",
                "answer": "우나스텔라의 최근 주요 뉴스는 다음과 같습니다:\n1. 원격진료 플랫폼 이용자 100만 돌파\n2. AI 진단 보조 시스템 FDA 승인\n3. 대형 병원과 디지털 헬스케어 MOU 체결",
                "context": {"company": "우나스텔라", "source": "news", "count": 3}
            }
        ]
        
        # Add chat history
        for i, chat_data in enumerate(chats):
            chat = ChatHistory(
                **chat_data,
                created_at=datetime.now() - timedelta(hours=i*2)
            )
            db.add(chat)
        
        db.commit()
        logger.info(f"Added {len(chats)} chat history entries")
        
    except Exception as e:
        logger.error(f"Error seeding chat history: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function to seed all data"""
    logger.info("Starting database seeding...")
    
    # Seed data in order
    logger.info("1. Seeding portfolio companies...")
    seed_portfolio_companies()
    
    logger.info("2. Seeding financial documents...")
    seed_financial_documents()
    
    logger.info("3. Seeding news articles...")
    seed_news_articles()
    
    logger.info("4. Seeding sample chat history...")
    seed_sample_chat_history()
    
    logger.info("Database seeding completed!")
    
    # Show summary
    db = SessionLocal()
    try:
        doc_count = db.query(FinancialDoc).count()
        news_count = db.query(News).count()
        chat_count = db.query(ChatHistory).count()
        company_count = db.query(PortfolioCompany).count()
        
        print("\n=== Seeding Summary ===")
        print(f"Portfolio companies: {company_count}")
        print(f"Financial documents: {doc_count}")
        print(f"News articles: {news_count}")
        print(f"Chat history: {chat_count}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()