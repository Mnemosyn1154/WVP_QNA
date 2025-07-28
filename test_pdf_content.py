#!/usr/bin/env python3
"""
Test PDF content extraction
"""

import fitz  # PyMuPDF
import sys

pdf_path = "data/financial_docs/마인이스/2024/마인이스_2024_재무제표.pdf"

try:
    # Open PDF
    pdf_document = fitz.open(pdf_path)
    
    print(f"PDF Pages: {len(pdf_document)}")
    print("=" * 60)
    
    # Extract text from first few pages
    for page_num in range(min(3, len(pdf_document))):
        page = pdf_document[page_num]
        text = page.get_text()
        
        print(f"\n--- Page {page_num + 1} ---")
        print(text[:500])  # First 500 characters
        
        # Look for revenue/sales keywords
        if any(keyword in text for keyword in ["매출", "수익", "revenue", "sales", "1,234,567"]):
            print("\n[FOUND REVENUE DATA]")
            # Find lines containing revenue info
            for line in text.split('\n'):
                if any(keyword in line for keyword in ["매출", "수익", "1,234,567"]):
                    print(f"  > {line.strip()}")
    
    pdf_document.close()
    
except Exception as e:
    print(f"Error: {e}")