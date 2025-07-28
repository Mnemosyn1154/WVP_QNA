#!/usr/bin/env python3
"""Test Claude API directly"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv("CLAUDE_API_KEY")
if not api_key:
    from app.core.config import settings
    api_key = settings.CLAUDE_API_KEY

print(f"API Key present: {bool(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}")

# Test simple message
try:
    client = Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Hello, can you respond with a simple test message?"
            }
        ]
    )
    
    print("\n✓ Claude API call successful!")
    print(f"Response: {message.content[0].text}")
    
except Exception as e:
    print(f"\n✗ Claude API call failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()