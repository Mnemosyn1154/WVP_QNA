"""
Gemini Service for Simple Queries
Uses Gemini Pro for cost-effective simple lookups and basic questions
"""

import os
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from loguru import logger
import time
import asyncio


class GeminiService:
    """
    Service for handling simple queries with Gemini Pro
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 1.5 Flash model for simple queries (cost-effective)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System prompt for financial analysis
        self.system_prompt = """당신은 한국 투자 포트폴리오 기업의 재무 정보를 분석하는 전문가입니다.
        
        간단하고 명확한 답변을 제공해주세요. 주요 수치와 사실을 중심으로 답변하되,
        복잡한 계산이나 깊은 분석이 필요한 경우 그렇다고 명시해주세요.
        
        답변 형식:
        - 핵심 정보를 먼저 제시
        - 간단명료하게 설명
        - 필요시 주요 수치 포함
        """
        
    async def ask_simple_question(
        self,
        question: str,
        context: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Ask a simple question to Gemini Pro
        
        Args:
            question: User's question
            context: Optional context (text only)
            max_tokens: Maximum response tokens
            
        Returns:
            Dict with answer and metadata
        """
        start_time = time.time()
        
        try:
            # Prepare prompt
            prompt_parts = [self.system_prompt]
            
            if context:
                prompt_parts.append(f"\n\n참고 정보:\n{context}")
            
            prompt_parts.append(f"\n\n질문: {question}")
            prompt_parts.append("\n\n답변:")
            
            full_prompt = "\n".join(prompt_parts)
            
            # Generate response
            logger.info(f"Sending simple query to Gemini Pro: {question[:100]}...")
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.1,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            # Extract answer
            answer = response.text if response.text else "답변을 생성할 수 없습니다."
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Estimate token usage (rough approximation)
            input_tokens = len(full_prompt) // 4
            output_tokens = len(answer) // 4
            
            return {
                "answer": answer,
                "model": "gemini-1.5-flash",
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "processing_time": processing_time,
                "complexity": "simple"
            }
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return {
                "answer": f"Gemini API 오류: {str(e)}",
                "model": "gemini-1.5-flash",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def check_availability(self) -> bool:
        """Check if Gemini API is available"""
        try:
            # Simple test query
            response = await self.ask_simple_question("안녕하세요")
            return "error" not in response
        except Exception as e:
            logger.error(f"Gemini availability check failed: {e}")
            return False
    
    def format_context_for_gemini(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format document context for Gemini (text only)
        
        Args:
            documents: List of documents with metadata
            
        Returns:
            Formatted text context
        """
        context_parts = []
        
        for doc in documents:
            # Add document header
            header = f"[{doc.get('company_name')} - {doc.get('year')}년 {doc.get('doc_type')}]"
            context_parts.append(header)
            
            # For Gemini, we need to extract text from PDFs
            # This is a limitation compared to Claude
            if doc.get('content_type') == 'text':
                context_parts.append(doc.get('content', ''))
            else:
                context_parts.append("(PDF 문서 - 텍스트 추출 필요)")
            
            context_parts.append("")  # Empty line between documents
        
        return "\n".join(context_parts)