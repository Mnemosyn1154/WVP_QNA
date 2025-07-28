"""
PDF optimization API endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import logging

from app.services.pdf_optimizer import PDFOptimizer, CompressionLevel
from app.services.pdf_splitter import PDFSplitter

logger = logging.getLogger(__name__)
router = APIRouter()

pdf_optimizer = PDFOptimizer()
pdf_splitter = PDFSplitter()


@router.post("/optimize")
async def optimize_pdf(
    file: UploadFile = File(...),
    target_size_mb: Optional[float] = Query(None, description="Target file size in MB"),
    compression_level: Optional[str] = Query("ebook", description="Compression level: screen, ebook, printer, prepress"),
    use_ghostscript: Optional[bool] = Query(True, description="Use Ghostscript for additional compression")
):
    """
    Optimize PDF file size while maintaining quality
    
    - **file**: PDF file to optimize
    - **target_size_mb**: Target file size in MB (default: 10MB for Claude API)
    - **compression_level**: Ghostscript compression level
    - **use_ghostscript**: Whether to use Ghostscript (requires installation)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Map compression level string to enum
        compression_map = {
            "screen": CompressionLevel.SCREEN,
            "ebook": CompressionLevel.EBOOK,
            "printer": CompressionLevel.PRINTER,
            "prepress": CompressionLevel.PREPRESS
        }
        compression = compression_map.get(compression_level, CompressionLevel.EBOOK)
        
        # Optimize PDF
        optimized_content, metadata = pdf_optimizer.optimize_pdf(
            pdf_content=content,
            target_size_mb=target_size_mb,
            compression_level=compression,
            use_ghostscript=use_ghostscript
        )
        
        # Generate report
        report = pdf_optimizer.get_optimization_report(
            original_size=len(content),
            optimized_size=len(optimized_content),
            metadata=metadata
        )
        
        # Log optimization results
        logger.info(f"PDF optimization completed: {metadata}")
        
        # Return optimized PDF with metadata in headers
        return StreamingResponse(
            io.BytesIO(optimized_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=optimized_{file.filename}",
                "X-Original-Size": str(metadata.get("original_size", 0)),
                "X-Optimized-Size": str(metadata.get("final_size", 0)),
                "X-Compression-Ratio": str(metadata.get("compression_ratio", 1.0)),
                "X-Optimization-Report": report.replace("\n", " | ")
            }
        )
        
    except Exception as e:
        logger.error(f"Error in PDF optimization endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/info")
