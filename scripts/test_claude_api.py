#!/usr/bin/env python3
"""
Test Claude API integration
"""

import asyncio
import sys
from pathlib import Path
import argparse
from loguru import logger
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.llm_client import LLMClient
from app.core.config import settings


async def test_basic_completion():
    """Test basic text completion"""
    client = LLMClient()
    
    test_prompts = [
        {
            "prompt": "한국의 수도는 어디인가요?",
            "type": "simple_lookup",
            "expected": "서울"
        },
        {
            "prompt": "삼성전자의 2023년 매출액이 300조원이었다면, 영업이익률 10%일 때 영업이익은 얼마인가요?",
            "type": "simple_lookup",
            "expected": "30조원"
        },
        {
            "prompt": "반도체 산업의 최근 동향과 향후 전망에 대해 간단히 설명해주세요.",
            "type": "standard",
            "expected": "반도체"
        }
    ]
    
    results = []
    
    for test in test_prompts:
        logger.info(f"Testing prompt: {test['prompt'][:50]}...")
        
        try:
            response = await client.generate_text(
                prompt=test['prompt'],
                question_type=test['type'],
                max_tokens=500,
                temperature=0.3
            )
            
            success = test['expected'].lower() in response.lower()
            
            results.append({
                "prompt": test['prompt'],
                "type": test['type'],
                "response": response[:200] + "..." if len(response) > 200 else response,
                "success": success,
                "error": None
            })
            
            logger.info(f"Response received: {'✅' if success else '❌'}")
            
        except Exception as e:
            results.append({
                "prompt": test['prompt'],
                "type": test['type'],
                "response": None,
                "success": False,
                "error": str(e)
            })
            logger.error(f"Error: {str(e)}")
    
    return results


async def test_document_analysis():
    """Test document analysis capability"""
    client = LLMClient()
    
    # Sample financial document content
    sample_doc = """
    삼성전자 2024년 3분기 실적 발표
    
    1. 매출액: 79조원 (전년 동기 대비 12% 증가)
    2. 영업이익: 9.1조원 (영업이익률 11.5%)
    3. 당기순이익: 7.2조원
    
    주요 사업부별 실적:
    - 반도체(DS): 매출 23조원, 영업이익 3.8조원
    - 스마트폰(IM): 매출 28조원, 영업이익 2.8조원
    - 디스플레이(DP): 매출 7조원, 영업이익 0.7조원
    
    주요 성과:
    - HBM3 메모리 양산 본격화
    - 갤럭시 S24 시리즈 판매 호조
    - OLED 패널 수요 증가
    """
    
    test_questions = [
        "삼성전자의 3분기 매출액은 얼마인가요?",
        "반도체 사업부의 영업이익률을 계산해주세요.",
        "전년 대비 매출 성장률은 몇 퍼센트인가요?"
    ]
    
    results = []
    
    for question in test_questions:
        logger.info(f"Testing document analysis: {question}")
        
        try:
            result = await client.analyze_document(
                document_content=sample_doc,
                question=question,
                doc_type="financial_report"
            )
            
            results.append({
                "question": question,
                "answer": result['answer'],
                "success": True,
                "error": None
            })
            
            logger.info("Analysis completed successfully")
            
        except Exception as e:
            results.append({
                "question": question,
                "answer": None,
                "success": False,
                "error": str(e)
            })
            logger.error(f"Error: {str(e)}")
    
    return results


async def test_model_routing():
    """Test model routing logic"""
    client = LLMClient()
    
    test_cases = [
        ("simple_lookup", 0.3, "simple"),
        ("standard", 0.5, "standard"),
        ("complex_analysis", 0.8, "advanced"),
        ("simple_lookup", 0.9, "simple"),  # Simple type overrides complexity
    ]
    
    results = []
    
    for question_type, complexity, expected_tier in test_cases:
        model = client.select_model(question_type, complexity)
        
        if "haiku" in model and expected_tier == "simple":
            correct = True
        elif "sonnet" in model and expected_tier == "standard":
            correct = True
        elif "opus" in model and expected_tier == "advanced":
            correct = True
        else:
            correct = False
        
        results.append({
            "question_type": question_type,
            "complexity": complexity,
            "selected_model": model,
            "expected_tier": expected_tier,
            "correct": correct
        })
        
        logger.info(f"Model routing: {question_type}/{complexity} -> {model} {'✅' if correct else '❌'}")
    
    return results


