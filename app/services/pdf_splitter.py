"""
PDF Splitting Service
Handles automatic PDF splitting for Claude API size limits
"""

import os
import io
import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import fitz  # PyMuPDF

from app.core.config import settings

logger = logging.getLogger(__name__)


class PDFSplitter:
    """Service for splitting large PDFs into smaller chunks"""
    
    def __init__(self):
        # Claude API file size limit (configurable)
        self.claude_api_max_size_mb = getattr(settings, 'CLAUDE_API_MAX_FILE_SIZE_MB', 10)
        self.claude_api_max_size = self.claude_api_max_size_mb * 1024 * 1024
        self.default_pages_per_chunk = 20
        
    def check_and_split(
        self, 
        pdf_content: bytes, 
        filename: str = "document.pdf",
        pages_per_chunk: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Check PDF size and split if necessary
        
        Args:
            pdf_content: PDF file content
            filename: Original filename
            pages_per_chunk: Number of pages per split file
            
        Returns:
            List of split file info and metadata
        """
        file_size = len(pdf_content)
        file_size_mb = file_size / (1024 * 1024)
        
        metadata = {
            "original_filename": filename,
            "original_size": file_size,
            "original_size_mb": round(file_size_mb, 2),
            "max_allowed_size_mb": self.claude_api_max_size_mb,
            "needs_splitting": file_size > self.claude_api_max_size,
            "split_performed": False
        }
        
        # If file is within limit, return as is
        if file_size <= self.claude_api_max_size:
            logger.info(f"PDF {filename} is within size limit ({file_size_mb:.2f} MB)")
            return [{
                "content": pdf_content,
                "filename": filename,
                "size": file_size,
                "size_mb": round(file_size_mb, 2),
                "pages": self._get_page_count(pdf_content),
                "part_number": None
            }], metadata
        
        # File needs splitting
        logger.warning(f"PDF {filename} exceeds limit ({file_size_mb:.2f} MB > {self.claude_api_max_size_mb} MB)")
        
        # Perform splitting
        split_files = self._split_pdf(
            pdf_content, 
            filename, 
            pages_per_chunk or self.default_pages_per_chunk
        )
        
        metadata["split_performed"] = True
        metadata["split_count"] = len(split_files)
        metadata["pages_per_chunk"] = pages_per_chunk or self.default_pages_per_chunk
        
        return split_files, metadata
    
    def _get_page_count(self, pdf_content: bytes) -> int:
        """Get total page count from PDF"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            page_count = len(pdf_document)
            pdf_document.close()
            return page_count
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0
    
    def _split_pdf(
        self, 
        pdf_content: bytes, 
        filename: str, 
        pages_per_chunk: int
    ) -> List[Dict[str, Any]]:
        """Split PDF into smaller chunks"""
        split_files = []
        
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            total_pages = len(pdf_document)
            
            # Calculate number of chunks needed
            num_chunks = (total_pages + pages_per_chunk - 1) // pages_per_chunk
            
            logger.info(f"Splitting {filename} into {num_chunks} chunks ({pages_per_chunk} pages each)")
            
            # Create base filename without extension
            base_name = Path(filename).stem
            extension = Path(filename).suffix or ".pdf"
            
            for chunk_idx in range(num_chunks):
                start_page = chunk_idx * pages_per_chunk
                end_page = min((chunk_idx + 1) * pages_per_chunk, total_pages)
                
                # Create new PDF for this chunk
                chunk_pdf = fitz.open()
                
                # Copy pages to chunk
                chunk_pdf.insert_pdf(
                    pdf_document,
                    from_page=start_page,
                    to_page=end_page - 1  # to_page is inclusive
                )
                
                # Get chunk content
                chunk_content = chunk_pdf.tobytes(
                    garbage=4,
                    deflate=True,
                    clean=True
                )
                
                chunk_size = len(chunk_content)
                chunk_size_mb = chunk_size / (1024 * 1024)
                
                # Generate chunk filename
                chunk_filename = f"{base_name}_part_{chunk_idx + 1}_of_{num_chunks}{extension}"
                
                split_file_info = {
                    "content": chunk_content,
                    "filename": chunk_filename,
                    "size": chunk_size,
                    "size_mb": round(chunk_size_mb, 2),
                    "pages": end_page - start_page,
                    "page_range": f"{start_page + 1}-{end_page}",
                    "part_number": chunk_idx + 1,
                    "total_parts": num_chunks
                }
                
                split_files.append(split_file_info)
                
                logger.info(f"Created chunk {chunk_idx + 1}: {chunk_filename} "
                          f"({chunk_size_mb:.2f} MB, pages {start_page + 1}-{end_page})")
                
                # Check if chunk is still too large
                if chunk_size > self.claude_api_max_size:
                    logger.warning(f"Chunk {chunk_idx + 1} is still too large ({chunk_size_mb:.2f} MB). "
                                 f"Consider using fewer pages per chunk.")
                
                chunk_pdf.close()
            
            pdf_document.close()
            
            return split_files
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {e}")
            # Return original file as fallback
            return [{
                "content": pdf_content,
                "filename": filename,
                "size": len(pdf_content),
                "size_mb": round(len(pdf_content) / (1024 * 1024), 2),
                "pages": self._get_page_count(pdf_content),
                "part_number": None,
                "error": str(e)
            }]
    
    def calculate_optimal_chunk_size(
        self, 
        pdf_content: bytes, 
        target_chunk_size_mb: float = 8.0
    ) -> int:
        """
        Calculate optimal pages per chunk based on file size
        
        Args:
            pdf_content: PDF content
            target_chunk_size_mb: Target size for each chunk in MB
            
        Returns:
            Optimal number of pages per chunk
        """
        try:
            total_pages = self._get_page_count(pdf_content)
            if total_pages == 0:
                return self.default_pages_per_chunk
            
            file_size_mb = len(pdf_content) / (1024 * 1024)
            avg_page_size_mb = file_size_mb / total_pages
            
            # Calculate pages that would fit in target size
            optimal_pages = int(target_chunk_size_mb / avg_page_size_mb)
            
            # Ensure at least 1 page per chunk
            optimal_pages = max(1, optimal_pages)
            
            # Cap at reasonable maximum
            optimal_pages = min(optimal_pages, 100)
            
            logger.info(f"Calculated optimal chunk size: {optimal_pages} pages per chunk")
            
            return optimal_pages
            
        except Exception as e:
            logger.error(f"Error calculating optimal chunk size: {e}")
            return self.default_pages_per_chunk
    
    def get_split_report(
        self, 
        split_files: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> str:
        """Generate a detailed split report"""
        report = f"""
PDF 분할 처리 결과
================

원본 파일: {metadata['original_filename']}
원본 크기: {metadata['original_size_mb']} MB
허용 한도: {metadata['max_allowed_size_mb']} MB
분할 필요: {'예' if metadata['needs_splitting'] else '아니오'}
"""
        
        if metadata.get('split_performed'):
            report += f"""
분할 수행: 예
총 {metadata['split_count']}개 파일로 분할됨
페이지/청크: {metadata.get('pages_per_chunk', 'N/A')}

분할된 파일 목록:
"""
            for idx, file_info in enumerate(split_files, 1):
                report += f"""
  파일 {idx}: {file_info['filename']}
  - 크기: {file_info['size_mb']} MB
  - 페이지: {file_info['pages']} ({file_info.get('page_range', 'N/A')})
"""
                if file_info['size_mb'] > self.claude_api_max_size_mb:
                    report += f"  - ⚠️ 경고: 여전히 크기 한도 초과\n"
        else:
            report += "\n분할 수행: 아니오 (크기 한도 내)\n"
        
        return report