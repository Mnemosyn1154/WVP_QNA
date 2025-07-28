#!/usr/bin/env python3
"""
문서 타입 업데이트 스크립트
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.financial_doc import FinancialDoc

# SQLite 데이터베이스
DATABASE_URL = "sqlite:///./portfolio_qa.db"


def update_document_types():
    """마인이스 문서 타입을 재무제표로 업데이트"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 마인이스의 기타문서를 찾아서 재무제표로 변경
        docs = session.query(FinancialDoc).filter_by(
            company_name="마인이스",
            doc_type="기타문서"
        ).all()
        
        for doc in docs:
            doc.doc_type = "재무제표"
            print(f"✅ 업데이트: {doc.company_name} {doc.year}년 - {doc.doc_type}")
        
        # 사업보고서도 재무제표로 변경
        annual_docs = session.query(FinancialDoc).filter_by(
            company_name="마인이스",
            doc_type="사업보고서"
        ).all()
        
        for doc in annual_docs:
            doc.doc_type = "재무제표"
            print(f"✅ 업데이트: {doc.company_name} {doc.year}년 - {doc.doc_type}")
        
        session.commit()
        print("\n✅ 데이터베이스 업데이트 완료!")
        
        # 파일명도 변경
        base_path = Path("data/financial_docs/마인이스")
        
        # 2023년 파일
        old_file_2023 = base_path / "2023" / "마인이스_2023_기타문서.pdf"
        new_file_2023 = base_path / "2023" / "마인이스_2023_재무제표.pdf"
        if old_file_2023.exists():
            old_file_2023.rename(new_file_2023)
            print(f"✅ 파일명 변경: {old_file_2023.name} → {new_file_2023.name}")
        
        # 2024년 파일
        old_file_2024 = base_path / "2024" / "마인이스_2024_사업보고서.pdf"
        new_file_2024 = base_path / "2024" / "마인이스_2024_재무제표.pdf"
        if old_file_2024.exists():
            old_file_2024.rename(new_file_2024)
            print(f"✅ 파일명 변경: {old_file_2024.name} → {new_file_2024.name}")
            
            # DB의 파일 경로도 업데이트
            doc_2024 = session.query(FinancialDoc).filter_by(
                company_name="마인이스",
                year=2024
            ).first()
            if doc_2024:
                doc_2024.file_path = str(new_file_2024).replace(str(Path.cwd()) + "/", "")
                session.commit()
        
        print("\n✅ 모든 업데이트 완료!")
        
        # 현재 상태 확인
        print("\n📊 현재 문서 현황:")
        all_docs = session.query(FinancialDoc).order_by(
            FinancialDoc.company_name, 
            FinancialDoc.year
        ).all()
        
        for doc in all_docs:
            print(f"  - {doc.company_name} {doc.year}년: {doc.doc_type}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 오류 발생: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    update_document_types()