#!/usr/bin/env python3
"""
Test PDF compression for 설로인 and 마인이스 PDFs
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.pdf_optimizer import PDFOptimizer, CompressionLevel


def test_pdf_compression():
    """Test PDF compression with different levels"""
    
    optimizer = PDFOptimizer()
    
    pdfs = [
        ("설로인", "data/financial_docs/설로인/2024/설로인_2024_재무제표.pdf"),
        ("마인이스", "data/financial_docs/마인이스/2024/마인이스_2024_재무제표.pdf")
    ]
    
    for company, pdf_path in pdfs:
        if not Path(pdf_path).exists():
            print(f"❌ File not found: {pdf_path}")
            continue
            
        print(f"\n{'='*60}")
        print(f"Testing {company} PDF")
        print(f"{'='*60}")
        
        # Read original PDF
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()
        
        original_size = len(pdf_content) / 1024 / 1024
        print(f"Original size: {original_size:.2f} MB")
        
        # Check if image-based
        is_scanned = optimizer.is_image_based_pdf(pdf_content)
        print(f"Is image-based: {is_scanned}")
        
        # Test different compression levels
        if is_scanned:
            # Test ULTRA_LOW for scanned PDFs
            print("\n🔥 Testing ULTRA_LOW compression...")
            optimized, metadata = optimizer.optimize_pdf(
                pdf_content,
                compression_level=CompressionLevel.ULTRA_LOW,
                target_size_mb=1.0
            )
            
            optimized_size = len(optimized) / 1024 / 1024
            compression_ratio = (1 - optimized_size / original_size) * 100
            
            print(f"Optimized size: {optimized_size:.2f} MB")
            print(f"Compression ratio: {compression_ratio:.1f}%")
            print(f"Metadata: {metadata}")
            
            # Save test file
            test_output = f"test_output_{company}_ultra_low.pdf"
            with open(test_output, "wb") as f:
                f.write(optimized)
            print(f"Saved test file: {test_output}")
        else:
            # Test SCREEN for regular PDFs
            print("\n📄 Testing SCREEN compression...")
            optimized, metadata = optimizer.optimize_pdf(
                pdf_content,
                compression_level=CompressionLevel.SCREEN
            )
            
            optimized_size = len(optimized) / 1024 / 1024
            compression_ratio = (1 - optimized_size / original_size) * 100
            
            print(f"Optimized size: {optimized_size:.2f} MB")
            print(f"Compression ratio: {compression_ratio:.1f}%")


if __name__ == "__main__":
    print("🧪 Testing PDF Compression")
    print("="*60)
    test_pdf_compression()