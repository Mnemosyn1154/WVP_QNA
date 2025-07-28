"""
Embedding client for text vectorization
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.core.config import settings


class EmbeddingClient:
    """Client for generating text embeddings"""
    
    def __init__(self):
        """Initialize the embedding model"""
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded. Dimension: {self.embedding_dim}")
    
    async def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text
        
        Args:
            text: Single text string or list of texts
        
        Returns:
            Embedding vector(s) as list(s) of floats
        """
        try:
            if isinstance(text, str):
                # Single text
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            else:
                # Multiple texts
                embeddings = self.model.encode(text, convert_to_numpy=True)
                return embeddings.tolist()
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def embed_documents(self, documents: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple documents with batching
        
        Args:
            documents: List of document texts
            batch_size: Batch size for processing
        
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            logger.info(f"Processing embedding batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            batch_embeddings = await self.embed_text(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def chunk_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (default from settings)
            chunk_overlap: Overlap between chunks (default from settings)
        
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to find a good breaking point (end of sentence)
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.8:  # Only break if we're past 80% of chunk
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        return chunks
    
    async def similarity_score(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score between 0 and 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        # Convert to 0-1 range
        return float((cosine_sim + 1) / 2)