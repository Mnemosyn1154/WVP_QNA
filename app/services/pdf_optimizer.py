"""
Advanced PDF Optimization Module
Handles PDF file size optimization using PyMuPDF and Ghostscript
"""

import io
import os
import subprocess
import logging
from typing import Optional, Tuple, Dict, Any
from enum import Enum
from pathlib import Path
import tempfile
import fitz  # PyMuPDF
from PIL import Image

logger = logging.getLogger(__name__)


class CompressionLevel(Enum):
    """PDF compression quality levels matching Ghostscript settings"""
    ULTRA_LOW = "/ultra_low"  # Ultra low quality for image-based PDFs (36 dpi)
    SCREEN = "/screen"  # Low quality, smallest size (72 dpi)
    EBOOK = "/ebook"    # Medium quality (150 dpi)
    PRINTER = "/printer"  # High quality (300 dpi)
    PREPRESS = "/prepress"  # Highest quality (300 dpi, color preserving)


class PDFOptimizer:
    """Advanced PDF optimization service with multiple compression strategies"""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit for Claude API
        self.image_quality_levels = {
            "high": {"dpi": 200, "jpeg_quality": 90},
            "medium": {"dpi": 150, "jpeg_quality": 85},
            "low": {"dpi": 100, "jpeg_quality": 75},
            "minimal": {"dpi": 72, "jpeg_quality": 60},
            "ultra_low": {"dpi": 36, "jpeg_quality": 40}
        }
        
    def optimize_pdf(
        self, 
        pdf_content: bytes, 
        target_size_mb: Optional[float] = None,
        compression_level: CompressionLevel = CompressionLevel.EBOOK,
        use_ghostscript: bool = True,
        force_scanned_optimization: bool = False
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Optimize PDF with multiple compression strategies
        
        Args:
            pdf_content: Original PDF content
            target_size_mb: Target file size in MB (optional)
            compression_level: Ghostscript compression level
            use_ghostscript: Whether to use Ghostscript for additional compression
            force_scanned_optimization: Force optimization for scanned documents
            
        Returns:
            Optimized PDF content and detailed metadata
        """
        original_size = len(pdf_content)
        target_size = (target_size_mb * 1024 * 1024) if target_size_mb else self.max_file_size
        
        metadata = {
            "original_size": original_size,
            "original_size_mb": round(original_size / (1024 * 1024), 2),
            "compression_methods": []
        }
        
        try:
            # Check if PDF is scanned and apply specialized optimization
            if force_scanned_optimization or self.is_image_based_pdf(pdf_content):
                logger.info("Detected scanned PDF, applying specialized optimization")
                optimized_content, scan_metadata = self._optimize_scanned_pdf(pdf_content)
                metadata["compression_methods"].append("ScannedPDF")
                metadata.update(scan_metadata)
                metadata["is_scanned"] = True
                
                metadata["final_size"] = len(optimized_content)
                metadata["final_size_mb"] = round(len(optimized_content) / (1024 * 1024), 2)
                metadata["compression_ratio"] = round(len(optimized_content) / original_size, 3)
                return optimized_content, metadata
            
            # Step 1: PyMuPDF optimization for regular PDFs
            optimized_content, pymupdf_metadata = self._optimize_with_pymupdf(pdf_content)
            metadata["compression_methods"].append("PyMuPDF")
            metadata.update(pymupdf_metadata)
            
            # Check if we've reached target size
            if len(optimized_content) <= target_size:
                metadata["final_size"] = len(optimized_content)
                metadata["final_size_mb"] = round(len(optimized_content) / (1024 * 1024), 2)
                metadata["compression_ratio"] = round(len(optimized_content) / original_size, 3)
                return optimized_content, metadata
            
            # Step 2: Ghostscript optimization if available and enabled
            if use_ghostscript and self._check_ghostscript():
                gs_content, gs_metadata = self._optimize_with_ghostscript(
                    optimized_content, 
                    compression_level
                )
                if gs_content and len(gs_content) < len(optimized_content):
                    optimized_content = gs_content
                    metadata["compression_methods"].append("Ghostscript")
                    metadata.update(gs_metadata)
            
            # Step 3: Aggressive optimization if still too large
            if len(optimized_content) > target_size:
                aggressive_content, aggressive_metadata = self._aggressive_optimization(
                    pdf_content, 
                    target_size
                )
                if len(aggressive_content) < len(optimized_content):
                    optimized_content = aggressive_content
                    metadata["compression_methods"].append("Aggressive")
                    metadata.update(aggressive_metadata)
            
            metadata["final_size"] = len(optimized_content)
            metadata["final_size_mb"] = round(len(optimized_content) / (1024 * 1024), 2)
            metadata["compression_ratio"] = round(len(optimized_content) / original_size, 3)
            
            return optimized_content, metadata
            
        except Exception as e:
            logger.error(f"Error in PDF optimization: {e}")
            metadata["error"] = str(e)
            return pdf_content, metadata
    
    def _optimize_scanned_pdf(self, pdf_content: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Optimize scanned PDF documents with specialized settings"""
        metadata = {"optimization_type": "scanned_pdf"}
        
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            num_pages = len(pdf_document)
            metadata["total_pages"] = num_pages
            
            # Create optimized document
            optimized_pdf = fitz.open()
            
            # Target settings for scanned documents
            target_dpi = 150
            jpeg_quality = 85
            
            images_processed = 0
            
            for page_num in range(num_pages):
                page = pdf_document[page_num]
                
                # Get page dimensions
                page_rect = page.rect
                page_width = page_rect.width
                page_height = page_rect.height
                
                # Convert page to pixmap at target DPI
                mat = fitz.Matrix(target_dpi / 72.0, target_dpi / 72.0)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to grayscale
                pix_gray = fitz.Pixmap(fitz.csGRAY, pix)
                pix = None  # Free original pixmap
                
                # Convert to PIL Image for JPEG compression
                img_data = pix_gray.tobytes("png")
                img_pil = Image.open(io.BytesIO(img_data))
                
                # Save as JPEG with specified quality
                img_buffer = io.BytesIO()
                img_pil.save(img_buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                img_buffer.seek(0)
                
                # Create new page with original dimensions
                new_page = optimized_pdf.new_page(width=page_width, height=page_height)
                
                # Insert the compressed image
                img_rect = fitz.Rect(0, 0, page_width, page_height)
                new_page.insert_image(img_rect, stream=img_buffer.getvalue())
                
                images_processed += 1
                pix_gray = None  # Free grayscale pixmap
                
                logger.debug(f"Processed page {page_num + 1}/{num_pages} - DPI: {target_dpi}, Quality: {jpeg_quality}%")
            
            # Save optimized PDF
            optimized_content = optimized_pdf.tobytes(
                garbage=4,
                deflate=True,
                deflate_images=True,
                clean=True
            )
            
            metadata.update({
                "images_processed": images_processed,
                "target_dpi": target_dpi,
                "jpeg_quality": jpeg_quality,
                "color_mode": "grayscale",
                "optimization_method": "scanned_pdf_pipeline",
                "original_size": len(pdf_content),
                "optimized_size": len(optimized_content),
                "compression_ratio": round(len(optimized_content) / len(pdf_content), 3)
            })
            
            pdf_document.close()
            optimized_pdf.close()
            
            logger.info(f"Scanned PDF optimization complete: {len(pdf_content)} -> {len(optimized_content)} bytes "
                       f"({metadata['compression_ratio']:.1%} of original)")
            
            return optimized_content, metadata
            
        except Exception as e:
            logger.error(f"Scanned PDF optimization error: {e}")
            metadata["error"] = str(e)
            return pdf_content, metadata
    
    def _optimize_with_pymupdf(self, pdf_content: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Optimize PDF using PyMuPDF library"""
        metadata = {}
        
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            num_pages = len(pdf_document)
            metadata["total_pages"] = num_pages
            
            # Create optimized document
            optimized_pdf = fitz.open()
            
            # Process each page
            images_compressed = 0
            for page_num in range(num_pages):
                page = pdf_document[page_num]
                
                # Get images on the page
                image_list = page.get_images()
                
                if image_list:
                    # Page has images - optimize them
                    for img_index, img in enumerate(image_list):
                        try:
                            # Extract image
                            xref = img[0]
                            pix = fitz.Pixmap(pdf_document, xref)
                            
                            # Convert to PIL Image for optimization
                            if pix.colorspace:
                                img_data = pix.tobytes("png")
                                img_pil = Image.open(io.BytesIO(img_data))
                                
                                # Resize if too large
                                max_dimension = 1200
                                if img_pil.width > max_dimension or img_pil.height > max_dimension:
                                    img_pil.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                                
                                # Save as JPEG with compression
                                img_buffer = io.BytesIO()
                                img_pil.save(img_buffer, format="JPEG", quality=85, optimize=True)
                                img_buffer.seek(0)
                                
                                # Replace image in page
                                page._replace_image(xref, stream=img_buffer.getvalue())
                                images_compressed += 1
                            
                            pix = None  # Free resources
                        except Exception as e:
                            logger.debug(f"Could not optimize image {img_index} on page {page_num}: {e}")
                
                # Add page to optimized document
                optimized_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            
            # Remove metadata to save space
            optimized_pdf.metadata = {}
            
            # Save with maximum compression
            optimized_content = optimized_pdf.tobytes(
                garbage=4,  # Maximum garbage collection
                deflate=True,  # Compress streams
                deflate_images=True,  # Compress images
                deflate_fonts=True,  # Compress fonts
                clean=True  # Clean up redundant objects
            )
            
            metadata["images_compressed"] = images_compressed
            metadata["pymupdf_size"] = len(optimized_content)
            
            pdf_document.close()
            optimized_pdf.close()
            
            return optimized_content, metadata
            
        except Exception as e:
            logger.error(f"PyMuPDF optimization error: {e}")
            metadata["pymupdf_error"] = str(e)
            return pdf_content, metadata
    
    def is_image_based_pdf(self, pdf_content: bytes) -> bool:
        """Check if PDF is primarily image-based (scanned document)"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            total_text_chars = 0
            total_images = 0
            
            for page in pdf_document:
                # Count text characters
                text = page.get_text()
                total_text_chars += len(text.strip())
                
                # Count images
                image_list = page.get_images()
                total_images += len(image_list)
            
            pdf_document.close()
            
            # If very little text and has images, it's likely scanned
            is_scanned = total_text_chars < 100 and total_images > 0
            
            logger.info(f"PDF analysis - Text chars: {total_text_chars}, Images: {total_images}, Is scanned: {is_scanned}")
            
            return is_scanned
            
        except Exception as e:
            logger.error(f"Error checking if PDF is image-based: {e}")
            return False
    
    def _check_ghostscript(self) -> bool:
        """Check if Ghostscript is available"""
        try:
            result = subprocess.run(
                ["gs", "--version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("Ghostscript not found. Install it for better compression.")
            return False
    
    def _optimize_with_ghostscript(
        self, 
        pdf_content: bytes, 
        compression_level: CompressionLevel
    ) -> Tuple[Optional[bytes], Dict[str, Any]]:
        """Optimize PDF using Ghostscript"""
        metadata = {}
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as input_file:
                input_file.write(pdf_content)
                input_file.flush()
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
                output_path = output_file.name
            
            # Base Ghostscript command
            gs_command = [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                "-dDetectDuplicateImages",
                "-dCompressFonts=true",
                "-dSubsetFonts=true",
            ]
            
            # Apply ultra-low compression for image-based PDFs
            if compression_level == CompressionLevel.ULTRA_LOW:
                gs_command.extend([
                    "-dPDFSETTINGS=/screen",
                    "-dDownsampleColorImages=true",
                    "-dDownsampleGrayImages=true",
                    "-dDownsampleMonoImages=true",
                    "-dColorImageResolution=36",
                    "-dGrayImageResolution=36",
                    "-dMonoImageResolution=36",
                    "-dColorImageDownsampleType=/Bicubic",
                    "-dGrayImageDownsampleType=/Bicubic",
                    "-dMonoImageDownsampleType=/Subsample",
                    "-dJPEGQ=40",
                    "-sProcessColorModel=DeviceGray",
                    "-sColorConversionStrategy=Gray",
                    "-dOverrideICC"
                ])
            else:
                gs_command.extend([
                    f"-dPDFSETTINGS={compression_level.value}",
                    "-dColorImageDownsampleType=/Bicubic",
                    "-dGrayImageDownsampleType=/Bicubic",
                    "-dMonoImageDownsampleType=/Bicubic",
                ])
            
            gs_command.extend([
                f"-sOutputFile={output_path}",
                input_path
            ])
            
            # Run Ghostscript
            result = subprocess.run(
                gs_command, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                with open(output_path, "rb") as f:
                    optimized_content = f.read()
                
                metadata["ghostscript_size"] = len(optimized_content)
                metadata["ghostscript_level"] = compression_level.name
                
                # Clean up temp files
                os.unlink(input_path)
                os.unlink(output_path)
                
                return optimized_content, metadata
            else:
                logger.error(f"Ghostscript error: {result.stderr}")
                metadata["ghostscript_error"] = result.stderr
                
        except Exception as e:
            logger.error(f"Ghostscript optimization error: {e}")
            metadata["ghostscript_error"] = str(e)
        
        finally:
            # Clean up temp files if they exist
            for path in [input_path, output_path]:
                if 'path' in locals() and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass
        
        return None, metadata
    
    def _aggressive_optimization(
        self, 
        pdf_content: bytes, 
        target_size: int
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Apply aggressive optimization techniques"""
        metadata = {"aggressive_mode": True}
        
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            # For image-based PDFs, keep all pages but compress images heavily
            if self.is_image_based_pdf(pdf_content):
                # Don't reduce pages for scanned documents
                optimized_pdf = fitz.open()
                
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    
                    # Get all images on the page
                    image_list = page.get_images()
                    
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            pix = fitz.Pixmap(pdf_document, xref)
                            
                            # Convert to PIL Image for aggressive compression
                            img_data = pix.tobytes("png")
                            img_pil = Image.open(io.BytesIO(img_data))
                            
                            # Resize to very low resolution
                            new_width = pix.width // 4  # Reduce to 25% of original
                            new_height = pix.height // 4
                            img_pil = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            
                            # Convert to grayscale
                            img_pil = img_pil.convert('L')
                            
                            # Save with low JPEG quality
                            img_buffer = io.BytesIO()
                            img_pil.save(img_buffer, format="JPEG", quality=30, optimize=True)
                            img_buffer.seek(0)
                            
                            # Replace image in page
                            page._replace_image(xref, stream=img_buffer.getvalue())
                            
                            pix = None
                        except Exception as e:
                            logger.debug(f"Could not compress image: {e}")
                    
                    # Add compressed page
                    optimized_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
                
                optimized_content = optimized_pdf.tobytes(
                    garbage=4,
                    deflate=True,
                    deflate_images=True,
                    deflate_fonts=True,
                    clean=True
                )
                
                optimized_pdf.close()
                pdf_document.close()
                
                metadata["image_based_compression"] = True
                metadata["pages_kept"] = len(pdf_document)
                
                return optimized_content, metadata
            
            # For text-based PDFs, use original logic
            current_size = len(pdf_content)
            size_ratio = target_size / current_size
            pages_to_keep = max(1, int(len(pdf_document) * size_ratio * 0.8))
            
            text_pdf = fitz.open()
            
            for page_num in range(min(pages_to_keep, len(pdf_document))):
                page = pdf_document[page_num]
                text = page.get_text()
                
                # Extract tables
                tables = page.find_tables()
                if tables:
                    text += "\n\n[표 데이터]\n"
                    for table in tables:
                        for row in table.extract():
                            text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                
                # Create text-only page
                new_page = text_pdf.new_page(width=595, height=842)  # A4
                text_rect = fitz.Rect(40, 40, 555, 802)
                
                # Insert text with smaller font
                new_page.insert_textbox(
                    text_rect,
                    text,
                    fontsize=9,
                    fontname="helv",
                    align=fitz.TEXT_ALIGN_LEFT
                )
            
            optimized_content = text_pdf.tobytes(
                garbage=4,
                deflate=True,
                clean=True
            )
            
            metadata["pages_kept"] = pages_to_keep
            metadata["text_only"] = True
            
            pdf_document.close()
            text_pdf.close()
            
            return optimized_content, metadata
            
        except Exception as e:
            logger.error(f"Aggressive optimization error: {e}")
            metadata["aggressive_error"] = str(e)
            return pdf_content, metadata
    
    def get_optimization_report(
        self, 
        original_size: int, 
        optimized_size: int, 
        metadata: Dict[str, Any]
    ) -> str:
        """Generate a detailed optimization report"""
        report = f"""
PDF 최적화 결과 리포트
====================

원본 파일 크기: {original_size:,} bytes ({round(original_size / (1024 * 1024), 2)} MB)
최적화된 크기: {optimized_size:,} bytes ({round(optimized_size / (1024 * 1024), 2)} MB)
압축률: {round((1 - optimized_size / original_size) * 100, 1)}%
압축 방법: {', '.join(metadata.get('compression_methods', []))}

세부 정보:
"""
        
        if "total_pages" in metadata:
            report += f"- 총 페이지 수: {metadata['total_pages']}\n"
        
        if "images_compressed" in metadata:
            report += f"- 압축된 이미지 수: {metadata['images_compressed']}\n"
        
        if "ghostscript_level" in metadata:
            report += f"- Ghostscript 압축 레벨: {metadata['ghostscript_level']}\n"
        
        if "aggressive_mode" in metadata:
            report += f"- 공격적 압축 모드 사용: 예\n"
            if "pages_kept" in metadata:
                report += f"- 유지된 페이지 수: {metadata['pages_kept']}\n"
        
        if "error" in metadata:
            report += f"\n⚠️ 오류 발생: {metadata['error']}\n"
        
        return report