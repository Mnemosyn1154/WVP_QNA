"""
Comparison endpoints for multiple companies
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from loguru import logger

from app.db.session import get_db
from app.services.claude_service import ClaudeService
from app.services.document_service import DocumentService
from app.schemas.chat_schemas import ChatResponse

router = APIRouter()


@router.post("/companies", response_model=ChatResponse)
async def compare_companies(
    request: Dict,
    db: Session = Depends(get_db)
):
    """
    Compare financial metrics across multiple companies
    """
    try:
        question = request.get("question", "")
        companies = request.get("companies", [])
        
        logger.info(f"Comparing companies: {companies} with question: {question}")
        
        # Initialize services
        claude_service = ClaudeService()
        document_service = DocumentService(db)
        
        # Extract companies from question if not provided
        if not companies:
            # Try to extract multiple companies from question
            known_companies = ["마인이스", "우나스텔라", "설로인"]
            companies = [c for c in known_companies if c in question]
        
        if len(companies) < 2:
            # Try to handle the comparison case
            if "비교" in question:
                companies = []
                for company in ["마인이스", "설로인", "우나스텔라"]:
                    if company in question:
                        companies.append(company)
        
        if not companies:
            raise HTTPException(
                status_code=400,
                detail="비교할 회사를 찾을 수 없습니다. 회사명을 명시해주세요."
            )
        
        # Extract year from question
        year = document_service.extract_year_from_question(question)
        if not year:
            year = 2024  # Default to most recent year
        
        # Collect documents and content for all companies
        company_data = {}
        for company in companies:
            documents = document_service.find_relevant_documents(company, year)
            if documents:
                doc = documents[0]
                try:
                    pdf_content = document_service.read_pdf_content(doc.file_path)
                    company_data[company] = {
                        "document": doc,
                        "content": pdf_content
                    }
                except Exception as e:
                    logger.error(f"Error reading PDF for {company}: {e}")
        
        if not company_data:
            raise HTTPException(
                status_code=404,
                detail="요청하신 회사들의 문서를 찾을 수 없습니다."
            )
        
        # Prepare combined prompt for Claude
        combined_prompt = f"다음 {len(company_data)}개 회사의 {year}년 재무제표를 비교 분석해주세요:\n\n"
        
        # Send all PDFs to Claude for comparison
        documents_info = []
        for company, data in company_data.items():
            doc = data["document"]
            documents_info.append({
                "company": company,
                "year": doc.year,
                "doc_type": doc.doc_type,
                "content": data["content"]
            })
        
        # Call Claude with all documents
        result = await claude_service.analyze_multiple_pdfs_with_question(
            documents_info=documents_info,
            question=question
        )
        
        # Prepare response
        sources = [f"{company} {year}년 재무제표" for company in company_data.keys()]
        
        return ChatResponse(
            answer=result["answer"],
            sources=sources,
            processing_time=result.get("processing_time", 0),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_companies: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"비교 처리 중 오류가 발생했습니다: {str(e)}"
        )