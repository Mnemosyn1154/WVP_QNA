#!/usr/bin/env python3
"""
문서 파일 정리 및 메타데이터 추출 스크립트
- 업로드된 파일들의 이름을 분석하여 정리
- 데이터베이스에 메타데이터 저장
"""

import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.financial_doc import FinancialDoc

# SQLite를 사용한 간단한 설정
DATABASE_URL = "sqlite:///./portfolio_qa.db"


class DocumentOrganizer:
    """문서 파일 정리 및 분석 클래스"""
    
    def __init__(self):
        self.base_path = Path("data/financial_docs")
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        # 테이블 생성 (없을 경우)
        from app.models.base import Base
        Base.metadata.create_all(bind=self.engine)
        
        # 문서 타입 매핑
        self.doc_type_patterns = {
            "사업보고서": ["사업보고서", "annual", "연간"],
            "분기보고서": ["분기", "quarter", r"\dQ", "1Q", "2Q", "3Q", "4Q"],
            "반기보고서": ["반기", "half"],
            "재무제표": ["재무제표", "financial", "가결산"],
        }
        
    def analyze_filename(self, filename):
        """파일명 분석하여 메타데이터 추출"""
        metadata = {
            "doc_type": None,
            "year": None,
            "quarter": None,
            "original_filename": filename
        }
        
        # 연도 추출 (2023, 2024, 23, 24 등)
        year_patterns = [
            r"20(\d{2})",  # 2023, 2024
            r"(\d{2})년",   # 23년, 24년
            r"_(\d{2})\.",  # _23., _24.
            r"(\d{4})\.?(?:12|Q|q)",  # 202312, 2024Q
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, filename)
            if match:
                year_str = match.group(1)
                if len(year_str) == 2:
                    metadata["year"] = 2000 + int(year_str)
                else:
                    metadata["year"] = int(year_str)
                break
        
        # 문서 타입 추출
        filename_lower = filename.lower()
        for doc_type, patterns in self.doc_type_patterns.items():
            for pattern in patterns:
                if isinstance(pattern, str):
                    if pattern.lower() in filename_lower:
                        metadata["doc_type"] = doc_type
                        break
                else:  # regex pattern
                    if re.search(pattern, filename, re.IGNORECASE):
                        metadata["doc_type"] = doc_type
                        break
            if metadata["doc_type"]:
                break
        
        # 분기 추출
        quarter_match = re.search(r"(\d)[Qq]|Q(\d)|(\d)분기", filename)
        if quarter_match:
            quarter_num = quarter_match.group(1) or quarter_match.group(2) or quarter_match.group(3)
            metadata["quarter"] = int(quarter_num)
        
        # 4Q가 있으면 사업보고서로 분류
        if "4Q" in filename or "4q" in filename:
            metadata["doc_type"] = "사업보고서"
            metadata["quarter"] = None
        
        return metadata
    
    def generate_new_filename(self, company, metadata):
        """표준화된 파일명 생성"""
        year = metadata["year"]
        doc_type = metadata["doc_type"] or "기타문서"
        quarter = metadata["quarter"]
        
        if quarter and doc_type != "사업보고서":
            new_name = f"{company}_{year}_Q{quarter}_{doc_type}.pdf"
        else:
            new_name = f"{company}_{year}_{doc_type}.pdf"
        
        return new_name
    
    def calculate_file_hash(self, filepath):
        """파일 해시 계산"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def process_company_documents(self, company_name):
        """특정 회사의 문서들 처리"""
        company_path = self.base_path / company_name
        if not company_path.exists():
            print(f"⚠️  {company_name} 폴더가 없습니다.")
            return
        
        print(f"\n📁 {company_name} 문서 처리 중...")
        processed = 0
        
        session = self.Session()
        
        try:
            # 모든 PDF 파일 찾기
            for year_dir in company_path.iterdir():
                if not year_dir.is_dir():
                    continue
                    
                year = year_dir.name
                
                for file_path in year_dir.glob("*.[pP][dD][fF]"):
                    print(f"\n  파일: {file_path.name}")
                    
                    # 파일명 분석
                    metadata = self.analyze_filename(file_path.name)
                    
                    # 연도가 파일명에서 추출되지 않으면 폴더명 사용
                    if not metadata["year"]:
                        try:
                            metadata["year"] = int(year)
                        except ValueError:
                            print(f"    ⚠️  연도를 확인할 수 없습니다: {year}")
                            continue
                    
                    print(f"    분석 결과: 연도={metadata['year']}, "
                          f"타입={metadata['doc_type']}, 분기={metadata['quarter']}")
                    
                    # 새 파일명 생성
                    new_filename = self.generate_new_filename(company_name, metadata)
                    new_path = file_path.parent / new_filename
                    
                    # 파일명 변경 (필요한 경우)
                    if file_path.name != new_filename:
                        if new_path.exists():
                            print(f"    ⚠️  대상 파일이 이미 존재합니다: {new_filename}")
                        else:
                            shutil.move(str(file_path), str(new_path))
                            print(f"    ✅ 파일명 변경: {file_path.name} → {new_filename}")
                            file_path = new_path
                    
                    # DB에 저장
                    existing = session.query(FinancialDoc).filter_by(
                        company_name=company_name,
                        year=metadata["year"],
                        doc_type=metadata["doc_type"],
                        quarter=metadata["quarter"]
                    ).first()
                    
                    if existing:
                        print(f"    ℹ️  이미 DB에 등록되어 있습니다.")
                    else:
                        # 파일 정보 수집
                        file_size = file_path.stat().st_size
                        file_hash = self.calculate_file_hash(file_path)
                        # 프로젝트 루트 기준 상대 경로
                        relative_path = str(file_path).replace(str(Path.cwd()) + "/", "")
                        
                        doc = FinancialDoc(
                            company_name=company_name,
                            doc_type=metadata["doc_type"] or "기타문서",
                            year=metadata["year"],
                            quarter=metadata["quarter"],
                            file_path=str(relative_path),
                            file_size=file_size,
                            # file_hash=file_hash  # 모델에 추가 필요시
                        )
                        
                        session.add(doc)
                        print(f"    ✅ DB에 등록되었습니다.")
                    
                    processed += 1
            
            session.commit()
            print(f"\n✅ {company_name}: {processed}개 파일 처리 완료")
            
        except Exception as e:
            session.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise
        finally:
            session.close()
    
    def process_excel_files(self):
        """엑셀 파일 처리 (별도 폴더로 이동)"""
        excel_dir = self.base_path.parent / "excel_files"
        excel_dir.mkdir(exist_ok=True)
        
        moved = 0
        for company_path in self.base_path.iterdir():
            if not company_path.is_dir():
                continue
                
            for excel_file in company_path.rglob("*.xlsx"):
                target = excel_dir / company_path.name / excel_file.parent.name / excel_file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(excel_file), str(target))
                print(f"  📊 엑셀 파일 이동: {excel_file} → {target}")
                moved += 1
        
        if moved > 0:
            print(f"\n✅ {moved}개 엑셀 파일을 별도 폴더로 이동했습니다.")
    
    def run(self):
        """전체 문서 정리 프로세스 실행"""
        print("🚀 문서 정리 및 DB 등록 시작...\n")
        
        # 엑셀 파일 별도 처리
        self.process_excel_files()
        
        # 각 회사별 처리
        companies = ["마인이스", "설로인", "우나스텔라"]
        for company in companies:
            self.process_company_documents(company)
        
        print("\n✅ 모든 문서 정리 완료!")
        print("\n📌 다음 단계:")
        print("1. 문서 인덱싱: python scripts/index_documents.py")
        print("2. 서버 실행: python test_server.py")


def main():
    """메인 함수"""
    organizer = DocumentOrganizer()
    organizer.run()


if __name__ == "__main__":
    main()