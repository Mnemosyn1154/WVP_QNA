#!/usr/bin/env python3
"""Test chat service directly to identify issues"""

import os
import asyncio
from app.db.session import SessionLocal
from app.services.chat_service import ChatService
from loguru import logger

# Enable test mode
os.environ["CLAUDE_TEST_MODE"] = "true"

async def test_chat_service():
    """Test the chat service directly"""
    db = SessionLocal()
    try:
        # Create chat service
        chat_service = ChatService(db=db)
        
        # Test questions
        test_questions = [
            "마인이스의 2024년 매출액은 얼마입니까?",
            "우나스텔라의 최근 실적은 어떻습니까?",
            "설로인의 사업 현황을 알려주세요"
        ]
        
        for question in test_questions:
            print(f"\n{'='*50}")
            print(f"Testing question: {question}")
            print('='*50)
            
            try:
                response = await chat_service.process_query(
                    question=question,
                    context=None
                )
                
                print(f"✓ Success!")
                print(f"Answer: {response.answer[:200]}...")
                print(f"Sources: {response.sources}")
                print(f"Processing time: {response.processing_time:.2f}s")
                
            except Exception as e:
                print(f"✗ Error: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
    
    finally:
        db.close()

def test_document_service():
    """Test document service separately"""
    from app.services.document_service import DocumentService
    
    db = SessionLocal()
    try:
        doc_service = DocumentService(db)
        
        # Test company extraction
        test_questions = [
            "마인이스의 2024년 매출액은?",
            "우나스텔라 최근 실적",
            "설로인 사업 현황"
        ]
        
        print("\n=== Testing Document Service ===")
        for question in test_questions:
            company = doc_service.extract_company_from_question(question)
            year = doc_service.extract_year_from_question(question)
            print(f"Question: {question}")
            print(f"  - Extracted company: {company}")
            print(f"  - Extracted year: {year}")
            
            if company:
                document, pdf_content = doc_service.get_document_for_question(question)
                if document:
                    print(f"  - Found document: {document.file_path}")
                    print(f"  - PDF content size: {len(pdf_content) if pdf_content else 0} bytes")
                else:
                    print("  - No document found")
            print()
    
    finally:
        db.close()

def test_claude_service():
    """Test Claude service initialization"""
    print("\n=== Testing Claude Service ===")
    from app.services.claude_service import ClaudeService
    
    try:
        claude = ClaudeService()
        print(f"✓ Claude service initialized successfully")
        print(f"  - Test mode: {claude.test_mode}")
        print(f"  - API key present: {bool(claude.api_key)}")
        print(f"  - Client initialized: {claude.client is not None}")
    except Exception as e:
        print(f"✗ Failed to initialize Claude service: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    # Test individual components
    test_document_service()
    test_claude_service()
    
    # Test full chat service
    await test_chat_service()

if __name__ == "__main__":
    asyncio.run(main())