"""
Chat service for handling Q&A requests
"""

from typing import Dict, Any, Optional, List
import time
import json
import hashlib
import os
from loguru import logger
from sqlalchemy.orm import Session

from app.services.claude_service import ClaudeService
from app.services.interactive_claude_service import InteractiveClaudeService
from app.services.gemini_service import GeminiService
from app.services.document_service import DocumentService
from app.services.pdf_processor import PDFProcessor
from app.schemas.chat_schemas import ChatResponse, Source
from app.models.chat_history import ChatHistory


class ChatService:
    """Service for handling chat/Q&A functionality"""
    
    def __init__(self, db: Session):
        self.db = db
        self.claude_service = ClaudeService()
        self.interactive_claude_service = InteractiveClaudeService()
        
        # Initialize Gemini service if API key is available
        gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCEPAGmLnxEpJwGMrsJ6qQq__0Nwt0LDOw")
        try:
            self.gemini_service = GeminiService(api_key=gemini_api_key)
            self.use_gemini = True
            logger.info("Gemini service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini service: {e}")
            self.gemini_service = None
            self.use_gemini = False
        
        self.document_service = DocumentService(db)
        self.pdf_processor = PDFProcessor()
        # Redis will be added later
        self.cache = {}
        # Feature flag for interactive mode (disabled when using Gemini)
        self.use_interactive_mode = False  # Disabled since we're using Gemini as default
    
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
            
            # Determine if we should use Claude (for comparisons or complex queries)
            use_claude = False
            
            # Check if this is a comparison question
            if "비교" in question or any(keyword in question for keyword in ["설로인", "우나스텔라"]):
                use_claude = True
                logger.info("Detected comparison or complex query, will use Claude")
            
            # Use Gemini as default if available and not complex query
            if self.use_gemini and self.gemini_service and not use_claude:
                logger.info("Using Gemini Pro for processing")
                
                # Find relevant documents
                document, pdf_content = self.document_service.get_document_for_question(question)
                
                # Prepare text context for Gemini
                context_text = ""
                sources = []
                
                if document and pdf_content:
                    # Extract text from PDF for Gemini (limitation: can't process PDF directly)
                    try:
                        from app.services.pdf_processor import PDFProcessor
                        processor = PDFProcessor()
                        text_content = processor.extract_text_from_pdf(pdf_content)
                        
                        # Check if PDF is image-based (scanned)
                        if text_content and "스캔된 이미지 문서" in text_content:
                            logger.warning(f"PDF is image-based, falling back to Claude for {document.company_name}")
                            use_claude = True
                        elif text_content and len(text_content.strip()) > 100:
                            context_text = f"[{document.company_name} - {document.year}년 {document.doc_type}]\n{text_content[:5000]}"  # Limit text length
                            sources.append(Source(
                                type="file",
                                name=f"{document.company_name}_{document.year}_{document.doc_type}.pdf",
                                url=f"/api/documents/download/{document.id}"
                            ))
                        else:
                            logger.warning(f"Insufficient text extracted from PDF, falling back to Claude")
                            use_claude = True
                    except Exception as e:
                        logger.warning(f"Failed to extract text from PDF: {e}")
                        use_claude = True
                
                # If still using Gemini, proceed
                if not use_claude:
                    # Call Gemini API
                    result = await self.gemini_service.ask_simple_question(
                        question=question,
                        context=context_text if context_text else None
                    )
                    
                    processing_time = result.get("processing_time", time.time() - start_time)
                    
                    response = ChatResponse(
                        answer=result["answer"],
                        sources=sources,
                        processing_time=processing_time,
                        metadata={
                            "model_used": result["model"],
                            "token_usage": result.get("usage", {}),
                            "complexity": result.get("complexity", "simple"),
                            "llm_provider": "gemini"
                        }
                    )
                    
                    # Cache and save to history
                    self._cache_response(cache_key, response.model_dump())
                    self._save_to_history(
                        user_id=user_id,
                        question=question,
                        answer=result["answer"],
                        sources=[s.model_dump() for s in sources],
                        context=context,
                        metadata=result
                    )
                    
                    return response
            
            # Check if this is a comparison question or has multiple companies
            companies = []
            for company in ["마인이스", "설로인", "우나스텔라"]:
                if company in question:
                    companies.append(company)
            
            logger.info(f"Found companies in question: {companies}")
            
            # If we have multiple companies or "비교" keyword, treat as comparison
            if len(companies) >= 2 or "비교" in question:
                logger.info(f"Processing as comparison question with companies: {companies}")
                # Handle multiple company comparison
                year = self.document_service.extract_year_from_question(question)
                if not year:
                    year = 2024
                
                logger.info(f"Extracted year: {year}")
                
                # Collect documents for all companies
                documents_info = []
                doc_ids = []  # Keep track of document IDs for sources
                for company in companies:
                    documents = self.document_service.find_relevant_documents(company, year)
                    logger.info(f"Found {len(documents)} documents for {company} in year {year}")
                    if documents:
                        doc = documents[0]
                        try:
                            pdf_content = self.document_service.read_pdf_content(doc.file_path)
                            documents_info.append({
                                "company": company,
                                "year": doc.year,
                                "doc_type": doc.doc_type,
                                "content": pdf_content
                            })
                            doc_ids.append((doc.id, company, doc.year, doc.doc_type))
                            logger.info(f"Successfully loaded PDF for {company}")
                        except Exception as e:
                            logger.error(f"Error reading PDF for {company}: {e}")
                
                if len(documents_info) >= 2:
                    # Call Claude with multiple PDFs
                    result = await self.claude_service.analyze_multiple_pdfs_with_question(
                        documents_info=documents_info,
                        question=question
                    )
                    
                    processing_time = time.time() - start_time
                    sources = [
                        Source(
                            type="file",
                            name=f"{company}_{year}_{doc_type}.pdf",
                            url=f"/api/documents/download/{doc_id}"
                        )
                        for doc_id, company, year, doc_type in doc_ids
                    ]
                    
                    response = ChatResponse(
                        answer=result["answer"],
                        sources=sources,
                        processing_time=processing_time,
                        metadata={
                            "model_used": result["model_used"],
                            "token_usage": result["usage"],
                            "estimated_cost": self.claude_service.estimate_cost(result["usage"], result["model_used"]),
                            "comparison": True,
                            "companies": companies
                        }
                    )
                    
                    # Cache and save to history
                    self._cache_response(cache_key, response.model_dump())
                    self._save_to_history(
                        user_id=user_id,
                        question=question,
                        answer=result["answer"],
                        sources=[s.model_dump() for s in sources],
                        context=context,
                        metadata=result
                    )
                    
                    return response
                else:
                    logger.warning(f"Not enough documents found for comparison. Found: {len(documents_info)}")
                    return ChatResponse(
                        answer=f"죄송합니다. 비교에 필요한 문서를 충분히 찾지 못했습니다. {companies} 회사들의 {year}년 재무제표를 확인할 수 없습니다.",
                        sources=[],
                        processing_time=time.time() - start_time
                    )
            
            # Find relevant document for the question (single company)
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
                sources=[
                    Source(
                        type="file",
                        name=f"{document.company_name}_{document.year}_{document.doc_type}.pdf",
                        url=f"/api/documents/download/{document.id}"
                    )
                ],
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
                sources=[s.model_dump() for s in response.sources],
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
        sources: List[Dict[str, Any]],
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