"""
Health check endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including all dependencies"""
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "dependencies": {}
    }
    
    # Check SQLite
    try:
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        health_status["dependencies"]["sqlite"] = {"status": "healthy"}
    except Exception as e:
        health_status["dependencies"]["sqlite"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check Claude API (just verify key exists)
    if settings.CLAUDE_API_KEY:
        health_status["dependencies"]["claude_api"] = {"status": "healthy", "configured": True}
    else:
        health_status["dependencies"]["claude_api"] = {"status": "unhealthy", "configured": False}
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/debug")
async def debug_info() -> Dict[str, Any]:
    """Debug endpoint to check configuration"""
    import os
    from app.services.claude_service import ClaudeService
    
    claude_service = ClaudeService()
    
    return {
        "CLAUDE_TEST_MODE_env": os.getenv("CLAUDE_TEST_MODE"),
        "CLAUDE_TEST_MODE_settings": getattr(settings, "CLAUDE_TEST_MODE", None),
        "claude_service_test_mode": claude_service.test_mode,
        "CLAUDE_API_KEY_exists": bool(os.getenv("CLAUDE_API_KEY")),
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }