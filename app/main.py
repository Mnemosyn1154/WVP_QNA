"""
FastAPI main application module
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.endpoints import chat, documents, health, pdf
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting up Portfolio Q&A Chatbot...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Add test data for development
    if settings.DEBUG:
        from app.db.session import SessionLocal
        from app.models.financial_doc import FinancialDoc
        
        db = SessionLocal()
        try:
            # Check if documents already exist
            existing_count = db.query(FinancialDoc).count()
            if existing_count == 0:
                # Add test documents
                test_docs = [
                    FinancialDoc(
                        company_name="마인이스",
                        doc_type="사업보고서",
                        year=2024,
                        file_path="data/financial_docs/마인이스_2024_사업보고서.pdf",
                        file_size=1024000
                    ),
                    FinancialDoc(
                        company_name="우나스텔라",
                        doc_type="사업보고서",
                        year=2024,
                        file_path="data/financial_docs/우나스텔라_2024_사업보고서.pdf",
                        file_size=2048000
                    ),
                    FinancialDoc(
                        company_name="설로인",
                        doc_type="사업보고서",
                        year=2024,
                        file_path="data/financial_docs/설로인_2024_사업보고서.pdf",
                        file_size=1536000
                    )
                ]
                for doc in test_docs:
                    db.add(doc)
                db.commit()
                logger.info(f"Added {len(test_docs)} test documents")
        except Exception as e:
            logger.error(f"Error adding test data: {e}")
            db.rollback()
        finally:
            db.close()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Q&A chatbot for investment portfolio management",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4001", "http://127.0.0.1:4001", "*"],  # Added specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["pdf"])
# app.include_router(news.router, prefix="/api/news", tags=["news"])  # Temporarily disabled

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Portfolio Q&A Chatbot API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }