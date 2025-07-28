#!/usr/bin/env python3
"""Test backend connection and diagnose issues"""

import requests
import json
import sys
from pathlib import Path

# Test configurations
BASE_URL = "http://127.0.0.1:8081"
FRONTEND_ORIGIN = "http://localhost:4001"

def test_health():
    """Test health endpoint"""
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_cors_preflight():
    """Test CORS preflight request"""
    print("\n2. Testing CORS preflight...")
    try:
        response = requests.options(
            f"{BASE_URL}/api/chat/",
            headers={
                "Origin": FRONTEND_ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers:")
        for header in ["Access-Control-Allow-Origin", "Access-Control-Allow-Methods", 
                      "Access-Control-Allow-Headers", "Access-Control-Allow-Credentials"]:
            value = response.headers.get(header, "Not present")
            print(f"     {header}: {value}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint with actual request"""
    print("\n3. Testing chat endpoint...")
    
    # Test with test mode first
    import os
    os.environ["CLAUDE_TEST_MODE"] = "true"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/",
            json={"question": "마인이스의 2024년 매출액은 얼마입니까?"},
            headers={
                "Content-Type": "application/json",
                "Origin": FRONTEND_ORIGIN
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"   Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_from_frontend_perspective():
    """Test exactly how frontend would call the API"""
    print("\n4. Testing from frontend perspective...")
    try:
        # Simulate axios request
        response = requests.post(
            f"{BASE_URL}/api/chat",  # Without trailing slash first
            json={"question": "테스트 질문입니다"},
            headers={
                "Content-Type": "application/json",
                "Origin": FRONTEND_ORIGIN,
                "Referer": f"{FRONTEND_ORIGIN}/chat",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            },
            allow_redirects=True  # Follow redirects automatically
        )
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"   Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def check_file_system():
    """Check if required files exist"""
    print("\n5. Checking file system...")
    data_path = Path("data/financial_docs")
    if data_path.exists():
        print(f"   Data directory exists: {data_path}")
        pdf_files = list(data_path.glob("*.pdf"))
        print(f"   PDF files found: {len(pdf_files)}")
        for pdf in pdf_files[:3]:  # Show first 3
            print(f"     - {pdf.name}")
    else:
        print(f"   Data directory not found: {data_path}")
    
    return data_path.exists()

def main():
    """Run all tests"""
    print("=== Backend Connection Diagnostics ===\n")
    
    results = {
        "Health Check": test_health(),
        "CORS Preflight": test_cors_preflight(),
        "Chat Endpoint": test_chat_endpoint(),
        "Frontend Simulation": test_from_frontend_perspective(),
        "File System": check_file_system()
    }
    
    print("\n=== Summary ===")
    for test, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test}: {status}")
    
    if not all(results.values()):
        print("\n⚠️  Some tests failed. Please check the output above for details.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")

if __name__ == "__main__":
    main()