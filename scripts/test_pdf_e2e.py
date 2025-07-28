"""
End-to-End PDF Processing Test Suite
Tests the complete pipeline: optimization -> splitting -> Claude API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import fitz  # PyMuPDF

from app.services.pdf_optimizer import PDFOptimizer, CompressionLevel
from app.services.pdf_splitter import PDFSplitter
from app.services.claude_service import ClaudeService
from app.core.config import settings


class PDFTestCase:
    """Represents a test case for PDF processing"""
    
    def __init__(self, name: str, description: str, pdf_path: str = None):
        self.name = name
        self.description = description
        self.pdf_path = pdf_path
        self.content = None
        self.results = {}
        
    def create_test_pdf(self) -> bytes:
        """Override this method to create test PDFs"""
        raise NotImplementedError
        
    def get_test_questions(self) -> List[str]:
        """Return questions to ask Claude about this PDF"""
        return [
            "이 문서의 주요 내용을 요약해주세요.",
            "문서에 포함된 주요 수치나 데이터를 알려주세요."
        ]


class TextHeavyPDFTest(PDFTestCase):
    """Test case for text-heavy financial reports"""
    
    def create_test_pdf(self) -> bytes:
        pdf = fitz.open()
        
        # Create 30 pages of dense financial text
        for page_num in range(30):
            page = pdf.new_page(width=595, height=842)
            
            text = f"""
2024년 재무제표 - 페이지 {page_num + 1}

1. 재무상태표 (단위: 백만원)
===========================
자산
  유동자산
    현금및현금성자산          12,345,678
    단기금융상품              8,765,432
    매출채권                  5,432,109
    재고자산                  3,210,987
  비유동자산
    유형자산                  45,678,901
    무형자산                  12,345,678
    
부채
  유동부채
    매입채무                  4,567,890
    단기차입금                2,345,678
  비유동부채
    장기차입금                15,678,901
    
자본
  자본금                      10,000,000
  자본잉여금                  25,678,901
  이익잉여금                  35,432,109

2. 손익계산서
===========================
매출액                        98,765,432
매출원가                      (65,432,109)
매출총이익                    33,333,323
판매관리비                    (12,345,678)
영업이익                      20,987,645
금융수익                      1,234,567
금융비용                      (2,345,678)
법인세차감전순이익            19,876,534
법인세비용                    (4,444,336)
당기순이익                    15,432,198
"""
            
            text_rect = fitz.Rect(50, 50, 545, 792)
            page.insert_textbox(text_rect, text, fontsize=9, fontname="helv")
        
        content = pdf.tobytes()
        pdf.close()
        return content


class ImageHeavyPDFTest(PDFTestCase):
    """Test case for image-heavy reports"""
    
    def create_test_pdf(self) -> bytes:
        pdf = fitz.open()
        
        # Create 20 pages with images and charts
        for page_num in range(20):
            page = pdf.new_page(width=595, height=842)
            
            # Add title
            page.insert_text((50, 50), f"차트 및 그래프 분석 - 페이지 {page_num + 1}", fontsize=14)
            
            # Simulate charts with shapes
            # Bar chart
            for i in range(5):
                height = 50 + i * 20
                rect = fitz.Rect(100 + i * 80, 400 - height, 150 + i * 80, 400)
                page.draw_rect(rect, fill=(0.2, 0.4, 0.8))
                page.insert_text((110 + i * 80, 420), f"{(i+1)*1000}억", fontsize=8)
            
            # Pie chart simulation
            center = fitz.Point(400, 600)
            page.draw_circle(center, 80, fill=(0.9, 0.9, 0.9))
            
            # Add data table
            table_text = """
            구분        2023년      2024년      증감률
            매출        1,234       1,567       27.0%
            영업이익      234         345       47.4%
            순이익        123         198       61.0%
            """
            page.insert_text((50, 700), table_text, fontsize=10)
        
        content = pdf.tobytes()
        pdf.close()
        return content


class ScannedPDFTest(PDFTestCase):
    """Test case for scanned documents"""
    
    def create_test_pdf(self) -> bytes:
        pdf = fitz.open()
        
        # Create 10 pages simulating scanned content
        for page_num in range(10):
            page = pdf.new_page(width=595, height=842)
            
            # Add background to simulate scan
            page.draw_rect(page.rect, fill=(0.95, 0.95, 0.92))
            
            # Add slightly rotated text to simulate scan imperfection
            text = f"""
주주총회 의사록 - {page_num + 1}페이지

일시: 2024년 3월 15일
장소: 본사 대회의실

안건:
1. 2023년 재무제표 승인의 건
2. 이사 선임의 건
3. 감사 선임의 건
4. 정관 변경의 건

