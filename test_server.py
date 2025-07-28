#!/usr/bin/env python3
"""
Simple test server for frontend testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Portfolio Q&A Test Server", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Portfolio Q&A Test Server", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Portfolio Q&A Test Server",
        "version": "0.1.0"
    }

@app.get("/api/health/detailed")
async def detailed_health_check():
    return {
        "status": "healthy",
        "service": "Portfolio Q&A Test Server",
        "version": "0.1.0",
        "dependencies": {
            "database": {"status": "healthy"},
            "redis": {"status": "healthy"},
            "vector_db": {"status": "healthy"}
        }
    }

@app.post("/api/chat")
async def chat_endpoint(request: dict):
    question = request.get("question", "")
    return {
        "answer": f"테스트 응답: '{question}'에 대한 답변입니다. 실제 AI는 연결되지 않았습니다.",
        "sources": ["테스트 문서 1", "테스트 문서 2"],
        "processing_time": 1.5
    }

@app.get("/api/documents/search")
async def search_documents(company: str = "마인이스", limit: int = 5):
    return [
        {
            "id": 1,
            "companyName": company,
            "docType": "사업보고서",
            "year": 2024,
            "filePath": f"/test/{company}_2024.pdf",
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00"
        }
    ]

@app.get("/api/news/search")
async def search_news(company: str = "마인이스", limit: int = 5):
    return [
        {
            "id": 1,
            "companyName": company,
            "title": f"{company} 테스트 뉴스",
            "content": "테스트 뉴스 내용입니다.",
            "source": "테스트 신문",
            "publishedDate": "2024-01-01T00:00:00",
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00"
        }
    ]

if __name__ == "__main__":
    print("🚀 Starting Portfolio Q&A Test Server...")
    print("📍 Frontend: http://localhost:4001")
    print("📍 Backend: http://localhost:8080")
    print("📍 API Docs: http://localhost:8080/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)