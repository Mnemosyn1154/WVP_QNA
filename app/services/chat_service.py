"""
Chat service for handling Q&A requests
"""

from typing import Dict, Any, Optional, List
import time
import json
import hashlib
from loguru import logger
from sqlalchemy.orm import Session

from app.services.claude_service import ClaudeService
from app.services.document_service import DocumentService
from app.services.pdf_processor import PDFProcessor
from app.schemas.chat_schemas import ChatResponse
from app.models.chat_history import ChatHistory


class ChatService:
    """Service for handling chat/Q&A functionality"""
    
    def __init__(self, db: Session):
        self.db = db
        self.claude_service = ClaudeService()
        self.document_service = DocumentService(db)
        self.pdf_processor = PDFProcessor()
        # Redis will be added later
        self.cache = {}
    
    async def process_query(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> ChatResponse:
        """
        Process a user query and return response
        
        Args:
            question: User's question
            context: Additional context
            user_id: Optional user ID for history
        
        Returns:
            ChatResponse with answer and metadata
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(question, context)
            cached_response = self._get_cached_response(cache_key)
            
            if cached_response:
                logger.info("Returning cached response")
                processing_time = time.time() - start_time
                cached_response["processing_time"] = processing_time
                return ChatResponse(**cached_response)
            
            # Find relevant document for the question
            document, pdf_content = self.document_service.get_document_for_question(question)
            
            if not document or not pdf_content:
                return ChatResponse(
                    answer="죄송합니다. 해당 질문에 대한 관련 문서를 찾을 수 없습니다. 회사명과 연도를 구체적으로 명시해주세요.",
                    sources=[],
                    processing_time=time.time() - start_time
                )
            
            # Check if PDF needs optimization
            if len(pdf_content) > 10 * 1024 * 1024:  # 10MB
                logger.info(f"Optimizing large PDF: {document.file_path}")
                pdf_content, optimization_metadata = self.pdf_processor.optimize_pdf(pdf_content)
                logger.info(f"PDF optimized: {optimization_metadata}")
            
            # Send to Claude API
            result = await self.claude_service.analyze_pdf_with_question(
                pdf_content=pdf_content,
                question=question,
                company_name=document.company_name,
                doc_year=document.year,
                doc_type=document.doc_type
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create response
            response = ChatResponse(
                answer=result["answer"],
                sources=[f"{document.company_name} {document.year}년 {document.doc_type}"],
                charts=None,  # TODO: Implement chart generation if needed
                processing_time=processing_time,
                metadata={
                    "model_used": result["model_used"],
                    "token_usage": result["usage"],
                    "estimated_cost": self.claude_service.estimate_cost(result["usage"], result["model_used"])
                }
            )
            
            # Cache the response
            self._cache_response(cache_key, response.model_dump())
            
            # Save to history
            self._save_to_history(
                user_id=user_id,
                question=question,
                answer=result["answer"],
                sources=[f"{document.company_name} {document.year}년 {document.doc_type}"],
                context=context,
                metadata=result
            )
            
            # Track API usage for cost monitoring
            self._track_api_usage(result["usage"], result["model_used"])
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            processing_time = time.time() - start_time
            
            # Return error response
            return ChatResponse(
                answer=f"죄송합니다. 질문을 처리하는 중 오류가 발생했습니다: {str(e)}",
                sources=[],
                processing_time=processing_time
            )
    
    def _generate_cache_key(self, question: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for question"""
        cache_data = {
            "question": question,
            "context": context or {}
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"chat:response:{cache_hash}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if exists"""
        # Simple in-memory cache for now, Redis will be added later
        return self.cache.get(cache_key)
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response with TTL"""
        # Simple in-memory cache for now, Redis will be added later
        self.cache[cache_key] = response
        
        # Limit cache size
        if len(self.cache) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    def _save_to_history(
        self,
        user_id: Optional[int],
        question: str,
        answer: str,
        sources: List[str],
        context: Optional[Dict[str, Any]],
        metadata: Dict[str, Any]
    ):
        """Save chat to history"""
        try:
            history = ChatHistory(
                user_id=user_id,
                question=question,
                answer=answer,
                context={
                    "sources": sources,
                    "original_context": context,
                    "metadata": metadata
                }
            )
            self.db.add(history)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving to history: {str(e)}")
            self.db.rollback()
    
    def _track_api_usage(self, usage: Dict[str, int], model: str):
        """Track API usage for cost monitoring"""
        try:
            # For now, just log the usage
            # Redis tracking will be added later
            total_tokens = usage["total_tokens"]
            estimated_cost = self.claude_service.estimate_cost(usage, model)
            
            logger.info(f"API Usage - Tokens: {total_tokens}, Estimated cost: ${estimated_cost:.4f}")
            
        except Exception as e:
            logger.warning(f"Error tracking API usage: {str(e)}")
    
    def check_daily_limit(self) -> bool:
        """Check if daily API limit is exceeded"""
        # For now, always allow - Redis tracking will be added later
        return True