"""
Interactive Claude Service with Dynamic Document Loading
"""

import os
from typing import Optional, Dict, Any, List, Tuple
from anthropic import Anthropic
import base64
from loguru import logger
import asyncio
import time

from app.core.llm_protocol import LLMProtocol, DocumentRequest, DocumentRequestType
from app.services.document_service import DocumentService
from app.services.pdf_optimizer import PDFOptimizer
from sqlalchemy.orm import Session


class InteractiveClaudeService:
    """
    Enhanced Claude service that supports interactive document requests
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize interactive Claude service"""
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            from app.core.config import settings
            self.api_key = settings.CLAUDE_API_KEY
            
        self.client = Anthropic(api_key=self.api_key)
        self.protocol = LLMProtocol()
        self.pdf_optimizer = PDFOptimizer()
        
        # Model to use
        self.model = "claude-3-5-sonnet-20241022"
        
    async def interactive_chat(
        self,
        question: str,
        db: Session,
        initial_context: Optional[List[Dict[str, Any]]] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Interactive chat that allows Claude to request additional documents
        
        Args:
            question: User's question
            db: Database session
            initial_context: Initial documents to provide
            max_iterations: Maximum conversation iterations
            
        Returns:
            Dict with final answer and metadata
        """
        # Initialize services
        document_service = DocumentService(db)
        
        # Reset protocol state
        self.protocol.reset()
        
        # Conversation history
        messages = []
        
        # Provided documents tracking
        provided_docs = []
        
        # Initial context if provided
        context_str = ""
        if initial_context:
            context_str = self.protocol.format_document_context(initial_context)
            provided_docs.extend(initial_context)
        
        # Metrics
        total_tokens = 0
        start_time = time.time()
        iterations = 0
        
        # Initial message
        initial_content = []
        if context_str:
            initial_content.append({
                "type": "text",
                "text": f"다음 문서들을 참고하여 질문에 답변해주세요:\n\n{context_str}\n\n질문: {question}"
            })
        else:
            initial_content.append({
                "type": "text", 
                "text": f"질문: {question}\n\n필요한 문서가 있다면 요청해주세요."
            })
        
        messages.append({
            "role": "user",
            "content": initial_content
        })
        
        # Interactive conversation loop
        final_answer = None
        
        while iterations < max_iterations:
            iterations += 1
            logger.info(f"Iteration {iterations}: Sending request to Claude")
            
            try:
                # Format messages for Claude API
                formatted_messages = []
                for msg in messages:
                    if msg["role"] == "user":
                        # Check if content includes PDF documents
                        if isinstance(msg["content"], list):
                            formatted_content = []
                            for item in msg["content"]:
                                if item["type"] == "text":
                                    # Check if text contains document references
                                    if "content_type" in str(item):
                                        # This is a document reference, need to format it
                                        continue
                                    else:
                                        formatted_content.append(item)
                            
                            # Add any PDF documents
                            for doc in provided_docs:
                                if doc.get("content_type") == "pdf_base64":
                                    formatted_content.append({
                                        "type": "document",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "application/pdf",
                                            "data": doc["content"]
                                        }
                                    })
                            
                            formatted_messages.append({
                                "role": "user",
                                "content": formatted_content if formatted_content else msg["content"]
                            })
                        else:
                            formatted_messages.append(msg)
                    else:
                        formatted_messages.append(msg)
                
                # Call Claude API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    temperature=0.1,
                    system=self.protocol.SYSTEM_PROMPT,
                    messages=formatted_messages
                )
                
                # Extract response text
                response_text = response.content[0].text if response.content else ""
                
                # Update token count
                total_tokens += response.usage.input_tokens + response.usage.output_tokens
                
                # Parse for document requests
                doc_requests = self.protocol.parse_response_for_requests(response_text)
                
                if not doc_requests:
                    # No more requests, this is the final answer
                    final_answer = self.protocol.extract_final_answer(response_text)
                    logger.info("No document requests found, conversation complete")
                    break
                
                # Process document requests
                logger.info(f"Found {len(doc_requests)} document requests")
                new_documents = await self._fulfill_document_requests(
                    doc_requests, 
                    document_service
                )
                
                if not new_documents:
                    # No new documents found, use current response as final
                    final_answer = self.protocol.extract_final_answer(response_text)
                    logger.info("No new documents found, using current response")
                    break
                
                # Add new documents to context
                provided_docs.extend(new_documents)
                new_context = self.protocol.format_document_context(new_documents)
                
                # Add assistant response to history
                messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                
                # Add new context as user message
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f"요청하신 문서를 찾았습니다:\n\n{new_context}\n\n이제 이 정보를 포함하여 질문에 답변해주세요."
                    }]
                })
                
            except Exception as e:
                logger.error(f"Error in iteration {iterations}: {e}")
                if iterations == 1:
                    raise  # Re-raise if first iteration fails
                # Otherwise use last response
                break
        
        # Calculate final metrics
        processing_time = time.time() - start_time
        
        # Prepare response
        return {
            "answer": final_answer or "죄송합니다. 답변을 생성할 수 없습니다.",
            "model_used": self.model,
            "usage": {
                "total_tokens": total_tokens,
                "iterations": iterations
            },
            "processing_time": processing_time,
            "documents_provided": len(provided_docs),
            "provided_documents": [
                {
                    "company": doc.get("company_name"),
                    "year": doc.get("year"),
                    "type": doc.get("doc_type", doc.get("type"))
                }
                for doc in provided_docs
            ]
        }
    
    async def _fulfill_document_requests(
        self,
        requests: List[DocumentRequest],
        document_service: DocumentService
    ) -> List[Dict[str, Any]]:
        """
        Fulfill document requests from LLM
        
        Args:
            requests: List of document requests
            document_service: Document service instance
            
        Returns:
            List of fulfilled documents with content
        """
        documents = []
        
        for request in requests:
            try:
                if request.request_type == DocumentRequestType.FINANCIAL_REPORT:
                    # Single company financial report
                    docs = document_service.find_relevant_documents(
                        company=request.company_name,
                        year=request.year,
                        doc_type=request.doc_type
                    )
                    
                    if docs:
                        doc = docs[0]
                        pdf_content = document_service.read_pdf_content(doc.file_path)
                        
                        # Always optimize PDFs to reduce size
                        logger.info(f"Original PDF size for {doc.company_name}: {len(pdf_content) / 1024 / 1024:.2f} MB")
                        
                        # Check if PDF is image-based (scanned)
                        is_scanned = self.pdf_optimizer.is_image_based_pdf(pdf_content)
                        
                        # Use aggressive compression for image-based PDFs
                        from app.services.pdf_optimizer import CompressionLevel
                        if is_scanned:
                            logger.warning(f"PDF for {doc.company_name} is image-based, using ultra-low compression")
                            pdf_content, opt_metadata = self.pdf_optimizer.optimize_pdf(
                                pdf_content,
                                compression_level=CompressionLevel.ULTRA_LOW,
                                target_size_mb=1.0
                            )
                            logger.info(f"Optimized image-based PDF to: {len(pdf_content) / 1024 / 1024:.2f} MB")
                        elif len(pdf_content) > 5 * 1024 * 1024:  # 5MB
                            pdf_content, opt_metadata = self.pdf_optimizer.optimize_pdf(
                                pdf_content,
                                compression_level=CompressionLevel.SCREEN,
                                target_size_mb=2.0
                            )
                            logger.info(f"Optimized PDF to: {len(pdf_content) / 1024 / 1024:.2f} MB")
                        elif len(pdf_content) > 2 * 1024 * 1024:  # 2MB
                            pdf_content, opt_metadata = self.pdf_optimizer.optimize_pdf(
                                pdf_content,
                                compression_level=CompressionLevel.EBOOK
                            )
                            logger.info(f"Optimized PDF to: {len(pdf_content) / 1024 / 1024:.2f} MB")
                        
                        # If still too large, warn but continue
                        if len(pdf_content) > 3 * 1024 * 1024:  # 3MB after optimization
                            logger.warning(f"PDF still large for {doc.company_name}: {len(pdf_content) / 1024 / 1024:.2f} MB")
                        
                        documents.append({
                            "type": "financial_report",
                            "company_name": doc.company_name,
                            "year": doc.year,
                            "doc_type": doc.doc_type,
                            "content": base64.b64encode(pdf_content).decode('utf-8'),
                            "content_type": "pdf_base64"
                        })
                        
                elif request.request_type == DocumentRequestType.COMPARE:
                    # Multiple companies comparison
                    for company in request.companies or []:
                        docs = document_service.find_relevant_documents(
                            company=company,
                            year=request.year,
                            doc_type=request.doc_type
                        )
                        
                        if docs:
                            doc = docs[0]
                            pdf_content = document_service.read_pdf_content(doc.file_path)
                            
                            if len(pdf_content) > 10 * 1024 * 1024:
                                pdf_content, _ = self.pdf_optimizer.optimize_pdf(pdf_content)
                            
                            documents.append({
                                "type": "financial_report",
                                "company_name": doc.company_name,
                                "year": doc.year,
                                "doc_type": doc.doc_type,
                                "content": base64.b64encode(pdf_content).decode('utf-8'),
                                "content_type": "pdf_base64"
                            })
                
                elif request.request_type == DocumentRequestType.NEWS:
                    # News search (simplified for now)
                    logger.info(f"News search requested for {request.company_name}")
                    # TODO: Implement news search when news data is available
                    
            except Exception as e:
                logger.error(f"Error fulfilling document request: {e}")
                continue
        
        return documents
    
    def format_documents_for_claude(self, documents: List[Dict[str, Any]]) -> List[Dict]:
        """
        Format documents for Claude API input
        
        Args:
            documents: List of documents with metadata and content
            
        Returns:
            List of formatted content items for Claude
        """
        content_items = []
        
        for doc in documents:
            # Add metadata as text
            metadata_text = f"=== {doc.get('company_name')} {doc.get('year')}년 {doc.get('doc_type')} ==="
            content_items.append({
                "type": "text",
                "text": metadata_text
            })
            
            # Add document content
            if doc.get("content_type") == "pdf_base64":
                content_items.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": doc.get("content")
                    }
                })
            elif doc.get("content_type") == "text":
                content_items.append({
                    "type": "text",
                    "text": doc.get("content")
                })
        
        return content_items