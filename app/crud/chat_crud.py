"""
CRUD operations for chat history
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_history import ChatHistory


class ChatCRUD:
    """CRUD operations for chat history"""
    
    async def create_chat_history(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        question: str,
        answer: str,
        context: Dict[str, Any]
    ) -> ChatHistory:
        """Create a new chat history entry"""
        chat_entry = ChatHistory(
            user_id=user_id,
            question=question,
            answer=answer,
            context=context
        )
        
        db.add(chat_entry)
        await db.commit()
        await db.refresh(chat_entry)
        
        return chat_entry
    
    async def get_chat_history(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatHistory]:
        """Get chat history with optional user filter"""
        query = select(ChatHistory)
        
        if user_id:
            query = query.where(ChatHistory.user_id == user_id)
        
        query = query.order_by(desc(ChatHistory.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_chat_by_id(
        self,
        db: AsyncSession,
        chat_id: int
    ) -> Optional[ChatHistory]:
        """Get a specific chat entry by ID"""
        result = await db.execute(
            select(ChatHistory).where(ChatHistory.id == chat_id)
        )
        return result.scalar_one_or_none()