의결사항:
- 제1호 의안: 원안대로 가결
- 제2호 의안: 원안대로 가결
- 제3호 의안: 수정 가결
- 제4호 의안: 부결

특별결의사항:
배당금 주당 500원 지급 결정
"""
            
            # Add text with slight gray color to simulate scan
            text_rect = fitz.Rect(60, 60, 535, 782)
            page.insert_textbox(text_rect, text, fontsize=11, 
                              fontname="helv", color=(0.2, 0.2, 0.2))
        
        content = pdf.tobytes()
        pdf.close()
        return content


class VeryLargePDFTest(PDFTestCase):
    """Test case for very large PDFs that require splitting"""
    
    def create_test_pdf(self) -> bytes:
        pdf = fitz.open()
        
        # Create 200 pages to ensure > 10MB
        for page_num in range(200):
            page = pdf.new_page(width=595, height=842)
            
            # Create dense content
            long_text = f"페이지 {page_num + 1}\n" + ("=" * 50) + "\n"
            
            # Add substantial content
            for section in range(5):
                long_text += f"""
섹션 {section + 1}: 상세 분석 보고서

본 섹션에서는 2024년 {page_num + 1}분기 실적에 대한 상세한 분석을 제공합니다.
주요 성과 지표는 다음과 같습니다:

- KPI 1: 목표 대비 {120 + section * 5}% 달성
- KPI 2: 전년 동기 대비 {15 + section * 3}% 성장
- KPI 3: 시장 점유율 {25 + section * 2}% 확보

상세 분석:
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

