#!/usr/bin/env python3
"""
Test script for scanned PDF optimization pipeline
Tests the new resolution reduction feature for scanned documents
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_optimizer import PDFOptimizer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_scanned_pdf_optimization():
    """Test the scanned PDF optimization pipeline"""
    
    # Initialize services
    pdf_optimizer = PDFOptimizer()
    
    # Look for PDF files in data directory
    data_dir = Path("data")
    test_pdf = None
    
    # Find 설로인 PDF
    for pdf_file in data_dir.glob("*설로인*.pdf"):
        test_pdf = pdf_file
        break
    
    if not test_pdf:
        logger.error("Could not find 설로인 PDF file in data directory")
        return
    
    logger.info(f"Testing scanned PDF optimization with {test_pdf.name}")
    
    try:
        # Read the PDF
        with open(test_pdf, "rb") as f:
            pdf_data = f.read()
        
        original_size = len(pdf_data)
        logger.info(f"Original PDF size: {original_size:,} bytes ({original_size / (1024 * 1024):.2f} MB)")
        
        # Test 1: Force scanned optimization
        logger.info("\n=== Test 1: Force scanned optimization ===")
        optimized_pdf, metadata = pdf_optimizer.optimize_pdf(
            pdf_data,
            force_scanned_optimization=True
        )
        
        logger.info("Optimization metadata:")
        for key, value in metadata.items():
            logger.info(f"  {key}: {value}")
        
        # Test 2: Auto-detection
        logger.info("\n=== Test 2: Auto-detection of scanned PDF ===")
        is_scanned = pdf_optimizer.is_image_based_pdf(pdf_data)
        logger.info(f"Is scanned PDF detected: {is_scanned}")
        
        # Test 3: Regular optimization (should auto-detect and use scanned optimization)
        logger.info("\n=== Test 3: Regular optimization with auto-detection ===")
        optimized_pdf2, metadata2 = pdf_optimizer.optimize_pdf(pdf_data)
        
        logger.info("Auto-detection metadata:")
        for key, value in metadata2.items():
            logger.info(f"  {key}: {value}")
        
        # Save test results
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save optimized PDF
        output_file = output_dir / f"{test_pdf.stem}_optimized.pdf"
        with open(output_file, "wb") as f:
            f.write(optimized_pdf)
        
        logger.info(f"\nOptimized PDF saved to {output_file}")
        
        # Summary
        logger.info("\n=== Optimization Summary ===")
        logger.info(f"Original size: {original_size:,} bytes")
        logger.info(f"Optimized size: {len(optimized_pdf):,} bytes")
        logger.info(f"Size reduction: {(1 - len(optimized_pdf) / original_size) * 100:.1f}%")
        logger.info(f"Compression ratio: {metadata.get('compression_ratio', 'N/A')}")
        
        # Test with other PDFs for comparison
        logger.info("\n=== Testing other PDFs for comparison ===")
        
        for pdf_file in data_dir.glob("*.pdf"):
            if pdf_file == test_pdf:
                continue
            try:
                with open(pdf_file, "rb") as f:
                    pdf = f.read()
                is_scanned = pdf_optimizer.is_image_based_pdf(pdf)
                logger.info(f"{pdf_file.name}: Scanned={is_scanned}, Size={len(pdf):,} bytes")
            except Exception as e:
                logger.error(f"Error testing {pdf_file.name}: {e}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scanned_pdf_optimization()