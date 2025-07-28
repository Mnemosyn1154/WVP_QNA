"""
Test script for PDF splitting functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_splitter import PDFSplitter
import glob
import json


def create_large_test_pdf():
    """Create a large test PDF for splitting tests"""
    import fitz
    
    # Create a PDF with many pages
    pdf = fitz.open()
    
    for page_num in range(100):  # 100 pages
        page = pdf.new_page(width=595, height=842)  # A4 size
        
        # Add some text content
        text = f"""
페이지 {page_num + 1}

이것은 테스트 PDF 문서입니다.
PDF 분할 기능을 테스트하기 위한 샘플 페이지입니다.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

재무 데이터 예시:
- 매출: 1,234,567,890원
- 영업이익: 234,567,890원
- 당기순이익: 123,456,789원
"""
        
        text_rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(text_rect, text, fontsize=11, fontname="helv")
        
        # Add a simple table
        table_start_y = 400
        for row in range(5):
            for col in range(4):
                cell_rect = fitz.Rect(50 + col * 120, table_start_y + row * 25, 
                                     165 + col * 120, table_start_y + (row + 1) * 25)
                page.draw_rect(cell_rect)
                page.insert_text((55 + col * 120, table_start_y + row * 25 + 15), 
                               f"Cell {row},{col}")
    
    # Save the PDF
    content = pdf.tobytes()
    pdf.close()
    
    return content, "large_test_document.pdf"


def test_pdf_splitting():
    """Test PDF splitting functionality"""
    splitter = PDFSplitter()
    
    print("PDF Splitter Test")
    print("=" * 60)
    print(f"Max file size: {splitter.claude_api_max_size_mb} MB")
    print()
    
    results = []
    
    # Test 1: Small PDF that doesn't need splitting
    print("Test 1: Small PDF (should not split)")
    print("-" * 40)
    small_pdf_path = "data/financial_docs/마인이스/2024/마인이스_2024_재무제표.pdf"
    
    if os.path.exists(small_pdf_path):
        with open(small_pdf_path, "rb") as f:
            content = f.read()
        
        split_files, metadata = splitter.check_and_split(content, os.path.basename(small_pdf_path))
        
        print(f"Original size: {metadata['original_size_mb']} MB")
        print(f"Needs splitting: {metadata['needs_splitting']}")
        print(f"Split performed: {metadata['split_performed']}")
        print()
        
        results.append({
            "test": "Small PDF",
            "file": os.path.basename(small_pdf_path),
            "result": metadata
        })
    
    # Test 2: Create and test large PDF
    print("Test 2: Large PDF (should split)")
    print("-" * 40)
    
    large_content, large_filename = create_large_test_pdf()
    large_size_mb = len(large_content) / (1024 * 1024)
    print(f"Created test PDF: {large_size_mb:.2f} MB with 100 pages")
    
    # Save it temporarily to test file size
    with open("test_large.pdf", "wb") as f:
        f.write(large_content)
    
    split_files, metadata = splitter.check_and_split(large_content, large_filename)
    
    print(f"Original size: {metadata['original_size_mb']} MB")
    print(f"Needs splitting: {metadata['needs_splitting']}")
    print(f"Split performed: {metadata['split_performed']}")
    
    if metadata['split_performed']:
        print(f"Split into {metadata['split_count']} files")
        print(f"Pages per chunk: {metadata['pages_per_chunk']}")
        print("\nSplit files:")
        for file_info in split_files:
            print(f"  - {file_info['filename']}: {file_info['size_mb']} MB, "
                  f"{file_info['pages']} pages ({file_info.get('page_range', 'N/A')})")
    
    results.append({
        "test": "Large PDF",
        "file": large_filename,
        "result": metadata,
        "split_files": len(split_files) if metadata['split_performed'] else 0
    })
    
    # Test 3: Custom pages per chunk
    print("\nTest 3: Custom pages per chunk (10 pages)")
    print("-" * 40)
    
    split_files_custom, metadata_custom = splitter.check_and_split(
        large_content, 
        "custom_chunk_test.pdf",
        pages_per_chunk=10
    )
    
    print(f"Split into {metadata_custom.get('split_count', 0)} files")
    print(f"Pages per chunk: {metadata_custom.get('pages_per_chunk', 'N/A')}")
    
    # Test 4: Calculate optimal chunk size
    print("\nTest 4: Calculate optimal chunk size")
    print("-" * 40)
    
    optimal_pages = splitter.calculate_optimal_chunk_size(large_content, target_chunk_size_mb=5.0)
    print(f"Optimal pages per chunk for 5MB target: {optimal_pages}")
    
    # Generate report
    print("\n" + "=" * 60)
    print("Sample Split Report:")
    print("=" * 60)
    report = splitter.get_split_report(split_files, metadata)
    print(report)
    
    # Save results
    with open("pdf_splitter_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\nTest results saved to pdf_splitter_test_results.json")
    
    # Clean up
    if os.path.exists("test_large.pdf"):
        os.remove("test_large.pdf")


if __name__ == "__main__":
    test_pdf_splitting()