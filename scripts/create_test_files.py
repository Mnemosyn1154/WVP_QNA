"""
Create test files for development
"""
from pathlib import Path

def create_test_file(filepath: Path, company: str, year: int):
    """Create a test file with dummy content"""
    content = f"""
{company} {year}년 사업보고서

테스트용 더미 문서입니다.

주요 재무 정보:
- 매출액: 1,234억원
- 영업이익: 234억원  
- 당기순이익: 123억원

사업 개요:
{company}는 혁신적인 기술을 보유한 기업으로, 지속적인 성장을 이어가고 있습니다.

주요 사업 분야:
1. AI 솔루션 개발
2. 클라우드 서비스
3. 데이터 분석

향후 전망:
{year+1}년에도 지속적인 성장이 예상됩니다.
"""
    
    filepath.write_text(content, encoding='utf-8')

def main():
    # Create data directory
    data_dir = Path("data/financial_docs")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Companies and their test files
    companies = [
        ("마인이스", 2024),
        ("우나스텔라", 2024),
        ("설로인", 2024)
    ]
    
    for company, year in companies:
        # Create as .txt for now (will be treated as PDF in test)
        filename = f"{company}_{year}_사업보고서.pdf"
        filepath = data_dir / filename
        
        if not filepath.exists():
            create_test_file(filepath, company, year)
            print(f"Created: {filepath}")
        else:
            print(f"Already exists: {filepath}")

if __name__ == "__main__":
    main()