"""
Claude API Service
Handles all interactions with Anthropic Claude API
"""

import os
from typing import Optional, Dict, Any, List
import anthropic
from anthropic import Anthropic
import base64
from loguru import logger

from app.services.pdf_optimizer import PDFOptimizer, CompressionLevel
from app.services.pdf_splitter import PDFSplitter


class ClaudeService:
    """Service for interacting with Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude service with API key"""
        self.test_mode = os.getenv("CLAUDE_TEST_MODE", "false").lower() == "true"
        
        if self.test_mode:
            self.api_key = "test-mode-key"
            self.client = None
            logger.warning("Claude service running in TEST MODE - no API calls will be made")
        else:
            self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
            if not self.api_key:
                # Try to get from settings
                from app.core.config import settings
                self.api_key = settings.CLAUDE_API_KEY
                
            if not self.api_key:
                raise ValueError("Claude API key not found. Set CLAUDE_API_KEY environment variable.")
            
            self.client = Anthropic(api_key=self.api_key)
        
        # Model configurations
        self.models = {
            "opus": "claude-3-opus-20240229",
            "sonnet": "claude-3-5-sonnet-20241022",
            "haiku": "claude-3-haiku-20240307"
        }
        
        # Default model selection
        self.default_model = "sonnet"
        
        # Initialize PDF processors
        self.pdf_optimizer = PDFOptimizer()
        self.pdf_splitter = PDFSplitter()
    
    def select_model(self, question: str, complexity: str = "medium", for_pdf: bool = False) -> str:
        """Select appropriate Claude model based on question complexity
        
        Args:
            question: The question to analyze
            complexity: Complexity level (simple/medium/complex)
            for_pdf: Whether this is for PDF analysis (requires Sonnet or Opus)
        """
        # PDF analysis requires Sonnet or Opus (Haiku doesn't support PDF input)
        if for_pdf:
            return self.models["sonnet"]
        
        # For non-PDF queries, use complexity-based selection
        if complexity == "simple" or len(question) < 20:
            return self.models["haiku"]
        elif complexity == "complex" or "분석" in question or "비교" in question:
            return self.models["sonnet"]
        else:
            return self.models["sonnet"]
    
    async def analyze_pdf_with_question(
        self, 
        pdf_content: bytes,
        question: str,
        company_name: str,
        doc_year: int,
        doc_type: str,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send PDF content and question to Claude API
        
        Args:
            pdf_content: PDF file content as bytes
            question: User's question
            company_name: Name of the company
            doc_year: Year of the document
            doc_type: Type of document (재무제표, 사업보고서 등)
            model_override: Override model selection
            
        Returns:
            Dict containing answer and metadata
        """
        # Test mode - return dummy response
        if self.test_mode:
            logger.info(f"TEST MODE: Analyzing question for {company_name}")
            return {
                "answer": f"[테스트 모드] {company_name}의 {doc_year}년 {doc_type}에 대한 질문 '{question}'에 대한 답변입니다.\n\n매출액: 1,234억원\n영업이익: 234억원\n당기순이익: 123억원",
                "model_used": "test-mode",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150
                },
                "company": company_name,
                "document": f"{doc_year}년 {doc_type}"
            }
        
        try:
            # Process PDF before sending to Claude
            processed_pdf_content = pdf_content
            processing_info = {"optimized": False, "split": False}
            
            # Check if PDF needs optimization or splitting
            pdf_size_mb = len(pdf_content) / (1024 * 1024)
            logger.info(f"Original PDF size: {pdf_size_mb:.2f} MB")
            
            # Optimize if file is large but not too large to require splitting
            if 5 < pdf_size_mb <= 20:
                logger.info("Optimizing PDF...")
                processed_pdf_content, opt_metadata = self.pdf_optimizer.optimize_pdf(
                    pdf_content,
                    compression_level=CompressionLevel.EBOOK
                )
                processing_info["optimized"] = True
                processing_info["optimization_ratio"] = opt_metadata.get("compression_ratio", 1.0)
                logger.info(f"Optimized PDF size: {len(processed_pdf_content) / (1024 * 1024):.2f} MB")
            
            # Check if splitting is needed
            split_files, split_metadata = self.pdf_splitter.check_and_split(
                processed_pdf_content,
                f"{company_name}_{doc_year}_{doc_type}.pdf"
            )
            
            if split_metadata["split_performed"]:
                processing_info["split"] = True
                processing_info["split_count"] = split_metadata["split_count"]
                logger.warning(f"PDF was split into {split_metadata['split_count']} parts")
                
                # For now, we'll use the first part and notify about the split
                # In a production system, you might want to process all parts
                processed_pdf_content = split_files[0]["content"]
                
                # Add a note about the split to the question
                question = f"{question}\n\n[참고: 문서가 크기 제한으로 인해 {split_metadata['split_count']}개 부분으로 분할되었습니다. 현재 첫 번째 부분을 분석 중입니다.]"
            
            # Convert PDF to base64
            pdf_base64 = base64.b64encode(processed_pdf_content).decode('utf-8')
            
            # Select model - always use PDF-capable model for PDF analysis
            model = model_override or self.select_model(question, for_pdf=True)
            
            # Construct prompt
            system_prompt = f"""당신은 한국 투자 포트폴리오 기업의 재무 문서를 분석하는 전문가입니다.
            
주어진 {company_name}의 {doc_year}년 {doc_type}를 분석하여 사용자의 질문에 정확하게 답변해주세요.

답변 시 주의사항:
1. 문서에 있는 정보만을 기반으로 답변하세요
2. 구체적인 숫자나 수치가 있다면 반드시 포함하세요
3. 답변의 근거가 되는 페이지나 섹션을 언급하세요
4. 찾을 수 없는 정보는 솔직하게 "문서에서 찾을 수 없습니다"라고 답하세요
5. 모든 금액은 원화 단위로, 천 단위 구분자를 사용하여 표시하세요 (예: 1,234,567원)"""

            # Use different approach based on model capability
            logger.info(f"Processing PDF for {company_name} - {doc_year} {doc_type} with model: {model}")
            
            # Only Sonnet and Opus support PDF input
            if model in [self.models["sonnet"], self.models["opus"]]:
                # Use beta API with PDF document
                message = self.client.beta.messages.create(
                    model=model,
                    max_tokens=4000,
                    temperature=0.1,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": pdf_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": f"위 {company_name}의 {doc_year}년 {doc_type} 문서를 분석하여 다음 질문에 답변해주세요:\n\n{question}\n\n답변 시 문서에 있는 구체적인 수치와 내용을 인용해주세요."
                                }
                            ]
                        }
                    ]
                )
            else:
                # Fallback for Haiku model
                user_prompt = f"""다음은 {company_name}의 {doc_year}년 {doc_type} 문서에 대한 질문입니다.

질문: {question}

이 문서는 PDF 형식으로 저장되어 있으며, 일반적으로 다음과 같은 정보를 포함합니다:
- 재무상태표 (자산, 부채, 자본)
- 손익계산서 (매출, 영업이익, 당기순이익)
- 현금흐름표
- 주요 사업 내용 및 성과

질문에 대해 구체적이고 정확한 답변을 제공해주세요."""
                
                message = self.client.messages.create(
                    model=model,
                    max_tokens=4000,
                    temperature=0.1,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )
            
            # Extract response
            answer = message.content[0].text if message.content else "응답을 생성할 수 없습니다."
            
            # Log the actual response for debugging
            logger.info(f"Claude API Response: {answer[:200]}...")
            logger.debug(f"Full Claude response: {message}")
            
            response = {
                "answer": answer,
                "model_used": model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens
                },
                "company": company_name,
                "document": f"{doc_year}년 {doc_type}",
                "pdf_processing": processing_info
            }
            
            # Add warning if document was split
            if processing_info.get("split"):
                response["warning"] = f"문서가 {processing_info['split_count']}개로 분할되어 첫 번째 부분만 분석되었습니다."
            
            return response
            
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit error: {e}")
            raise Exception("API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise Exception(f"API 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Claude service: {e}")
            raise Exception(f"예상치 못한 오류가 발생했습니다: {str(e)}")
    
    async def analyze_multiple_pdfs_with_question(
        self,
        documents_info: List[Dict[str, Any]],
        question: str,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple PDFs together for comparison
        
        Args:
            documents_info: List of dicts with company, content, year, doc_type
            question: User's comparison question
            model_override: Override model selection
            
        Returns:
            Dict containing comparative analysis
        """
        if self.test_mode:
            return {
                "answer": "[테스트 모드] 여러 회사 비교 분석 결과입니다.",
                "model_used": "test-mode",
                "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150}
            }
        
        try:
            # Always use Sonnet for PDF analysis
            model = model_override or self.models["sonnet"]
            
            # Prepare system prompt
            companies = [doc["company"] for doc in documents_info]
            year = documents_info[0]["year"] if documents_info else 2024
            
            system_prompt = f"""당신은 한국 투자 포트폴리오 기업의 재무 문서를 비교 분석하는 전문가입니다.

{len(companies)}개 회사({', '.join(companies)})의 {year}년 재무제표를 비교 분석하여 사용자의 질문에 답변해주세요.

답변 시 주의사항:
1. 각 회사의 구체적인 수치를 명시하여 비교하세요
2. 성장률, 비율 등을 계산하여 제시하세요
3. 표 형식으로 정리하면 더 좋습니다
4. 모든 금액은 원화 단위로 천 단위 구분자를 사용하세요
5. 각 회사의 특징과 차이점을 명확히 설명하세요"""

            # Prepare content list
            content_list = []
            
            for i, doc_info in enumerate(documents_info):
                company = doc_info["company"]
                pdf_base64 = base64.b64encode(doc_info["content"]).decode('utf-8')
                
                # Add document
                content_list.append({
                    "type": "text",
                    "text": f"=== {company} {doc_info['year']}년 {doc_info['doc_type']} ==="
                })
                
                content_list.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_base64
                    }
                })
            
            # Add the comparison question
            content_list.append({
                "type": "text",
                "text": f"\n위 {len(companies)}개 회사의 재무제표를 비교하여 다음 질문에 답변해주세요:\n\n{question}"
            })
            
            # Call Claude API
            logger.info(f"Comparing {len(companies)} companies with Claude")
            
            message = self.client.beta.messages.create(
                model=model,
                max_tokens=4000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content_list
                    }
                ]
            )
            
            answer = message.content[0].text if message.content else "응답을 생성할 수 없습니다."
            
            return {
                "answer": answer,
                "model_used": model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens
                },
                "companies": companies,
                "year": year
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_multiple_pdfs: {e}")
            raise
    
    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Estimate API cost based on token usage"""
        # Approximate costs per 1M tokens (as of 2024)
        costs = {
            self.models["opus"]: {"input": 15.0, "output": 75.0},
            self.models["sonnet"]: {"input": 3.0, "output": 15.0},
            self.models["haiku"]: {"input": 0.25, "output": 1.25}
        }
        
        model_costs = costs.get(model, costs[self.models["sonnet"]])
        
        input_cost = (usage["input_tokens"] / 1_000_000) * model_costs["input"]
        output_cost = (usage["output_tokens"] / 1_000_000) * model_costs["output"]
        
        return input_cost + output_cost