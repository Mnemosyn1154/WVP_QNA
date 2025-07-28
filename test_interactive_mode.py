#!/usr/bin/env python3
"""
Test script for interactive Claude mode
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.services.interactive_claude_service import InteractiveClaudeService
from loguru import logger


async def test_interactive_mode():
    """Test the interactive mode with various questions"""
    
    # Initialize service
    service = InteractiveClaudeService()
    db = SessionLocal()
    
    try:
        # Test cases
        test_questions = [
            # Simple single company question
            "마인이스의 2024년 매출은 얼마인가요?",
            
            # Comparison question that should trigger multiple requests
            "마인이스와 설로인의 2024년 매출을 비교해서 알려주세요.",
            
            # Complex question requiring multiple documents
            "마인이스의 2023년과 2024년 매출 성장률을 계산해주세요.",
            
            # Question without specifying company
            "2024년 매출이 가장 높은 회사는 어디인가요?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {question}")
            print(f"{'='*60}")
            
            try:
                result = await service.interactive_chat(
                    question=question,
                    db=db,
                    max_iterations=5
                )
                
                print(f"\n📝 Answer:")
                print(result["answer"])
                
                print(f"\n📊 Metadata:")
                print(f"- Model: {result['model_used']}")
                print(f"- Iterations: {result['usage']['iterations']}")
                print(f"- Total tokens: {result['usage']['total_tokens']}")
                print(f"- Documents provided: {result['documents_provided']}")
                print(f"- Processing time: {result['processing_time']:.2f}s")
                
                if result.get("provided_documents"):
                    print(f"\n📚 Documents used:")
                    for doc in result["provided_documents"]:
                        print(f"  - {doc['company']} {doc['year']}년 {doc['type']}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.exception("Test failed")
            
            # Wait a bit between tests
            await asyncio.sleep(2)
            
    finally:
        db.close()


async def test_protocol_parsing():
    """Test the protocol parsing functionality"""
    from app.core.llm_protocol import LLMProtocol
    
    protocol = LLMProtocol()
    
    # Test response with document request
    test_response = """
    질문에 답변하기 위해 추가 정보가 필요합니다.
    
    <request_document>
    {
      "type": "financial_report",
      "company_name": "마인이스",
      "year": 2024,
      "doc_type": "재무제표"
    }
    </request_document>
    
    문서를 확인한 후 답변드리겠습니다.
    """
    
    requests = protocol.parse_response_for_requests(test_response)
    print(f"Found {len(requests)} requests")
    for req in requests:
        print(f"- Type: {req.request_type.value}")
        print(f"  Company: {req.company_name}")
        print(f"  Year: {req.year}")
        print(f"  Doc type: {req.doc_type}")
    
    # Test final answer extraction
    clean_answer = protocol.extract_final_answer(test_response)
    print(f"\nClean answer:\n{clean_answer}")


if __name__ == "__main__":
    print("🧪 Testing Interactive Claude Mode")
    print("==================================\n")
    
    # Test protocol parsing first
    print("1. Testing Protocol Parsing")
    print("-" * 30)
    asyncio.run(test_protocol_parsing())
    
    print("\n\n2. Testing Interactive Chat")
    print("-" * 30)
    asyncio.run(test_interactive_mode())