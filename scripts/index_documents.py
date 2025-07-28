#!/usr/bin/env python3
"""
Index financial documents into the database and vector store
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.services.document_service import DocumentService
from app.core.embedding_client import EmbeddingClient
from app.core.config import settings
import chromadb
from chromadb.config import Settings as ChromaSettings


async def init_database():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


def get_chromadb_client() -> chromadb.Client:
    """Get ChromaDB client"""
    try:
        # For script, use HttpClient to connect to running ChromaDB
        return chromadb.HttpClient(
            host="localhost",
            port=8000,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    except Exception as e:
        logger.warning(f"Could not connect to ChromaDB server: {e}")
        # Fallback to persistent client
        return chromadb.PersistentClient(path="./chromadb_data")


async def index_documents(directory: str, company_filter: List[str] = None):
    """Index documents from directory"""
    
    # Initialize services
    chromadb_client = get_chromadb_client()
    embedding_client = EmbeddingClient()
    document_service = DocumentService(chromadb_client, embedding_client)
    
    # Get database session
    async with AsyncSessionLocal() as db:
        try:
            # Filter by company if specified
            if company_filter:
                logger.info(f"Indexing documents for companies: {company_filter}")
            else:
                logger.info(f"Indexing all documents from: {directory}")
            
            # Index documents
            result = await document_service.index_documents_from_directory(directory, db)
            
            return result
            
        except Exception as e:
            logger.error(f"Error during indexing: {str(e)}")
            raise


async def verify_indexed_documents():
    """Verify indexed documents in the database"""
    from app.models.financial_doc import FinancialDoc
    from sqlalchemy import select, func
    
    async with AsyncSessionLocal() as db:
        # Count total documents
        count_result = await db.execute(select(func.count(FinancialDoc.id)))
        total_docs = count_result.scalar()
        
        # Get document statistics by company
        stats_result = await db.execute(
            select(
                FinancialDoc.company_name,
                func.count(FinancialDoc.id).label('count'),
                func.array_agg(FinancialDoc.doc_type).label('types')
            ).group_by(FinancialDoc.company_name)
        )
        
        stats = stats_result.all()
        
        return {
            "total_documents": total_docs,
            "by_company": [
                {
                    "company": stat.company_name,
                    "count": stat.count,
                    "document_types": list(set(stat.types))
                }
                for stat in stats
            ]
        }


async def verify_vector_store():
    """Verify documents in vector store"""
    chromadb_client = get_chromadb_client()
    
    try:
        collection = chromadb_client.get_collection(name=settings.CHROMA_COLLECTION_NAME)
        count = collection.count()
        
        # Get sample
        sample = collection.peek(limit=5)
        
        return {
            "total_chunks": count,
            "sample_metadata": sample.get("metadatas", []) if sample else []
        }
    except Exception as e:
        logger.error(f"Error verifying vector store: {e}")
        return {"error": str(e)}


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Index financial documents")
    parser.add_argument(
        "--directory",
        default=settings.FINANCIAL_DOCS_PATH,
        help="Directory containing documents to index"
    )
    parser.add_argument(
        "--companies",
        nargs="+",
        help="Filter by specific companies"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify indexed documents instead of indexing"
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database tables"
    )
    
    args = parser.parse_args()
    
    logger.info("Starting document indexing script...")
    
    # Initialize database if requested
    if args.init_db:
        await init_database()
    
    if args.verify:
        # Verify mode
        logger.info("Verifying indexed documents...")
        
        db_stats = await verify_indexed_documents()
        vector_stats = await verify_vector_store()
        
        print("\n=== Database Statistics ===")
        print(f"Total documents: {db_stats['total_documents']}")
        print("\nBy Company:")
        for company_stat in db_stats['by_company']:
            print(f"  - {company_stat['company']}: {company_stat['count']} documents")
            print(f"    Types: {', '.join(company_stat['document_types'])}")
        
        print("\n=== Vector Store Statistics ===")
        if "error" in vector_stats:
            print(f"Error: {vector_stats['error']}")
        else:
            print(f"Total chunks: {vector_stats['total_chunks']}")
            if vector_stats['sample_metadata']:
                print("\nSample entries:")
                for i, meta in enumerate(vector_stats['sample_metadata'][:3]):
                    print(f"  {i+1}. Company: {meta.get('company')}, "
                          f"Year: {meta.get('year')}, "
                          f"Type: {meta.get('doc_type')}")
    
    else:
        # Index mode
        result = await index_documents(args.directory, args.companies)
        
        print("\n=== Indexing Results ===")
        print(f"Total files found: {result['total_files']}")
        print(f"Successfully indexed: {result['indexed']}")
        print(f"Errors: {result['errors']}")
        
        if result['error_details']:
            print("\nError details:")
            for error in result['error_details'][:5]:  # Show first 5 errors
                print(f"  - {error}")
    
    logger.info("Script completed!")


if __name__ == "__main__":
    asyncio.run(main())