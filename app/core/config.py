"""
Application configuration using Pydantic Settings
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Investment Portfolio Q&A Chatbot"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # ChromaDB
    CHROMADB_URL: str
    
    # Claude API
    CLAUDE_API_KEY: str
    CLAUDE_TEST_MODE: Optional[str] = None
    CLAUDE_API_MAX_FILE_SIZE_MB: float = 10.0  # Maximum file size for Claude API in MB
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Rate Limiting
    DAILY_COST_LIMIT: float = 3500.0  # KRW
    
    # File Storage
    DATA_PATH: str = "/data"
    FINANCIAL_DOCS_PATH: str = "/data/financial_docs"
    CACHE_PATH: str = "/data/cache"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Claude Model Configuration
    CLAUDE_MODEL_SIMPLE: str = "claude-3-haiku-20240307"
    CLAUDE_MODEL_STANDARD: str = "claude-3-sonnet-20240229"
    CLAUDE_MODEL_ADVANCED: str = "claude-3-opus-20240229"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "jhgan/ko-sroberta-multitask"
    
    # Vector DB Settings
    CHROMA_COLLECTION_NAME: str = "portfolio_documents"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()