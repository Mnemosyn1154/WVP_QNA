"""
PDF Processing Service
Handles PDF optimization and text extraction
"""

import io
import logging
from typing import Optional, Tuple, List, Dict
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for processing and optimizing PDF files"""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit for Claude
        self.target_dpi = 150  # Reduced DPI for images
        self.jpeg_quality = 85  # JPEG compression quality
    
    def optimize_pdf(self, pdf_content: bytes, max_pages: Optional[int] = None) -> Tuple[bytes, Dict[str, any]]:
        """
        Optimize PDF for Claude API submission
        
        Args:
            pdf_content: Original PDF content
            max_pages: Maximum number of pages to include
            
        Returns:
            Optimized PDF content and metadata
        """
        try:
            # Open PDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            # Get basic info
            num_pages = len(pdf_document)
            original_size = len(pdf_content)
            
            # Determine pages to process
            pages_to_process = min(num_pages, max_pages) if max_pages else num_pages
            
            # Create new optimized PDF
            optimized_pdf = fitz.open()
            
            for page_num in range(pages_to_process):
                page = pdf_document[page_num]
                
                # Get page dimensions
                rect = page.rect
                
                # Extract text
                text = page.get_text()
                
                # If page is mostly text, recreate it
                if len(text.strip()) > 100:  # Arbitrary threshold
                    # Create new page with text only
                    new_page = optimized_pdf.new_page(width=rect.width, height=rect.height)
                    
                    # Re-insert text (simplified - for production, preserve formatting)
                    text_rect = fitz.Rect(50, 50, rect.width - 50, rect.height - 50)
                    new_page.insert_textbox(
                        text_rect,
                        text,
                        fontsize=10,
                        fontname="helv",
                        align=fitz.TEXT_ALIGN_LEFT
                    )
                else:
                    # For image-heavy pages, reduce quality
                    pix = page.get_pixmap(dpi=self.target_dpi)
                    img_data = pix.tobytes("jpeg", jpg_quality=self.jpeg_quality)
                    
                    # Insert compressed image as new page
                    img_rect = fitz.Rect(0, 0, rect.width, rect.height)
                    new_page = optimized_pdf.new_page(width=rect.width, height=rect.height)
                    new_page.insert_image(img_rect, stream=img_data)
            
            # Save optimized PDF
            optimized_content = optimized_pdf.tobytes(
                garbage=4,  # Maximum garbage collection
                deflate=True,  # Compress streams
                clean=True  # Clean up redundant objects
            )
            
            # Close documents
            pdf_document.close()
            optimized_pdf.close()
            
            # Check if further optimization needed
            if len(optimized_content) > self.max_file_size:
                # Try text extraction as last resort
                optimized_content = self._extract_text_as_pdf(pdf_content, pages_to_process)
            
            metadata = {
                "original_pages": num_pages,
                "processed_pages": pages_to_process,
                "original_size": original_size,
                "optimized_size": len(optimized_content),
                "compression_ratio": round(len(optimized_content) / original_size, 2)
            }
            
            return optimized_content, metadata
            
        except Exception as e:
            logger.error(f"Error optimizing PDF: {e}")
            # Return original if optimization fails
            return pdf_content, {"error": str(e), "original_size": len(pdf_content)}
    
    def _extract_text_as_pdf(self, pdf_content: bytes, max_pages: int) -> bytes:
        """Extract text and create a text-only PDF"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            text_pdf = fitz.open()
            
            for page_num in range(min(len(pdf_document), max_pages)):
                page = pdf_document[page_num]
                text = page.get_text()
                
                # Handle tables specially
                tables = page.find_tables()
                if tables:
                    text += "\n\n[표 데이터]\n"
                    for table in tables:
                        for row in table.extract():
                            text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                
                # Create text-only page
                new_page = text_pdf.new_page(width=595, height=842)  # A4 size
                text_rect = fitz.Rect(50, 50, 545, 792)
                new_page.insert_textbox(
                    text_rect,
                    text,
                    fontsize=10,
                    fontname="helv",
                    align=fitz.TEXT_ALIGN_LEFT
                )
            
            content = text_pdf.tobytes()
            pdf_document.close()
            text_pdf.close()
            
            return content
            
        except Exception as e:
            logger.error(f"Error creating text PDF: {e}")
            # Create a simple text PDF with error message
            error_pdf = fitz.open()
            page = error_pdf.new_page()
            page.insert_text((50, 50), f"텍스트 추출 오류: {str(e)}")
            content = error_pdf.tobytes()
            error_pdf.close()
            return content
    
    def extract_relevant_pages(self, pdf_content: bytes, keywords: List[str]) -> Tuple[bytes, List[int]]:
        """
        Extract only pages containing specific keywords
        
        Args:
            pdf_content: Original PDF content
            keywords: List of keywords to search for
            
        Returns:
            PDF with relevant pages and list of page numbers
        """
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            relevant_pages = []
            
            # Search for keywords in each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text = page.get_text().lower()
                
                # Check if any keyword is present
                for keyword in keywords:
                    if keyword.lower() in text:
                        relevant_pages.append(page_num)
                        break
            
            # Always include first few pages (usually contain summary)
            for i in range(min(3, len(pdf_document))):
                if i not in relevant_pages:
                    relevant_pages.insert(i, i)
            
            # Sort pages
            relevant_pages.sort()
            
            # Create new PDF with relevant pages
            relevant_pdf = fitz.open()
            for page_num in relevant_pages:
                relevant_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            
            content = relevant_pdf.tobytes()
            
            pdf_document.close()
            relevant_pdf.close()
            
            return content, relevant_pages
            
        except Exception as e:
            logger.error(f"Error extracting relevant pages: {e}")
            return pdf_content, list(range(5))  # Return first 5 pages as fallback
    
    def extract_financial_tables(self, pdf_content: bytes) -> Dict[str, List[Dict]]:
        """Extract financial tables from PDF"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            all_tables = {}
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                tables = page.find_tables()
                
                if tables:
                    page_tables = []
                    for table in tables:
                        # Extract table data
                        data = table.extract()
                        # Convert to list of dicts with headers
                        if data and len(data) > 1:
                            headers = [str(h).strip() for h in data[0]]
                            rows = []
                            for row in data[1:]:
                                row_dict = {}
                                for i, cell in enumerate(row):
                                    if i < len(headers):
                                        row_dict[headers[i]] = str(cell).strip() if cell else ""
                                rows.append(row_dict)
                            page_tables.append({
                                "headers": headers,
                                "data": rows
                            })
                    
                    if page_tables:
                        all_tables[f"page_{page_num + 1}"] = page_tables
            
            pdf_document.close()
            return all_tables
            
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return {}
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract all text from PDF for text-based LLMs like Gemini
        
        Args:
            pdf_content: PDF file content
            
        Returns:
            Extracted text as string
        """
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            all_text = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    all_text.append(f"\n--- 페이지 {page_num + 1} ---\n")
                    all_text.append(text)
                
                # Extract tables
                tables = page.find_tables()
                if tables:
                    all_text.append("\n[표 데이터]\n")
                    for table in tables:
                        data = table.extract()
                        for row in data:
                            all_text.append(" | ".join(str(cell) if cell else "" for cell in row))
                        all_text.append("")  # Empty line after table
            
            pdf_document.close()
            
            # Join all text
            full_text = "\n".join(all_text)
            
            # If no text found, might be scanned PDF
            if len(full_text.strip()) < 100:
                logger.warning("PDF appears to be image-based, OCR might be needed")
                return "이 PDF는 스캔된 이미지 문서로 보입니다. 텍스트 추출이 제한적입니다."
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return f"PDF 텍스트 추출 오류: {str(e)}"