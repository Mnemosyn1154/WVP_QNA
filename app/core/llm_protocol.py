"""
LLM Interactive Protocol for Dynamic Document Requests
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from loguru import logger


class DocumentRequestType(Enum):
    """Types of documents that LLM can request"""
    FINANCIAL_REPORT = "financial_report"
    NEWS = "news"
    COMPARE = "compare"
    TREND = "trend"


@dataclass
class DocumentRequest:
    """Structured document request from LLM"""
    request_type: DocumentRequestType
    company_name: Optional[str] = None
    companies: Optional[List[str]] = None  # For comparisons
    year: Optional[int] = None
    quarter: Optional[int] = None
    doc_type: Optional[str] = None
    keywords: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    

class LLMProtocol:
    """
    Handles the protocol for LLM to request additional documents dynamically
    """
    
    # System prompt that teaches Claude how to request documents
    SYSTEM_PROMPT = """당신은 한국 투자 포트폴리오 기업의 재무 문서를 분석하는 전문가입니다.

질문에 답변하기 위해 추가 문서가 필요한 경우, 다음 형식으로 요청할 수 있습니다:

<request_document>
{
  "type": "financial_report",
  "company_name": "회사명",
  "year": 2024,
  "doc_type": "재무제표"
}
</request_document>

여러 회사를 비교해야 할 경우:
<request_document>
{
  "type": "compare",
  "companies": ["회사1", "회사2"],
  "year": 2024,
  "doc_type": "재무제표"
}
</request_document>

뉴스를 검색해야 할 경우:
<request_document>
{
  "type": "news",
  "company_name": "회사명",
  "keywords": ["키워드1", "키워드2"],
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}
</request_document>

중요: 이미 제공된 문서는 다시 요청하지 마세요. 필요한 정보가 없을 때만 요청하세요."""

    def __init__(self):
        self.request_pattern = re.compile(
            r'<request_document>(.*?)</request_document>',
            re.DOTALL
        )
        self.provided_documents = set()  # Track what's already provided
        
    def parse_response_for_requests(self, response: str) -> List[DocumentRequest]:
        """
        Parse LLM response to find document requests
        
        Args:
            response: LLM's response text
            
        Returns:
            List of DocumentRequest objects
        """
        requests = []
        
        # Find all request tags
        matches = self.request_pattern.findall(response)
        
        for match in matches:
            try:
                # Parse JSON content
                request_data = json.loads(match.strip())
                
                # Create DocumentRequest object
                request_type = DocumentRequestType(request_data.get("type"))
                
                request = DocumentRequest(
                    request_type=request_type,
                    company_name=request_data.get("company_name"),
                    companies=request_data.get("companies"),
                    year=request_data.get("year"),
                    quarter=request_data.get("quarter"),
                    doc_type=request_data.get("doc_type"),
                    keywords=request_data.get("keywords"),
                    date_from=request_data.get("date_from"),
                    date_to=request_data.get("date_to")
                )
                
                # Check if we already provided this document
                doc_key = self._get_document_key(request)
                if doc_key not in self.provided_documents:
                    requests.append(request)
                    self.provided_documents.add(doc_key)
                else:
                    logger.debug(f"Skipping already provided document: {doc_key}")
                    
            except Exception as e:
                logger.error(f"Error parsing document request: {e}")
                continue
                
        return requests
    
    def _get_document_key(self, request: DocumentRequest) -> str:
        """Generate a unique key for a document request"""
        if request.request_type == DocumentRequestType.FINANCIAL_REPORT:
            return f"{request.company_name}_{request.year}_{request.doc_type}"
        elif request.request_type == DocumentRequestType.COMPARE:
            companies = "_".join(sorted(request.companies or []))
            return f"compare_{companies}_{request.year}_{request.doc_type}"
        elif request.request_type == DocumentRequestType.NEWS:
            return f"news_{request.company_name}_{request.date_from}_{request.date_to}"
        else:
            return str(request)
    
    def format_document_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format documents into context for LLM
        
        Args:
            documents: List of document metadata and content
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for doc in documents:
            if doc.get("type") == "financial_report":
                context_parts.append(f"""
<document>
<metadata>
회사: {doc.get('company_name')}
연도: {doc.get('year')}
문서 유형: {doc.get('doc_type')}
</metadata>
<content>
{doc.get('content', '')}
</content>
</document>
""")
            elif doc.get("type") == "news":
                context_parts.append(f"""
<news>
<metadata>
회사: {doc.get('company_name')}
제목: {doc.get('title')}
날짜: {doc.get('date')}
출처: {doc.get('source')}
</metadata>
<content>
{doc.get('content', '')}
</content>
</news>
""")
        
        return "\n".join(context_parts)
    
    def should_continue_conversation(self, requests: List[DocumentRequest], iteration: int) -> bool:
        """
        Determine if we should continue the conversation
        
        Args:
            requests: List of document requests from LLM
            iteration: Current iteration number
            
        Returns:
            True if should continue, False otherwise
        """
        # Limits to prevent infinite loops
        MAX_ITERATIONS = 5
        MAX_DOCUMENTS = 10
        
        if iteration >= MAX_ITERATIONS:
            logger.warning(f"Reached maximum iterations: {MAX_ITERATIONS}")
            return False
            
        if len(self.provided_documents) >= MAX_DOCUMENTS:
            logger.warning(f"Reached maximum documents: {MAX_DOCUMENTS}")
            return False
            
        return len(requests) > 0
    
    def extract_final_answer(self, response: str) -> str:
        """
        Extract the final answer from response, removing request tags
        
        Args:
            response: Full LLM response
            
        Returns:
            Clean answer without request tags
        """
        # Remove all request tags
        clean_response = self.request_pattern.sub('', response)
        
        # Clean up extra whitespace
        clean_response = re.sub(r'\n\s*\n', '\n\n', clean_response)
        
        return clean_response.strip()
    
    def reset(self):
        """Reset the protocol state for a new conversation"""
        self.provided_documents.clear()