""" * 2
            
            text_rect = fitz.Rect(40, 40, 555, 802)
            page.insert_textbox(text_rect, long_text, fontsize=9, fontname="helv")
        
        content = pdf.tobytes()
        pdf.close()
        return content


def run_e2e_tests():
    """Run comprehensive E2E tests"""
    print("PDF Processing E2E Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize services
    optimizer = PDFOptimizer()
    splitter = PDFSplitter()
    
    # Check if Claude API is available
    use_claude = False
    try:
        claude_service = ClaudeService()
        use_claude = not claude_service.test_mode
        print(f"Claude API: {'Available' if use_claude else 'Test Mode'}")
    except Exception as e:
        print(f"Claude API: Not available ({e})")
    
    print()
    
    # Define test cases
    test_cases = [
        TextHeavyPDFTest("text_heavy", "텍스트 위주 재무제표"),
        ImageHeavyPDFTest("image_heavy", "이미지/차트 포함 보고서"),
        ScannedPDFTest("scanned", "스캔된 문서"),
        VeryLargePDFTest("very_large", "대용량 문서 (분할 필요)")
    ]
    
    # Add real PDFs if available
    real_pdfs = glob.glob("data/financial_docs/**/*.pdf", recursive=True)[:2]
    for pdf_path in real_pdfs:
        test_case = PDFTestCase(
            f"real_{os.path.basename(pdf_path)}", 
            f"실제 PDF: {os.path.basename(pdf_path)}",
            pdf_path
        )
        test_cases.append(test_case)
    
    # Run tests
    all_results = []
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {idx}/{len(test_cases)}: {test_case.description}")
        print("-" * 60)
        
        result = {
            "test_case": test_case.name,
            "description": test_case.description,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Get PDF content
            if test_case.pdf_path and os.path.exists(test_case.pdf_path):
                with open(test_case.pdf_path, "rb") as f:
                    pdf_content = f.read()
            else:
                pdf_content = test_case.create_test_pdf()
            
            original_size_mb = len(pdf_content) / (1024 * 1024)
            result["original_size_mb"] = round(original_size_mb, 2)
            print(f"Original size: {original_size_mb:.2f} MB")
            
            # Step 1: Optimization
            print("\nStep 1: Optimization...")
            start_time = time.time()
            
            opt_content, opt_metadata = optimizer.optimize_pdf(
                pdf_content,
                compression_level=CompressionLevel.EBOOK
            )
            
            opt_time = time.time() - start_time
            opt_size_mb = len(opt_content) / (1024 * 1024)
            
            result["optimization"] = {
                "size_mb": round(opt_size_mb, 2),
                "compression_ratio": opt_metadata.get("compression_ratio", 1.0),
                "time_seconds": round(opt_time, 2),
                "methods": opt_metadata.get("compression_methods", [])
            }
            
            print(f"Optimized size: {opt_size_mb:.2f} MB ({opt_metadata.get('compression_ratio', 1.0):.1%} of original)")
            print(f"Time: {opt_time:.2f}s")
            
            # Step 2: Splitting check
            print("\nStep 2: Split check...")
            split_files, split_metadata = splitter.check_and_split(
                opt_content,
                f"test_{test_case.name}.pdf"
            )
            
            result["splitting"] = {
                "needed": split_metadata["needs_splitting"],
                "performed": split_metadata["split_performed"],
                "file_count": len(split_files)
            }
            
            if split_metadata["split_performed"]:
                print(f"Split into {len(split_files)} files")
                for i, file_info in enumerate(split_files[:3], 1):  # Show first 3
                    print(f"  Part {i}: {file_info['size_mb']} MB, {file_info['pages']} pages")
            else:
                print("No splitting needed")
            
            # Step 3: Claude API test (if available)
            if use_claude and isinstance(test_case, TextHeavyPDFTest):
                print("\nStep 3: Claude API test...")
                
                # Use first file (whether split or not)
                test_content = split_files[0]["content"]
                
                try:
                    # Create a minimal test
                    import asyncio
                    response = asyncio.run(claude_service.analyze_pdf_with_question(
                        pdf_content=test_content,
                        question="이 문서의 종류와 주요 내용을 간단히 설명해주세요.",
                        company_name="테스트회사",
                        doc_type="테스트문서",
                        doc_year=2024
                    ))
                    
                    result["claude_test"] = {
                        "success": True,
                        "model_used": response.get("model_used"),
                        "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                        "response_preview": response.get("answer", "")[:100] + "..."
                    }
                    
                    print(f"Claude API: Success")
                    print(f"Model: {response.get('model_used')}")
                    print(f"Tokens: {response.get('usage', {}).get('total_tokens', 0)}")
                    
                except Exception as e:
                    result["claude_test"] = {
                        "success": False,
                        "error": str(e)
                    }
                    print(f"Claude API: Failed - {e}")
            
            result["success"] = True
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"ERROR: {e}")
        
        all_results.append(result)
    
    # Generate report
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in all_results if r.get("success"))
    print(f"Total tests: {len(all_results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(all_results) - success_count}")
    
    print("\nCompression Performance:")
    compression_ratios = [r["optimization"]["compression_ratio"] 
                         for r in all_results 
                         if r.get("success") and "optimization" in r]
    if compression_ratios:
        print(f"Average compression: {sum(compression_ratios)/len(compression_ratios):.1%}")
        print(f"Best compression: {min(compression_ratios):.1%}")
        print(f"Worst compression: {max(compression_ratios):.1%}")
    
    print("\nSplitting Summary:")
    split_count = sum(1 for r in all_results 
                     if r.get("splitting", {}).get("performed"))
    print(f"Files requiring split: {split_count}/{len(all_results)}")
    
    # Save detailed results
    report_filename = f"pdf_e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "test_count": len(all_results),
            "success_count": success_count,
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {report_filename}")
    
    return all_results


def test_failure_cases():
    """Test edge cases and failure scenarios"""
    print("\nTesting Failure Cases")
    print("=" * 60)
    
    optimizer = PDFOptimizer()
    splitter = PDFSplitter()
    
    # Test 1: Empty PDF
    print("\nTest 1: Empty PDF")
    try:
        empty_pdf = fitz.open()
        empty_content = empty_pdf.tobytes()
        empty_pdf.close()
        
        opt_content, _ = optimizer.optimize_pdf(empty_content)
        print("✓ Empty PDF handled gracefully")
    except Exception as e:
        print(f"✗ Empty PDF failed: {e}")
    
    # Test 2: Corrupted PDF
    print("\nTest 2: Corrupted PDF")
    try:
        corrupted_content = b"This is not a valid PDF content"
        opt_content, metadata = optimizer.optimize_pdf(corrupted_content)
        if "error" in metadata:
            print("✓ Corrupted PDF handled gracefully")
        else:
            print("✗ Corrupted PDF not detected")
    except Exception as e:
        print(f"✓ Corrupted PDF raised exception as expected: {e}")
    
    # Test 3: Extreme page count
    print("\nTest 3: PDF with 1 page for splitting")
    try:
        pdf = fitz.open()
        page = pdf.new_page()
        page.insert_text((50, 50), "Single page")
        content = pdf.tobytes()
        pdf.close()
        
        # Force splitting
        splitter.claude_api_max_size = 100  # 100 bytes
        split_files, metadata = splitter.check_and_split(content, "single.pdf")
        print(f"✓ Single page PDF handled: {len(split_files)} files")
    except Exception as e:
        print(f"✗ Single page PDF failed: {e}")


if __name__ == "__main__":
    # Run main E2E tests
    results = run_e2e_tests()
    
    # Run failure case tests
    test_failure_cases()
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)