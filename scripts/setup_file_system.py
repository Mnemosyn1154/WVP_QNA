#!/usr/bin/env python3
"""
Setup file system structure for financial documents
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings


def create_file_structure():
    """Create the required directory structure for document storage"""
    
    base_path = Path(settings.DATA_PATH)
    financial_docs_path = Path(settings.FINANCIAL_DOCS_PATH)
    cache_path = Path(settings.CACHE_PATH)
    
    # Create main directories
    directories = [
        base_path,
        financial_docs_path,
        cache_path,
        cache_path / "embeddings"
    ]
    
    # Create sample company directories
    sample_companies = [
        "삼성전자", "LG전자", "SK하이닉스", "현대자동차", "POSCO",
        "네이버", "카카오", "셀트리온", "삼성바이오로직스", "현대모비스"
    ]
    
    for company in sample_companies:
        company_path = financial_docs_path / company
        directories.append(company_path)
        
        # Create year directories (2022-2024)
        for year in range(2022, 2025):
            year_path = company_path / str(year)
            directories.append(year_path)
    
    # Create all directories
    created_count = 0
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            created_count += 1
        else:
            logger.info(f"Directory already exists: {directory}")
    
    # Create metadata file
    metadata_file = base_path / "metadata.json"
    if not metadata_file.exists():
        metadata = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "companies": sample_companies,
            "document_types": ["사업보고서", "반기보고서", "분기보고서"],
            "years": list(range(2022, 2025))
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created metadata file: {metadata_file}")
    
    return {
        "directories_created": created_count,
        "total_directories": len(directories),
        "base_path": str(base_path),
        "companies": sample_companies
    }


def create_sample_documents():
    """Create sample PDF placeholder files for testing"""
    
    financial_docs_path = Path(settings.FINANCIAL_DOCS_PATH)
    
    # Sample document templates
    doc_templates = [
        {"type": "사업보고서", "filename": "annual_report_{year}.pdf"},
        {"type": "반기보고서", "filename": "half_year_report_{year}.pdf"},
        {"type": "1분기보고서", "filename": "Q1_report_{year}.pdf"},
        {"type": "3분기보고서", "filename": "Q3_report_{year}.pdf"}
    ]
    
    sample_companies = ["삼성전자", "LG전자", "SK하이닉스"]
    created_files = []
    
    for company in sample_companies:
        for year in [2023, 2024]:
            for template in doc_templates:
                # Skip quarters for 2024 if it's early in the year
                if year == 2024 and template["type"] not in ["사업보고서", "1분기보고서"]:
                    continue
                
                filename = template["filename"].format(year=year)
                file_path = financial_docs_path / company / str(year) / filename
                
                # Create a placeholder text file (in real scenario, these would be PDFs)
                if not file_path.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create sample content
                    content = f"""
{company} {year}년 {template['type']}

1. 회사 개요
- 회사명: {company}
- 보고서 유형: {template['type']}
- 회계연도: {year}

2. 주요 재무 정보
- 매출액: {1234 * (year - 2020)}억원
- 영업이익: {123 * (year - 2020)}억원
- 당기순이익: {100 * (year - 2020)}억원

3. 주요 사업 현황
- 주력 제품 매출 성장
- 신규 사업 진출
- R&D 투자 확대

(이것은 테스트를 위한 샘플 문서입니다)
"""
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    created_files.append(str(file_path))
                    logger.info(f"Created sample file: {file_path}")
    
    return created_files


def main():
    """Main function"""
    logger.info("Starting file system setup...")
    
    # Create directory structure
    result = create_file_structure()
    logger.info(f"Directory structure created: {result}")
    
    # Create sample documents
    if "--with-samples" in sys.argv:
        logger.info("Creating sample documents...")
        sample_files = create_sample_documents()
        logger.info(f"Created {len(sample_files)} sample files")
    
    logger.info("File system setup completed!")
    
    # Print summary
    print("\n=== File System Setup Summary ===")
    print(f"Base path: {result['base_path']}")
    print(f"Directories created: {result['directories_created']}")
    print(f"Total directories: {result['total_directories']}")
    print(f"Companies configured: {', '.join(result['companies'][:5])}...")
    print("\nTo create sample documents, run with --with-samples flag")


if __name__ == "__main__":
    main()