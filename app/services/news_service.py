"""
News service for managing news articles
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import json
import chromadb
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.news import News
from app.schemas.news_schemas import NewsResponse
from app.core.embedding_client import EmbeddingClient
from app.core.config import settings


class NewsService:
    """Service for managing news articles"""
    
    def __init__(
        self,
        chromadb_client: chromadb.Client,
        embedding_client: EmbeddingClient
    ):
        self.chromadb_client = chromadb_client
        self.embedding_client = embedding_client
        
        # Get or create collection
        try:
            self.collection = self.chromadb_client.get_collection(
                name=settings.CHROMA_COLLECTION_NAME
            )
        except:
            self.collection = self.chromadb_client.create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
    
    async def search_news(
        self,
        company_name: str,
        keyword: Optional[str],
        from_date: Optional[date],
        to_date: Optional[date],
        limit: int,
        db: AsyncSession
    ) -> List[NewsResponse]:
        """Search for news articles by criteria"""
        query = select(News).where(News.company_name == company_name)
        
        if keyword:
            # Search in title and content
            query = query.where(
                or_(
                    News.title.ilike(f"%{keyword}%"),
                    News.content.ilike(f"%{keyword}%")
                )
            )
        
        if from_date:
            query = query.where(News.published_date >= datetime.combine(from_date, datetime.min.time()))
        
        if to_date:
            query = query.where(News.published_date <= datetime.combine(to_date, datetime.max.time()))
        
        # Order by published date descending
        query = query.order_by(News.published_date.desc()).limit(limit)
        
        result = await db.execute(query)
        news_items = result.scalars().all()
        
        return [NewsResponse.model_validate(item) for item in news_items]
    
    async def get_news_by_id(
        self,
        news_id: int,
        db: AsyncSession
    ) -> Optional[NewsResponse]:
        """Get news article by ID"""
        result = await db.execute(
            select(News).where(News.id == news_id)
        )
        news_item = result.scalar_one_or_none()
        
        if news_item:
            return NewsResponse.model_validate(news_item)
        return None
    
    async def index_news_from_file(
        self,
        source_file: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Index news from a JSON file"""
        indexed_count = 0
        error_count = 0
        errors = []
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            if not isinstance(news_data, list):
                news_data = [news_data]
            
            logger.info(f"Found {len(news_data)} news items to index")
            
            for item in news_data:
                try:
                    # Validate required fields
                    if not all(k in item for k in ['company_name', 'title']):
                        raise ValueError("Missing required fields: company_name, title")
                    
                    # Parse date if provided
                    published_date = None
                    if 'published_date' in item:
                        published_date = datetime.fromisoformat(item['published_date'].replace('Z', '+00:00'))
                    
                    # Create news entry
                    news = News(
                        company_name=item['company_name'],
                        title=item['title'],
                        content=item.get('content'),
                        content_url=item.get('content_url'),
                        source=item.get('source'),
                        published_date=published_date
                    )
                    
                    db.add(news)
                    await db.commit()
                    await db.refresh(news)
                    
                    # Index to vector database
                    await self._index_news_content(news)
                    
                    indexed_count += 1
                    logger.info(f"Indexed news: {news.title[:50]}...")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Error indexing news item: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return {
                "indexed": indexed_count,
                "errors": error_count,
                "error_details": errors,
                "total_items": len(news_data)
            }
            
        except Exception as e:
            logger.error(f"Error reading news file: {str(e)}")
            raise
    
    async def _index_news_content(self, news: News):
        """Index news content to vector database"""
        try:
            # Combine title and content for indexing
            text_content = f"{news.title}\n\n{news.content or ''}"
            
            if not text_content.strip():
                logger.warning(f"No content to index for news ID {news.id}")
                return
            
            # For news, we might not need chunking if articles are short
            # But we'll chunk for consistency
            chunks = self.embedding_client.chunk_text(text_content, chunk_size=500)
            
            # Prepare data for vector database
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                doc_id = f"news_{news.id}_{i}_{uuid.uuid4().hex[:8]}"
                
                documents.append(chunk)
                metadatas.append({
                    "source": f"{news.source or 'Unknown'} - {news.title[:50]}",
                    "company": news.company_name,
                    "news_id": news.id,
                    "published_date": news.published_date.isoformat() if news.published_date else None,
                    "type": "news",
                    "chunk_index": i,
                    "url": news.content_url
                })
                ids.append(doc_id)
            
            # Generate embeddings and add to ChromaDB
            if documents:
                embeddings = await self.embedding_client.embed_documents(documents)
                
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"Added {len(documents)} chunks to vector database for news ID {news.id}")
                
        except Exception as e:
            logger.error(f"Error indexing news content: {str(e)}")
            raise
    
    async def create_news_article(
        self,
        company_name: str,
        title: str,
        content: Optional[str],
        content_url: Optional[str],
        source: Optional[str],
        published_date: Optional[datetime],
        db: AsyncSession
    ) -> NewsResponse:
        """Create a new news article"""
        news = News(
            company_name=company_name,
            title=title,
            content=content,
            content_url=content_url,
            source=source,
            published_date=published_date
        )
        
        db.add(news)
        await db.commit()
        await db.refresh(news)
        
        # Index to vector database
        await self._index_news_content(news)
        
        return NewsResponse.model_validate(news)