#!/usr/bin/env python3
"""Test Claude API with PDF document"""

import os
import base64
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv("CLAUDE_API_KEY")
if not api_key:
    raise ValueError("CLAUDE_API_KEY not found in environment")

print(f"API Key present: {bool(api_key)}")

# Test with PDF
try:
    client = Anthropic(api_key=api_key)
    
    # Read a sample PDF
    pdf_path = "data/financial_docs/마인이스/2024/마인이스_2024_재무제표.pdf"
    
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()
    
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    print(f"\nPDF loaded: {len(pdf_content)} bytes")
    
    # Try different approaches
    
    # Approach 1: Using beta API with document type (Sonnet model)
    print("\n1. Testing beta API with document type (Sonnet)...")
    try:
        message = client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "이 PDF 문서의 첫 페이지에 어떤 내용이 있나요?"
                        }
                    ]
                }
            ]
        )
        print("✓ Beta API with document type successful!")
        print(f"Response: {message.content[0].text[:200]}...")
    except Exception as e:
        print(f"✗ Beta API with document type failed: {type(e).__name__}: {e}")
    
    # Approach 2: Using regular API with image type (PDF as image)
    print("\n2. Testing regular API with image type...")
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "이 문서의 첫 페이지에 어떤 내용이 있나요?"
                        }
                    ]
                }
            ]
        )
        print("✓ Regular API with image type successful!")
        print(f"Response: {message.content[0].text[:200]}...")
    except Exception as e:
        print(f"✗ Regular API with image type failed: {type(e).__name__}: {e}")
    
    # Approach 3: Using tools/functions API
    print("\n3. Testing with tools API...")
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            tools=[
                {
                    "name": "analyze_document",
                    "description": "Analyze a PDF document",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "The content of the document"
                            }
                        }
                    }
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"Please analyze this PDF document (base64): {pdf_base64[:100]}..."
                }
            ]
        )
        print("✓ Tools API successful!")
        print(f"Response: {message.content[0].text[:200] if message.content and message.content[0].text else 'No text response'}...")
    except Exception as e:
        print(f"✗ Tools API failed: {type(e).__name__}: {e}")
    
except Exception as e:
    print(f"\n✗ General error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()