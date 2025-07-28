"""
Chat endpoints for Q&A functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.db.session import get_db
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.api.deps import get_chat_service

router = APIRouter()


@router.delete("/cache")
async def clear_cache(db: Session = Depends(get_db)):
    """Clear the chat cache"""
    chat_service = ChatService(db)
    chat_service.cache.clear()
    return {"message": "Cache cleared successfully", "status": "success"}


@router.post("/", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    db: Session = Depends(get_db)
):
    """
    Process a user question and return an AI-generated response
    """
    try:
        logger.info(f"Received chat request: {request.question}")
        response = await chat_service.process_query(
            question=request.question,
            context=request.context
        )
        logger.info("Chat response generated successfully")
        return response
    except Exception as e:
        logger.error(f"Error in create_chat_completion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get chat history (placeholder for now - requires authentication)
    """
    # TODO: Implement after authentication is set up
    return {
        "message": "Chat history endpoint - requires authentication",
        "limit": limit,
        "offset": offset
    }