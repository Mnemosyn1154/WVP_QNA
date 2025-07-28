#!/usr/bin/env python3
"""Test environment variable loading"""

import os
import sys
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv()

print("=== Environment Variable Test ===\n")

# Check critical environment variables
env_vars = [
    "CLAUDE_API_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "CHROMADB_URL",
    "SECRET_KEY"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Show only first 10 chars for sensitive data
        display_value = value[:10] + "..." if len(value) > 10 else value
        print(f"✓ {var}: {display_value}")
    else:
        print(f"✗ {var}: NOT SET")

# Test loading through pydantic settings
print("\n=== Testing Pydantic Settings ===")
try:
    from app.core.config import settings
    print(f"✓ Settings loaded successfully")
    print(f"  - APP_NAME: {settings.APP_NAME}")
    print(f"  - CLAUDE_API_KEY present: {bool(settings.CLAUDE_API_KEY)}")
    print(f"  - DEBUG: {settings.DEBUG}")
except Exception as e:
    print(f"✗ Failed to load settings: {e}")

# Test Claude service initialization
print("\n=== Testing Claude Service ===")
try:
    from app.services.claude_service import ClaudeService
    claude = ClaudeService()
    print(f"✓ Claude service initialized")
    print(f"  - Test mode: {claude.test_mode}")
    print(f"  - API key present: {bool(claude.api_key)}")
    print(f"  - Client initialized: {claude.client is not None}")
except Exception as e:
    print(f"✗ Failed to initialize Claude service: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")