async def get_optimization_info(
    file: UploadFile = File(...)
):
    """
    Get optimization information without actually optimizing the file
    
    Returns estimated compression ratios and recommendations
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        # Analyze PDF
        import fitz
        pdf_document = fitz.open(stream=content, filetype="pdf")
        
        info = {
            "filename": file.filename,
            "original_size_mb": round(file_size_mb, 2),
            "total_pages": len(pdf_document),
            "has_images": False,
            "image_count": 0,
            "recommendations": []
        }
        
        # Check for images
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            images = page.get_images()
            if images:
                info["has_images"] = True
                info["image_count"] += len(images)
        
        pdf_document.close()
        
        # Provide recommendations
        if file_size_mb > 10:
            info["recommendations"].append("파일 크기가 10MB를 초과합니다. Claude API 전송을 위해 최적화가 필요합니다.")
        
        if info["has_images"]:
            info["recommendations"].append(f"{info['image_count']}개의 이미지가 포함되어 있습니다. 이미지 압축으로 크기를 줄일 수 있습니다.")
        
        if info["total_pages"] > 50:
            info["recommendations"].append(f"총 {info['total_pages']}페이지로 분량이 많습니다. 필요한 페이지만 추출하는 것을 고려하세요.")
        
        # Estimate compression ratios
        if info["has_images"]:
            info["estimated_compression"] = {
                "screen": "60-80% 크기 감소 (낮은 품질)",
                "ebook": "40-60% 크기 감소 (중간 품질)",
                "printer": "20-40% 크기 감소 (높은 품질)",
                "prepress": "10-20% 크기 감소 (최고 품질)"
            }
        else:
            info["estimated_compression"] = {
                "text_optimization": "10-30% 크기 감소 예상"
            }
        
        return info
        
    except Exception as e:
        logger.error(f"Error analyzing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/split")
async def split_pdf(
    file: UploadFile = File(...),
    pages_per_chunk: Optional[int] = Query(None, description="Number of pages per chunk (default: 20)")
):
    """
    Check and split PDF if it exceeds Claude API size limit
    
    - **file**: PDF file to check and potentially split
    - **pages_per_chunk**: Number of pages per split file
    
    Returns split file information and processing report
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Check and split if necessary
        split_files, metadata = pdf_splitter.check_and_split(
            pdf_content=content,
            filename=file.filename,
            pages_per_chunk=pages_per_chunk
        )
        
        # Generate report
        report = pdf_splitter.get_split_report(split_files, metadata)
        
        # Log results
        logger.info(f"PDF split check completed: {metadata}")
        
        # Prepare response
        response_data = {
            "original_filename": metadata["original_filename"],
            "original_size_mb": metadata["original_size_mb"],
            "needs_splitting": metadata["needs_splitting"],
            "split_performed": metadata["split_performed"],
            "split_count": metadata.get("split_count", 0),
            "report": report,
            "files": []
        }
        
        # Add file information (without actual content for API response)
        for file_info in split_files:
            response_data["files"].append({
                "filename": file_info["filename"],
                "size_mb": file_info["size_mb"],
                "pages": file_info["pages"],
                "page_range": file_info.get("page_range"),
                "part_number": file_info.get("part_number"),
                "total_parts": file_info.get("total_parts")
            })
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in PDF split endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_pdf_for_claude(
    file: UploadFile = File(...),
    optimize: bool = Query(True, description="Apply optimization before splitting"),
    target_size_mb: Optional[float] = Query(None, description="Target size for optimization"),
    compression_level: Optional[str] = Query("ebook", description="Compression level if optimizing")
):
    """
    Complete PDF processing pipeline for Claude API submission
    
    1. Optimize PDF to reduce size
    2. Check if splitting is needed
    3. Split if necessary
    
    Returns processed files ready for Claude API
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        content = await file.read()
        original_size_mb = len(content) / (1024 * 1024)
        
        processing_steps = []
        
        # Step 1: Optimize if requested
        if optimize:
            compression_map = {
                "screen": CompressionLevel.SCREEN,
                "ebook": CompressionLevel.EBOOK,
                "printer": CompressionLevel.PRINTER,
                "prepress": CompressionLevel.PREPRESS
            }
            compression = compression_map.get(compression_level, CompressionLevel.EBOOK)
            
            optimized_content, opt_metadata = pdf_optimizer.optimize_pdf(
                pdf_content=content,
                target_size_mb=target_size_mb,
                compression_level=compression,
                use_ghostscript=True
            )
            
            processing_steps.append({
                "step": "optimization",
                "original_size_mb": round(original_size_mb, 2),
                "optimized_size_mb": round(len(optimized_content) / (1024 * 1024), 2),
                "compression_ratio": opt_metadata.get("compression_ratio", 1.0)
            })
            
            content = optimized_content
        
        # Step 2: Check and split if necessary
        split_files, split_metadata = pdf_splitter.check_and_split(
            pdf_content=content,
            filename=file.filename
        )
        
        processing_steps.append({
            "step": "split_check",
            "needs_splitting": split_metadata["needs_splitting"],
            "split_performed": split_metadata["split_performed"],
            "split_count": split_metadata.get("split_count", 0)
        })
        
        # Calculate optimal pages if splitting was needed but chunk is still too large
        if split_metadata["split_performed"]:
            any_oversized = any(f["size_mb"] > pdf_splitter.claude_api_max_size_mb for f in split_files)
            if any_oversized:
                optimal_pages = pdf_splitter.calculate_optimal_chunk_size(content)
                processing_steps.append({
                    "step": "optimization_suggestion",
                    "message": f"일부 청크가 여전히 크기 제한을 초과합니다. {optimal_pages}페이지씩 분할하는 것을 권장합니다."
                })
        
        # Prepare response
        final_size_mb = sum(f["size_mb"] for f in split_files)
        
        return {
            "success": True,
            "original_filename": file.filename,
            "original_size_mb": round(original_size_mb, 2),
            "final_size_mb": round(final_size_mb, 2),
            "processing_steps": processing_steps,
            "ready_for_claude": all(f["size_mb"] <= pdf_splitter.claude_api_max_size_mb for f in split_files),
            "files": [{
                "filename": f["filename"],
                "size_mb": f["size_mb"],
                "pages": f["pages"],
                "page_range": f.get("page_range"),
                "ready": f["size_mb"] <= pdf_splitter.claude_api_max_size_mb
            } for f in split_files]
        }
        
    except Exception as e:
        logger.error(f"Error in PDF processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))