async def test_rag_pipeline():
    """Test full RAG pipeline (requires indexed documents)"""
    from app.services.rag_pipeline import RAGPipeline
    from app.core.embedding_client import EmbeddingClient
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    
    try:
        # Initialize components
        chromadb_client = chromadb.HttpClient(
            host="localhost",
            port=8000,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        llm_client = LLMClient()
        embedding_client = EmbeddingClient()
        
        rag_pipeline = RAGPipeline(chromadb_client, llm_client, embedding_client)
        
        # Test questions
        test_questions = [
            "삼성전자의 최근 매출은 얼마인가요?",
            "LG전자의 주요 사업 분야는 무엇인가요?",
            "SK하이닉스의 HBM 제품에 대해 알려주세요."
        ]
        
        results = []
        
        for question in test_questions:
            logger.info(f"Testing RAG pipeline: {question}")
            
            try:
                answer, sources = await rag_pipeline.generate_response(
                    question=question,
                    top_k=3
                )
                
                results.append({
                    "question": question,
                    "answer": answer[:200] + "..." if len(answer) > 200 else answer,
                    "sources": sources,
                    "success": True,
                    "error": None
                })
                
                logger.info(f"Found {len(sources)} sources")
                
            except Exception as e:
                results.append({
                    "question": question,
                    "answer": None,
                    "sources": [],
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"Error: {str(e)}")
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
        return []


def print_test_results(test_name: str, results: List[Dict]):
    """Print test results in a formatted way"""
    print(f"\n{'='*60}")
    print(f" {test_name}")
    print(f"{'='*60}")
    
    if not results:
        print("No results to display")
        return
    
    success_count = sum(1 for r in results if r.get('success', False))
    total_count = len(results)
    
    print(f"Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {'✅' if result.get('success') else '❌'} ", end="")
        
        if 'prompt' in result:
            print(f"Prompt: {result['prompt'][:60]}...")
        elif 'question' in result:
            print(f"Question: {result['question'][:60]}...")
        elif 'question_type' in result:
            print(f"Type: {result['question_type']}, Complexity: {result['complexity']}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
        elif 'response' in result and result['response']:
            print(f"   Response: {result['response']}")
        elif 'answer' in result and result['answer']:
            print(f"   Answer: {result['answer']}")
        elif 'selected_model' in result:
            print(f"   Model: {result['selected_model']}")
        
        if 'sources' in result and result['sources']:
            print(f"   Sources: {', '.join(result['sources'][:3])}")
        
        print()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Claude API integration")
    parser.add_argument(
        "--test",
        choices=["basic", "document", "routing", "rag", "all"],
        default="basic",
        help="Type of test to run"
    )
    
    args = parser.parse_args()
    
    print(f"\n🤖 Claude API Test Suite")
    print(f"API Key: {'✅ Configured' if settings.CLAUDE_API_KEY else '❌ Missing'}")
    
    if not settings.CLAUDE_API_KEY:
        print("\n❌ Error: CLAUDE_API_KEY not found in environment variables")
        print("Please set your Claude API key in the .env file")
        return
    
    if args.test in ["basic", "all"]:
        logger.info("Running basic completion tests...")
        results = await test_basic_completion()
        print_test_results("Basic Completion Tests", results)
    
    if args.test in ["document", "all"]:
        logger.info("Running document analysis tests...")
        results = await test_document_analysis()
        print_test_results("Document Analysis Tests", results)
    
    if args.test in ["routing", "all"]:
        logger.info("Running model routing tests...")
        results = await test_model_routing()
        print_test_results("Model Routing Tests", results)
    
    if args.test in ["rag", "all"]:
        logger.info("Running RAG pipeline tests...")
        results = await test_rag_pipeline()
        if results:
            print_test_results("RAG Pipeline Tests", results)
        else:
            print("\n⚠️  RAG pipeline tests require indexed documents.")
            print("   Run the indexing scripts first:")
            print("   1. python scripts/setup_file_system.py --with-samples")
            print("   2. python scripts/index_documents.py")
    
    print("\n✅ Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())