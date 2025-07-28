#!/usr/bin/env python3
"""
Analyze PDF structure to understand token usage
"""

import fitz  # PyMuPDF
import sys
from pathlib import Path

def analyze_pdf(pdf_path):
    """Analyze PDF structure and content"""
    pdf = fitz.open(pdf_path)
    
    print(f"\n📄 PDF Analysis: {Path(pdf_path).name}")
    print("=" * 60)
    
    # Basic info
    print(f"Total pages: {len(pdf)}")
    print(f"PDF version: {pdf.metadata.get('format', 'Unknown')}")
    print(f"File size: {Path(pdf_path).stat().st_size / 1024 / 1024:.2f} MB")
    
    # Analyze content
    total_text_length = 0
    total_images = 0
    total_image_size = 0
    image_details = []
    
    for page_num, page in enumerate(pdf):
        # Text analysis
        text = page.get_text()
        total_text_length += len(text)
        
        # Image analysis
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(pdf, xref)
            img_size = len(pix.tobytes())
            total_images += 1
            total_image_size += img_size
            
            image_details.append({
                'page': page_num + 1,
                'width': pix.width,
                'height': pix.height,
                'size_kb': img_size / 1024,
                'colorspace': pix.colorspace.name if pix.colorspace else 'Unknown'
            })
            
            pix = None  # Free memory
    
    print(f"\n📝 Text Content:")
    print(f"Total text characters: {total_text_length:,}")
    print(f"Average chars per page: {total_text_length / len(pdf):,.0f}")
    
    print(f"\n🖼️ Image Content:")
    print(f"Total images: {total_images}")
    print(f"Total image size: {total_image_size / 1024 / 1024:.2f} MB")
    
    if image_details:
        print(f"\nTop 5 largest images:")
        sorted_images = sorted(image_details, key=lambda x: x['size_kb'], reverse=True)[:5]
        for i, img in enumerate(sorted_images, 1):
            print(f"  {i}. Page {img['page']}: {img['width']}x{img['height']}, "
                  f"{img['size_kb']:.1f} KB, {img['colorspace']}")
    
    # Estimate token usage
    # Rough estimation: text chars * 0.25 + image complexity factor
    estimated_tokens = (total_text_length * 0.25) + (total_images * 1000)
    print(f"\n🔢 Estimated token usage: {estimated_tokens:,.0f}")
    print(f"   - From text: {total_text_length * 0.25:,.0f}")
    print(f"   - From images: {total_images * 1000:,.0f}")
    
    pdf.close()

if __name__ == "__main__":
    # Analyze both PDFs
    pdfs = [
        "data/financial_docs/설로인/2024/설로인_2024_재무제표.pdf",
        "data/financial_docs/마인이스/2024/마인이스_2024_재무제표.pdf"
    ]
    
    for pdf_path in pdfs:
        if Path(pdf_path).exists():
            analyze_pdf(pdf_path)
        else:
            print(f"❌ File not found: {pdf_path}")