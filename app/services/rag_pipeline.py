"""
RAG (Retrieval-Augmented Generation) Pipeline
"""

from typing import List, Tuple, Dict, Any, Optional
import chromadb
from loguru import logger

from app.core.llm_client import LLMClient
from app.core.embedding_client import EmbeddingClient
from app.core.config import settings


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for Q&A"""
    
    def __init__(
        self,
        chromadb_client: chromadb.Client,
        llm_client: LLMClient,
        embedding_client: EmbeddingClient
    ):
        self.chromadb_client = chromadb_client
        self.llm_client = llm_client
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
    
    async def generate_response(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Tuple[str, List[str]]:
        """
        Generate response using RAG pipeline
        
        Args:
            question: User's question
            context: Additional context
            top_k: Number of documents to retrieve
        
        Returns:
            Tuple of (answer, sources)
        """
        logger.info(f"Processing question: {question[:100]}...")
        
        # 1. Generate query embedding
        query_embedding = await self.embedding_client.embed_text(question)
        
        # 2. Retrieve relevant documents
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["documents"][0]:
            logger.warning("No relevant documents found")
            return await self._generate_no_context_response(question), []
        
        # 3. Extract documents and metadata
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        
        # 4. Build augmented prompt
        augmented_prompt = self._build_augmented_prompt(
            question=question,
            documents=documents,
            metadatas=metadatas,
            context=context
        )
        
        # 5. Generate response
        question_type = self._classify_question(question)
        answer = await self.llm_client.generate_text(
            prompt=augmented_prompt,
            question_type=question_type,
            temperature=0.3  # Lower temperature for factual responses
        )
        
        # 6. Extract sources
        sources = self._extract_sources(metadatas)
        
        logger.info(f"Generated response with {len(sources)} sources")
        
        return answer, sources
    
    def _build_augmented_prompt(
        self,
        question: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build augmented prompt with retrieved documents"""
        
        # Format documents with metadata
        formatted_docs = []
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            source = meta.get("source", f"Document {i+1}")
            formatted_doc = f"[{source}]\n{doc}"
            formatted_docs.append(formatted_doc)
        
        documents_text = "\n\n---\n\n".join(formatted_docs)
        
        # Build prompt
        prompt = f"""You are an intelligent assistant for an investment team analyzing portfolio companies.
You have access to financial reports, news articles, and other documents about these companies.

Based on the following documents, please answer the user's question.
Provide specific data points, numbers, and cite your sources.
If the answer is not in the provided documents, clearly state that you don't have enough information.

Retrieved Documents:
{documents_text}

User Question: {question}

Please provide a clear, concise, and accurate answer based on the documents above.
When citing information, reference the document source in square brackets."""
        
        # Add context if provided
        if context:
            prompt += f"\n\nAdditional Context: {context}"
        
        return prompt
    
    async def _generate_no_context_response(self, question: str) -> str:
        """Generate response when no relevant documents are found"""
        prompt = f"""You are an intelligent assistant for an investment team.
The user has asked a question, but no relevant documents were found in the database.

User Question: {question}

Please provide a helpful response explaining that you don't have the specific information requested,
and suggest what kind of documents or information would be needed to answer their question."""
        
        return await self.llm_client.generate_text(
            prompt=prompt,
            question_type="simple",
            temperature=0.7
        )
    
    def _classify_question(self, question: str) -> str:
        """Classify question type for model selection"""
        question_lower = question.lower()
        
        # Simple lookup patterns
        simple_patterns = [
            "얼마", "몇", "언제", "어디", "누구",
            "매출", "이익", "자산", "부채"
        ]
        
        # Complex analysis patterns
        complex_patterns = [
            "분석", "비교", "평가", "전망", "예측",
            "왜", "어떻게", "설명", "요약"
        ]
        
        if any(pattern in question_lower for pattern in simple_patterns):
            return "simple_lookup"
        elif any(pattern in question_lower for pattern in complex_patterns):
            return "complex_analysis"
        else:
            return "standard"
    
    def _extract_sources(self, metadatas: List[Dict[str, Any]]) -> List[str]:
        """Extract source references from metadata"""
        sources = []
        
        for meta in metadatas:
            source = meta.get("source", "Unknown")
            page = meta.get("page")
            
            if page:
                source_ref = f"{source} (p.{page})"
            else:
                source_ref = source
            
            if source_ref not in sources:
                sources.append(source_ref)
        
        return sources
    
    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add documents to the vector database"""
        logger.info(f"Adding {len(documents)} documents to vector database")
        
        # Generate embeddings
        embeddings = await self.embedding_client.embed_documents(documents)
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully added {len(documents)} documents")