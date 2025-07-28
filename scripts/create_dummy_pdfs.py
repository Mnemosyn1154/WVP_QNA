"""
Create dummy PDF files for testing
"""
from reportlab.pdfgen import canvas
from pathlib import Path

def create_dummy_pdf(filepath: Path, company: str, year: int):
    """Create a dummy PDF with test content"""
    c = canvas.Canvas(str(filepath))
    
    # Add test content
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, f"{company} {year}년 사업보고서")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"테스트용 더미 문서입니다.")
    c.drawString(100, 680, f"실제 내용은 추후 업로드됩니다.")
    
    # Add some dummy financial data
    c.drawString(100, 640, f"매출액: 1,234억원")
    c.drawString(100, 620, f"영업이익: 234억원")
    c.drawString(100, 600, f"당기순이익: 123억원")
    
    c.save()

def main():
    # Create data directory
    data_dir = Path("data/financial_docs")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Companies and their dummy PDFs
    companies = [
        ("마인이스", 2024),
        ("우나스텔라", 2024),
        ("설로인", 2024)
    ]
    
    for company, year in companies:
        filename = f"{company}_{year}_사업보고서.pdf"
        filepath = data_dir / filename
        
        if not filepath.exists():
            create_dummy_pdf(filepath, company, year)
            print(f"Created: {filepath}")
        else:
            print(f"Already exists: {filepath}")

if __name__ == "__main__":
    main()