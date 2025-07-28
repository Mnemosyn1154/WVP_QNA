#!/usr/bin/env python3
"""Test FastAPI endpoint directly"""

import os
os.environ["CLAUDE_TEST_MODE"] = "true"

from fastapi.testclient import TestClient
from app.main import app
import json

# Create test client
client = TestClient(app)

def test_health():
    """Test health endpoint"""
    print("=== Testing Health Endpoint ===")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_chat_endpoint():
    """Test chat endpoint"""
    print("=== Testing Chat Endpoint ===")
    
    # Test with trailing slash
    response = client.post(
        "/api/chat/",
        json={"question": "마인이스의 2024년 매출액은?"},
        headers={"Origin": "http://localhost:4001"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
        # Print full error details
        if response.status_code == 500:
            print("\nDetailed error information:")
            import traceback
            # Try to get exception details from FastAPI
            try:
                detail = response.json()
                print(f"Detail: {detail}")
            except:
                print("Could not parse error detail")
    
    # Also check CORS headers
    print(f"\nCORS Headers:")
    for header in ["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"]:
        value = response.headers.get(header, "Not present")
        print(f"  {header}: {value}")

def test_cors_preflight():
    """Test CORS preflight"""
    print("\n=== Testing CORS Preflight ===")
    response = client.options(
        "/api/chat/",
        headers={
            "Origin": "http://localhost:4001",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
    )
    
    print(f"Status: {response.status_code}")
    print("CORS Headers:")
    for header in ["Access-Control-Allow-Origin", "Access-Control-Allow-Methods", 
                  "Access-Control-Allow-Headers", "Access-Control-Allow-Credentials"]:
        value = response.headers.get(header, "Not present")
        print(f"  {header}: {value}")

if __name__ == "__main__":
    test_health()
    test_cors_preflight()
    test_chat_endpoint()