#!/usr/bin/env python3
"""
Setup sample PDF files for testing
Creates dummy PDF files or downloads sample files
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Sample companies
SAMPLE_COMPANIES = ["마인이스", "우나스텔라", "설로인"]


def create_sample_pdf(filepath, company, doc_type, year, quarter=None):
    """Create a sample PDF with Korean financial report content"""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Korean style
    korean_style = ParagraphStyle(
        'Korean',
        parent=styles['Normal'],
        fontName='Helvetica',  # In production, use Korean font
        fontSize=12,
        leading=18
    )
    
    title_style = ParagraphStyle(
        'KoreanTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=1  # Center
    )
    
    # Title
    if quarter:
        title = f"{company} {year}년 {quarter}분기 {doc_type}"
    else:
        title = f"{company} {year}년 {doc_type}"
    
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Company info
    story.append(Paragraph(f"<b>회사명:</b> {company}", korean_style))
    story.append(Paragraph(f"<b>보고서 유형:</b> {doc_type}", korean_style))
    story.append(Paragraph(f"<b>회계연도:</b> {year}년", korean_style))
    if quarter:
        story.append(Paragraph(f"<b>분기:</b> {quarter}분기", korean_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Sample financial data table
    story.append(Paragraph("<b>주요 재무 현황</b>", korean_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Create sample financial data
    data = [
        ['항목', '당기', '전기', '증감률'],
        ['매출액', '80,123', '75,432', '+6.2%'],
        ['영업이익', '12,345', '11,234', '+9.9%'],
        ['당기순이익', '9,876', '8,765', '+12.7%'],
        ['자산총계', '150,000', '140,000', '+7.1%'],
        ['부채총계', '50,000', '48,000', '+4.2%'],
        ['자본총계', '100,000', '92,000', '+8.7%']
    ]
    
    # Create table
    table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Add sample text content
    story.append(Paragraph("<b>사업 개요</b>", korean_style))
    story.append(Paragraph(
        f"{company}는 대한민국을 대표하는 기업으로, 지속적인 혁신과 성장을 통해 "
        f"글로벌 시장에서 경쟁력을 강화하고 있습니다. {year}년에는 특히 "
        f"신사업 분야에서 괄목할만한 성과를 달성하였으며, ESG 경영을 통해 "
        f"지속가능한 성장 기반을 마련하였습니다.",
        korean_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(
        f"본 문서는 테스트용 샘플 문서입니다. 실제 {company}의 {doc_type}가 아닙니다.",
        ParagraphStyle('Footer', parent=korean_style, fontSize=10, textColor=colors.grey)
    ))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {filepath}")


def setup_sample_pdfs():
    """Create sample PDF files for testing"""
    print("📄 Creating sample PDF files...")
    
    # Ensure reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("Installing reportlab for PDF generation...")
        os.system(f"{sys.executable} -m pip install reportlab")
    
    created_count = 0
    
    for company in SAMPLE_COMPANIES:
        for year in [2023, 2024]:
            # Annual report
            dir_path = Path(f"data/financial_docs/{company}/{year}")
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create annual report
            filepath = dir_path / f"{company}_{year}_사업보고서.pdf"
            if not filepath.exists():
                create_sample_pdf(filepath, company, "사업보고서", year)
                created_count += 1
            
            # Create quarterly reports
            for quarter in [1, 2]:
                for doc_type in ["분기보고서", "반기보고서"]:
                    if doc_type == "반기보고서" and quarter != 2:
                        continue  # 반기보고서는 2분기만
                    
                    filename = f"{company}_{year}_Q{quarter}_{doc_type}.pdf"
                    filepath = dir_path / filename
                    if not filepath.exists():
                        create_sample_pdf(filepath, company, doc_type, year, quarter)
                        created_count += 1
    
    print(f"\n✅ Created {created_count} sample PDF files")
    print(f"📁 Files location: data/financial_docs/")
    
    # Create a README in the data directory
    readme_content = """# Sample Data Directory

This directory contains sample PDF files for testing the Q&A chatbot.

## Structure:
```
data/
├── financial_docs/
│   ├── 삼성전자/
│   │   ├── 2023/
│   │   │   ├── 삼성전자_2023_사업보고서.pdf
│   │   │   ├── 삼성전자_2023_Q1_분기보고서.pdf
│   │   │   └── ...
│   │   └── 2024/
│   └── ...
└── news_attachments/
```

## Adding Real Documents:
1. Replace the sample PDFs with actual financial reports
2. Maintain the same directory structure
3. Run the indexing script: `python scripts/index_documents.py`

## Note:
These are dummy PDFs created for testing purposes only.
They do not contain actual financial data.
"""
    
    readme_path = Path("data/README.md")
    readme_path.write_text(readme_content, encoding='utf-8')
    print("📝 Created data/README.md")


def main():
    """Main function"""
    print("🚀 Setting up sample files...\n")
    
    # Check if reportlab is available
    try:
        import reportlab
        setup_sample_pdfs()
    except ImportError:
        print("⚠️  reportlab not found. Installing...")
        os.system(f"{sys.executable} -m pip install reportlab")
        setup_sample_pdfs()
    
    print("\n✅ Sample file setup completed!")
    print("\n📌 Next steps:")
    print("1. Review the generated PDFs in data/financial_docs/")
    print("2. Replace with actual financial documents when available")
    print("3. Run document indexing: python scripts/index_documents.py")


if __name__ == "__main__":
    main()