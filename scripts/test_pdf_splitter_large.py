"""
Test PDF splitter with a truly large PDF
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_splitter import PDFSplitter
import fitz


def create_very_large_pdf():
    """Create a very large PDF that exceeds 10MB"""
    pdf = fitz.open()
    
    # Create 500 pages with images
    for page_num in range(500):
        page = pdf.new_page(width=595, height=842)  # A4
        
        # Add substantial text content
        long_text = f"""
페이지 {page_num + 1} / 500

투자 포트폴리오 분석 보고서
========================

1. 재무 상태표 (단위: 백만원)
------------------------------
자산 총계: 123,456,789
부채 총계: 45,678,901
자본 총계: 77,777,888

2. 손익계산서
------------------------------
매출액: 98,765,432
매출원가: 65,432,109
매출총이익: 33,333,323
판매관리비: 12,345,678
영업이익: 20,987,645
당기순이익: 15,432,198

3. 현금흐름표
------------------------------
영업활동 현금흐름: 25,678,901
투자활동 현금흐름: -10,234,567
재무활동 현금흐름: -5,444,334
현금및현금성자산 증감: 10,000,000

""" * 3  # Repeat 3 times to make it larger
        
        # Add text
        text_rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(text_rect, long_text, fontsize=10, fontname="helv")
        
        # Add some graphical elements to increase size
        for i in range(10):
            page.draw_circle(fitz.Point(100 + i * 40, 700), 20)
            page.draw_rect(fitz.Rect(100 + i * 40, 720, 120 + i * 40, 740))
    
    content = pdf.tobytes()
    pdf.close()
    
    return content


def test_large_pdf_splitting():
    """Test with a truly large PDF"""
    splitter = PDFSplitter()
    
    print("Creating very large test PDF...")
    large_content = create_very_large_pdf()
    size_mb = len(large_content) / (1024 * 1024)
    
    print(f"Created PDF: {size_mb:.2f} MB with 500 pages")
    print()
    
    # Force a smaller max size for testing
    original_max_size = splitter.claude_api_max_size_mb
    splitter.claude_api_max_size_mb = 0.5  # Set to 0.5MB for testing
    splitter.claude_api_max_size = int(0.5 * 1024 * 1024)
    
    print(f"Testing with max size limit: {splitter.claude_api_max_size_mb} MB")
    print("-" * 60)
    
    # Test splitting
    split_files, metadata = splitter.check_and_split(
        large_content,
        "very_large_test.pdf",
        pages_per_chunk=50
    )
    
    print(f"Original size: {metadata['original_size_mb']} MB")
    print(f"Needs splitting: {metadata['needs_splitting']}")
    print(f"Split performed: {metadata['split_performed']}")
    
    if metadata['split_performed']:
        print(f"\nSplit into {metadata['split_count']} files:")
        for idx, file_info in enumerate(split_files, 1):
            status = "✓" if file_info['size_mb'] <= splitter.claude_api_max_size_mb else "✗"
            print(f"{status} File {idx}: {file_info['filename']}")
            print(f"   Size: {file_info['size_mb']} MB")
            print(f"   Pages: {file_info['pages']} ({file_info.get('page_range', 'N/A')})")
    
    # Generate report
    report = splitter.get_split_report(split_files, metadata)
    print("\n" + report)
    
    # Test optimal chunk calculation
    print("\nCalculating optimal chunk size...")
    optimal = splitter.calculate_optimal_chunk_size(large_content, target_chunk_size_mb=1.5)
    print(f"Optimal pages per chunk for 1.5MB target: {optimal}")
    
    # Restore original max size
    splitter.claude_api_max_size_mb = original_max_size


if __name__ == "__main__":
    test_large_pdf_splitting()