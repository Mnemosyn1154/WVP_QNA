"""
Document management endpoints
"""

from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document_schemas import DocumentResponse, DocumentSearchQuery
from app.services.document_service import DocumentService
from app.api.deps import get_document_service

router = APIRouter()


@router.get("/search", response_model=List[DocumentResponse])
async def search_documents(
    company: str = Query(..., description="Company name to search for"),
    year: Optional[int] = Query(None, description="Year of the document"),
    doc_type: Optional[str] = Query(None, description="Document type (사업보고서, 반기보고서, 분기보고서)"),
    limit: int = Query(10, ge=1, le=100),
    document_service: DocumentService = Depends(get_document_service),
    db: Session = Depends(get_db)
):
    """
    Search for financial documents by company, year, and type
    """
    try:
        documents = document_service.search_documents(
            company_name=company,
            year=year,
            doc_type=doc_type,
            limit=limit,
            db=db
        )
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    document_service: DocumentService = Depends(get_document_service),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    document = document_service.get_document_by_id(document_id, db)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return document


@router.post("/index")
async def index_documents(
    directory_path: str,
    document_service: DocumentService = Depends(get_document_service),
    db: Session = Depends(get_db)
):
    """
    Index documents from a directory (admin function)
    """
    # TODO: Add authentication/authorization
    try:
        result = document_service.index_documents_from_directory(directory_path, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing documents: {str(e)}"
        )


@router.get("/download/{document_id}")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Download a financial document by ID
    """
    from app.models.financial_doc import FinancialDoc
    
    # Get document metadata directly
    document = db.query(FinancialDoc).filter(FinancialDoc.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Check if file exists
    # Handle both absolute and relative paths
    file_path = Path(document.file_path)
    if not file_path.is_absolute():
        # If relative, make it relative to project root
        file_path = Path.cwd() / file_path
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found on server: {file_path}"
        )
    
    # Generate filename for download
    filename = f"{document.company_name}_{document.year}_{document.doc_type}.pdf"
    
    # Return file response
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )