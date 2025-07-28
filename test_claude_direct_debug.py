#!/usr/bin/env python3
"""
Direct test of Claude API with PDF
"""

import os
import sys
import base64
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("CLAUDE_API_KEY")
if not api_key:
    print("CLAUDE_API_KEY not found in environment")
    sys.exit(1)

print(f"API Key exists: {bool(api_key)}")
print(f"API Key prefix: {api_key[:10]}...")

# Initialize client
client = Anthropic(api_key=api_key)

# Read PDF
pdf_path = "data/financial_docs/마인이스/2024/마인이스_2024_재무제표.pdf"
with open(pdf_path, "rb") as f:
    pdf_content = f.read()

print(f"PDF size: {len(pdf_content) / 1024:.2f} KB")

# Convert to base64
pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

# Test with Claude
try:
    print("\nSending to Claude API...")
    
    message = client.beta.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0.1,
        system="당신은 재무 분석 전문가입니다. PDF 문서를 정확히 읽고 구체적인 수치를 제공해주세요.",
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
                        "text": "이 문서에서 2024년 매출액을 찾아주세요. 정확한 숫자를 알려주세요."
                    }
                ]
            }
        ]
    )
    
    print("\nClaude Response:")
    print("-" * 60)
    print(message.content[0].text)
    print("-" * 60)
    
    print(f"\nTokens used: {message.usage.input_tokens + message.usage.output_tokens}")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()