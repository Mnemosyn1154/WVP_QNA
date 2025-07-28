#!/usr/bin/env python3
"""
Test Gemini integration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.gemini_service import GeminiService
from loguru import logger


async def test_gemini_service():
    """Test basic Gemini service functionality"""
    
    logger.info("Testing Gemini service...")
    
    # Initialize service
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCEPAGmLnxEpJwGMrsJ6qQq__0Nwt0LDOw")
    gemini_service = GeminiService(api_key=api_key)
    
    # Test 1: Simple question without context
    print("\n=== Test 1: Simple Question ===")
    result = await gemini_service.ask_simple_question(
        question="마인이스의 주요 사업은 무엇인가요?"
    )
    print(f"Answer: {result['answer'][:200]}...")
    print(f"Processing time: {result['processing_time']:.2f}s")
    print(f"Token usage: {result.get('usage', 'N/A')}")
    
    # Test 2: Question with context
    print("\n=== Test 2: Question with Context ===")
    context = """
    마인이스 2024년 재무제표
    매출액: 1,500억원
    영업이익: 250억원
    당기순이익: 180억원
    주요 사업: AI 솔루션 개발 및 컨설팅
    """
    
    result = await gemini_service.ask_simple_question(
        question="마인이스의 2024년 영업이익률은 얼마인가요?",
        context=context
    )
    print(f"Answer: {result['answer']}")
    print(f"Processing time: {result['processing_time']:.2f}s")
    
    # Test 3: Check availability
    print("\n=== Test 3: Availability Check ===")
    is_available = await gemini_service.check_availability()
    print(f"Gemini API available: {is_available}")


async def test_with_chat_service():
    """Test Gemini through chat service"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.services.chat_service import ChatService
    
    print("\n=== Test 4: Chat Service Integration ===")
    
    # Create DB session
    engine = create_engine("sqlite:///./data/portfolio_qa.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        chat_service = ChatService(db)
        
        # Test question
        response = await chat_service.process_query(
            question="마인이스의 2024년 매출액은 얼마인가요?"
        )
        
        print(f"Answer: {response.answer[:200]}...")
        print(f"Sources: {response.sources}")
        print(f"Model used: {response.metadata.get('model_used')}")
        print(f"LLM provider: {response.metadata.get('llm_provider')}")
        print(f"Processing time: {response.processing_time:.2f}s")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("🧪 Testing Gemini Integration")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_gemini_service())
    asyncio.run(test_with_chat_service())
    
    print("\n✅ Gemini integration test completed!")