"""
Test script for PDF optimization functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_optimizer import PDFOptimizer, CompressionLevel
import glob
import json


def test_pdf_optimization():
    """Test PDF optimization with sample files"""
    optimizer = PDFOptimizer()
    
    # Find sample PDF files
    pdf_files = glob.glob("data/financial_docs/**/*.pdf", recursive=True)
    
    if not pdf_files:
        print("No PDF files found in data/financial_docs/")
        return
    
    print(f"Found {len(pdf_files)} PDF files to test\n")
    
    results = []
    
    for pdf_path in pdf_files[:3]:  # Test first 3 files
        print(f"\nTesting: {pdf_path}")
        print("-" * 50)
        
        try:
            # Read PDF file
            with open(pdf_path, "rb") as f:
                original_content = f.read()
            
            original_size_mb = len(original_content) / (1024 * 1024)
            print(f"Original size: {original_size_mb:.2f} MB")
            
            # Test different compression levels
            for level in [CompressionLevel.SCREEN, CompressionLevel.EBOOK]:
                print(f"\nTesting {level.name} compression...")
                
                optimized_content, metadata = optimizer.optimize_pdf(
                    pdf_content=original_content,
                    compression_level=level,
                    use_ghostscript=True
                )
                
                optimized_size_mb = len(optimized_content) / (1024 * 1024)
                compression_ratio = (1 - len(optimized_content) / len(original_content)) * 100
                
                print(f"Optimized size: {optimized_size_mb:.2f} MB")
                print(f"Compression: {compression_ratio:.1f}%")
                print(f"Methods used: {', '.join(metadata.get('compression_methods', []))}")
                
                # Save result
                result = {
                    "file": os.path.basename(pdf_path),
                    "compression_level": level.name,
                    "original_size_mb": round(original_size_mb, 2),
                    "optimized_size_mb": round(optimized_size_mb, 2),
                    "compression_ratio": round(compression_ratio, 1),
                    "metadata": metadata
                }
                results.append(result)
                
                # Save optimized file for inspection
                output_path = f"test_output_{os.path.basename(pdf_path).replace('.pdf', '')}_{level.name}.pdf"
                with open(output_path, "wb") as f:
                    f.write(optimized_content)
                print(f"Saved optimized file: {output_path}")
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            results.append({
                "file": os.path.basename(pdf_path),
                "error": str(e)
            })
    
    # Save results to JSON
    with open("pdf_optimization_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n\nOptimization Summary")
    print("=" * 60)
    for result in results:
        if "error" in result:
            print(f"{result['file']}: ERROR - {result['error']}")
        else:
            print(f"{result['file']} ({result['compression_level']}): "
                  f"{result['original_size_mb']} MB → {result['optimized_size_mb']} MB "
                  f"({result['compression_ratio']}% reduction)")
    
    # Generate report
    report = optimizer.get_optimization_report(
        original_size=int(original_size_mb * 1024 * 1024),
        optimized_size=int(optimized_size_mb * 1024 * 1024),
        metadata=metadata
    )
    print("\n" + report)


def test_ghostscript_availability():
    """Test if Ghostscript is available"""
    optimizer = PDFOptimizer()
    if optimizer._check_ghostscript():
        print("✓ Ghostscript is available")
        import subprocess
        result = subprocess.run(["gs", "--version"], capture_output=True, text=True)
        print(f"  Version: {result.stdout.strip()}")
    else:
        print("✗ Ghostscript is not available")
        print("  To install on macOS: brew install ghostscript")
        print("  To install on Ubuntu: sudo apt-get install ghostscript")


if __name__ == "__main__":
    print("PDF Optimizer Test Suite")
    print("=" * 60)
    
    # Check Ghostscript
    test_ghostscript_availability()
    print()
    
    # Test optimization
    test_pdf_optimization()