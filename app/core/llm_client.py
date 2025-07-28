"""
LLM Client for Claude API integration
"""

from typing import Optional, Dict, Any
import anthropic
from loguru import logger

from app.core.config import settings


class LLMClient:
    """Client for interacting with Claude API"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
        self.model_routing = {
            "simple": settings.CLAUDE_MODEL_SIMPLE,
            "standard": settings.CLAUDE_MODEL_STANDARD,
            "advanced": settings.CLAUDE_MODEL_ADVANCED
        }
    
    def select_model(self, question_type: str, complexity: float = 0.5) -> str:
        """
        Select appropriate Claude model based on question type and complexity
        
        Args:
            question_type: Type of question (simple_lookup, analysis, complex)
            complexity: Complexity score from 0 to 1
        
        Returns:
            Model name to use
        """
        if question_type == "simple_lookup":
            return self.model_routing["simple"]
        elif complexity > 0.7 or question_type == "complex_analysis":
            return self.model_routing["advanced"]
        else:
            return self.model_routing["standard"]
    
    async def generate_text(
        self,
        prompt: str,
        question_type: str = "standard",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using Claude API
        
        Args:
            prompt: The prompt to send to Claude
            question_type: Type of question for model selection
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            **kwargs: Additional parameters for the API
        
        Returns:
            Generated text response
        """
        model = self.select_model(question_type)
        
        try:
            logger.info(f"Calling Claude API with model: {model}")
            
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                **kwargs
            )
            
            response_text = message.content[0].text
            logger.info(f"Successfully generated response with {len(response_text)} characters")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise
    
    async def analyze_document(
        self,
        document_content: str,
        question: str,
        doc_type: str = "financial_report"
    ) -> Dict[str, Any]:
        """
        Analyze a document with a specific question
        
        Args:
            document_content: Content of the document
            question: Question about the document
            doc_type: Type of document
        
        Returns:
            Analysis result with answer and extracted data
        """
        prompt = self._build_document_analysis_prompt(document_content, question, doc_type)
        
        response = await self.generate_text(
            prompt=prompt,
            question_type="complex_analysis",
            temperature=0.3  # Lower temperature for factual analysis
        )
        
        return {
            "answer": response,
            "doc_type": doc_type,
            "question": question
        }
    
    def _build_document_analysis_prompt(
        self,
        document_content: str,
        question: str,
        doc_type: str
    ) -> str:
        """Build prompt for document analysis"""
        
        if doc_type == "financial_report":
            return f"""You are an expert financial analyst helping an investment team.
            
Analyze the following financial document and answer the user's question.
Provide specific numbers and page references when available.
If the answer is not in the document, clearly state that.

Document:
{document_content}

User Question: {question}

Please provide a clear, concise answer with specific data points and sources."""
        
        else:
            return f"""You are an intelligent assistant analyzing documents.
            
Based on the following document, answer the user's question.
Be specific and cite relevant parts of the document.

Document:
{document_content}

User Question: {question}"""