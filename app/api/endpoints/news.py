"""
News search endpoints
"""

from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.news_schemas import NewsResponse, NewsSearchQuery
from app.services.news_service import NewsService
from app.api.deps import get_news_service

router = APIRouter()


@router.get("/search", response_model=List[NewsResponse])
async def search_news(
    company: str = Query(..., description="Company name to search for"),
    keyword: Optional[str] = Query(None, description="Additional keyword to filter"),
    from_date: Optional[date] = Query(None, description="Start date for search"),
    to_date: Optional[date] = Query(None, description="End date for search"),
    limit: int = Query(20, ge=1, le=100),
    news_service: NewsService = Depends(get_news_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for news articles by company and optional filters
    """
    try:
        news_items = await news_service.search_news(
            company_name=company,
            keyword=keyword,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            db=db
        )
        return news_items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching news: {str(e)}"
        )


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_article(
    news_id: int,
    news_service: NewsService = Depends(get_news_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific news article by ID
    """
    article = await news_service.get_news_by_id(news_id, db)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"News article with ID {news_id} not found"
        )
    return article


@router.post("/index")
async def index_news(
    source_file: str,
    news_service: NewsService = Depends(get_news_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Index news from a source file (admin function)
    """
    # TODO: Add authentication/authorization
    try:
        result = await news_service.index_news_from_file(source_file, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing news: {str(e)}"
        )