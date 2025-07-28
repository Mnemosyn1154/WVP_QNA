# Investment Portfolio Q&A Chatbot: Code Guideline

## 1. Project Overview

This document outlines the coding standards and best practices for the "Investment Portfolio Intelligence Assistant" project. This AI-powered conversational Q&A chatbot aims to provide investment teams with rapid access to financial and news information on portfolio companies. The system leverages a React.js frontend, a FastAPI backend, and a Retrieval-Augmented Generation (RAG) pattern utilizing Anthropic's Claude API, PostgreSQL, ChromaDB, and Redis.

Key architectural decisions include:
*   **Decoupled Frontend/Backend**: React.js for UI, FastAPI for business logic.
*   **RAG Pattern**: Claude API for LLM, ChromaDB for vector search, PostgreSQL for metadata.
*   **Performance Optimization**: Redis for caching, asynchronous processing in FastAPI.
*   **Scalability**: Dockerized services, domain-driven backend structure.

## 2. Core Principles

1.  **Readability**: Code MUST be easily understood by other developers.
2.  **Maintainability**: Code MUST be simple to modify, debug, and extend.
3.  **Testability**: Code MUST be designed for easy and comprehensive testing.
4.  **Performance**: Code MUST be optimized for speed and resource efficiency, especially for I/O operations.
5.  **Security**: Code MUST adhere to security best practices, protecting sensitive data.

## 3. Language-Specific Guidelines

### 3.1 Python (FastAPI Backend)

#### File Organization and Directory Structure
*   **MUST**: Organize code by business domain within the `app/` directory.
    ```
    app/
    ├── api/                # API endpoints (routers)
    │   ├── endpoints/
    │   │   ├── chat.py
    │   │   ├── documents.py
    │   │   └── auth.py
    │   └── deps.py         # Dependency injection utilities
    ├── core/               # Core configurations, utilities, security
    │   ├── config.py
    │   └── security.py
    ├── crud/               # Database CRUD operations (repositories)
    │   ├── chat_crud.py
    │   └── document_crud.py
    ├── schemas/            # Pydantic models for request/response/database
    │   ├── chat_schemas.py
    │   └── document_schemas.py
    ├── services/           # Business logic, external API calls, RAG pipeline
    │   ├── chat_service.py
    │   ├── document_service.py
    │   └── rag_pipeline.py
    ├── db/                 # Database session management
    │   └── session.py
    └── main.py             # FastAPI app initialization
    ```
*   **MUST NOT**: Create monolithic files containing multiple unrelated domains or layers.

#### Import/Dependency Management
*   **MUST**: Use absolute imports from the `app` root.
    ```python
    # MUST: Absolute import
    from app.services.chat_service import ChatService
    from app.schemas.chat_schemas import ChatRequest
    ```
*   **MUST NOT**: Use relative imports that make code less portable or harder to refactor.
    ```python
    # MUST NOT: Relative import
    # from ..services.chat_service import ChatService
    ```
*   **MUST**: Explicitly declare dependencies using FastAPI's `Depends` for better testability and maintainability.
    ```python
    # MUST: Use FastAPI's Depends for dependency injection
    from fastapi import Depends, APIRouter
    from app.services.chat_service import ChatService

    router = APIRouter()

    @router.post("/chat/")
    async def create_chat_completion(
        request: ChatRequest,
        chat_service: ChatService = Depends(ChatService)
    ):
        return await chat_service.process_query(request.question)
    ```

#### Error Handling Patterns
*   **MUST**: Use FastAPI's `HTTPException` for API-level errors.
    ```python
    # MUST: Raise HTTPException for API errors
    from fastapi import HTTPException, status

    async def get_document(doc_id: int):
        doc = await document_crud.get(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc
    ```
*   **MUST**: Implement custom exception handlers for specific application errors.
*   **MUST**: Log detailed error information for debugging.
    ```python
    # MUST: Log errors
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Some risky operation
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error(f"Calculation error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    ```

### 3.2 JavaScript/TypeScript (React.js Frontend)

#### File Organization and Directory Structure
*   **MUST**: Organize components and hooks by feature or domain.
    ```
    src/
    ├── components/         # Reusable UI components (e.g., Button, Modal)
    │   ├── common/
    │   └── layout/
    ├── features/           # Feature-specific components, hooks, and logic
    │   ├── chat/
    │   │   ├── components/ # Chat-specific components (e.g., ChatWindow, MessageBubble)
    │   │   ├── hooks/      # Chat-specific hooks (e.g., useChat)
    │   │   └── ChatPage.jsx
    │   ├── auth/
    │   │   └── LoginPage.jsx
    │   └── documents/
    ├── hooks/              # Global reusable hooks (e.g., useAuth)
    ├── services/           # API interaction logic
    │   └── api.js
    ├── contexts/           # React Context API providers
    ├── utils/              # General utility functions
    ├── App.jsx
    └── main.jsx
    ```
*   **MUST NOT**: Dump all components into a single `components/` directory without further organization.

#### Import/Dependency Management
*   **MUST**: Use absolute imports configured via `jsconfig.json` or `tsconfig.json` for cleaner paths.
    ```javascript
    // jsconfig.json or tsconfig.json
    {
      "compilerOptions": {
        "baseUrl": "src"
      }
    }

    // MUST: Absolute import
    import { Button } from 'components/common/Button';
    import { useChat } from 'features/chat/hooks/useChat';
    ```
*   **MUST NOT**: Use deeply nested relative imports.

#### Error Handling Patterns
*   **MUST**: Use `try-catch` blocks for asynchronous operations (e.g., API calls) and display user-friendly error messages.
    ```javascript
    // MUST: Handle errors in async operations
    import { useState } from 'react';
    import api from 'services/api';

    function ChatInput() {
      const [error, setError] = useState(null);

      const handleSubmit = async (question) => {
        try {
          setError(null);
          const response = await api.post('/chat', { question });
          // Process response
        } catch (err) {
          console.error("Failed to send message:", err);
          setError("Failed to send message. Please try again.");
        }
      };

      return (
        <div>
          {error && <div className="text-red-500">{error}</div>}
          <button onClick={() => handleSubmit("Hello")}>Send</button>
        </div>
      );
    }
    ```
*   **MUST**: Centralize error logging or reporting (e.g., to a monitoring service) if applicable.

## 4. Code Style Rules

### MUST Follow:

*   **Consistent Naming Conventions**:
    *   **Python**: `snake_case` for variables, functions, and modules. `PascalCase` for classes. `UPPER_SNAKE_CASE` for constants.
    *   **JavaScript/TypeScript**: `camelCase` for variables and functions. `PascalCase` for React components and classes. `UPPER_SNAKE_CASE` for global constants.
    *   **Rationale**: Ensures immediate recognition of code elements and improves readability.

    ```python
    # MUST: Python naming
    class ChatService:
        MAX_RETRIES = 3
        def process_query(self, user_question: str):
            pass
    ```
    ```javascript
    // MUST: JavaScript naming
    const maxRetries = 3;
    function ChatInput() { /* ... */ }
    class ApiService { /* ... */ }
    ```

*   **Type Hinting (Python) / TypeScript (JavaScript)**:
    *   **MUST**: Use type hints for all function arguments, return values, and class attributes in Python.
    *   **MUST**: Use TypeScript for all frontend code to ensure type safety.
    *   **Rationale**: Improves code clarity, enables static analysis, and reduces runtime errors.

    ```python
    # MUST: Python type hints
    def calculate_revenue(sales: float, price_per_unit: float) -> float:
        return sales * price_per_unit
    ```
    ```typescript
    // MUST: TypeScript types
    interface ChatMessage {
      id: string;
      text: string;
      sender: 'user' | 'ai';
    }

    const sendMessage = (message: ChatMessage): void => { /* ... */ };
    ```

*   **Docstrings/Comments**:
    *   **MUST**: Provide clear and concise docstrings for all modules, classes, and functions in Python (Google style).
    *   **MUST**: Add comments for complex logic or non-obvious code sections in both Python and JavaScript.
    *   **Rationale**: Essential for understanding code purpose and usage, especially in a team environment.

    ```python
    # MUST: Python Docstring
    def get_financial_report(company_name: str, year: int) -> dict:
        """Retrieves the financial report for a given company and year.

        Args:
            company_name: The name of the company.
            year: The fiscal year of the report.

        Returns:
            A dictionary containing the financial report data.
        """
        # ... implementation ...
    ```

*   **Pydantic for Data Validation**:
    *   **MUST**: Use Pydantic models for all request bodies, response models, and database schemas in FastAPI.
    *   **Rationale**: Provides robust data validation, serialization, and automatic documentation.

    ```python
    # MUST: Use Pydantic for data validation
    from pydantic import BaseModel

    class ChatRequest(BaseModel):
        question: str
        context: dict | None = None

    class ChatResponse(BaseModel):
        answer: str
        sources: list[str]
    ```

*   **Asynchronous Programming**:
    *   **MUST**: Use `async/await` for all I/O-bound operations (database queries, external API calls, file operations) in FastAPI.
    *   **Rationale**: Prevents blocking the event loop, improving concurrency and overall system responsiveness.

    ```python
    # MUST: Use async/await for I/O operations
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.crud.document_crud import DocumentCRUD

    async def get_document_by_id(db: AsyncSession, doc_id: int):
        return await DocumentCRUD(db).get(doc_id)
    ```

### MUST NOT Do:

*   **Monolithic Files/Modules**:
    *   **MUST NOT**: Create huge, multi-responsibility modules or files that handle too many unrelated concerns.
    *   **Rationale**: Violates Single Responsibility Principle, makes code hard to navigate, test, and maintain.

    ```python
    # MUST NOT: Monolithic file (avoid combining unrelated logic)
    # chat_and_document_and_user_service.py
    # This file should be split into chat_service.py, document_service.py, user_service.py
    ```

*   **Complex State Management (Frontend)**:
    *   **MUST NOT**: Introduce overly complex state management patterns (e.g., Redux) unless absolutely necessary for global, deeply shared state. Prefer React Context API and local component state for most cases.
    *   **Rationale**: Increases boilerplate and learning curve for a project of this scale. Context API is sufficient for the current requirements.

    ```javascript
    // MUST NOT: Over-engineer state management for simple cases
    // Avoid introducing Redux/Zustand/Jotai for simple chat state if Context API suffices.
    // Use React Context API for global state like user authentication or theme.
    ```

*   **Hardcoding Sensitive Information**:
    *   **MUST NOT**: Hardcode API keys, database credentials, or any other sensitive information directly in the code.
    *   **Rationale**: Major security vulnerability. Use environment variables (e.g., `os.getenv` in Python, `import.meta.env` in Vite) or a secure configuration management system.

    ```python
    # MUST NOT: Hardcode API key
    # CLAUDE_API_KEY = "sk-..."

    # MUST: Use environment variables
    import os
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    ```

*   **Ignoring Exceptions**:
    *   **MUST NOT**: Use empty `except` blocks or `pass` in `except` blocks, suppressing errors without logging or handling them.
    *   **Rationale**: Makes debugging impossible and hides critical issues.

    ```python
    # MUST NOT: Suppress exceptions
    # try:
    #     some_risky_operation()
    # except Exception:
    #     pass # This is bad!

    # MUST: Handle or log exceptions appropriately
    try:
        some_risky_operation()
    except SpecificException as e:
        logger.error(f"Error during operation: {e}")
        # Re-raise, return error, or provide fallback
    ```

## 5. Architecture Patterns

### Component/Module Structure Guidelines

*   **Domain-Driven Design (Backend)**:
    *   **MUST**: Structure the backend around business domains (e.g., `chat`, `documents`, `auth`). Each domain should have its own `api/endpoints`, `services`, `crud`, and `schemas` subdirectories.
    *   **Rationale**: Promotes high cohesion and low coupling, making the codebase easier to understand, develop, and scale independently.

*   **Layered Architecture (Backend)**:
    *   **MUST**: Maintain clear separation between API (endpoints), Service (business logic), and Repository (CRUD/data access) layers.
    *   **Rationale**: Each layer has a distinct responsibility, simplifying testing and allowing changes in one layer without affecting others.

    ```python
    # app/api/endpoints/chat.py (API Layer)
    from fastapi import APIRouter, Depends
    from app.schemas.chat_schemas import ChatRequest, ChatResponse
    from app.services.chat_service import ChatService

    router = APIRouter()

    @router.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest, service: ChatService = Depends()):
        return await service.process_query(request.question, request.context)

    # app/services/chat_service.py (Service Layer - Business Logic)
    from app.services.rag_pipeline import RAGPipeline
    from app.crud.chat_crud import ChatCRUD
    from app.schemas.chat_schemas import ChatResponse
    from sqlalchemy.ext.asyncio import AsyncSession

    class ChatService:
        def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
            self.rag_pipeline = RAGPipeline(db_session)
            self.chat_crud = ChatCRUD(db_session)

        async def process_query(self, question: str, context: dict) -> ChatResponse:
            answer, sources = await self.rag_pipeline.generate_response(question, context)
            await self.chat_crud.save_chat_history(question, answer, sources)
            return ChatResponse(answer=answer, sources=sources)

    # app/crud/chat_crud.py (Repository Layer - Data Access)
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.models import ChatHistory

    class ChatCRUD:
        def __init__(self, db_session: AsyncSession):
            self.db = db_session

        async def save_chat_history(self, question: str, answer: str, sources: list[str]):
            chat_entry = ChatHistory(question=question, answer=answer, context={"sources": sources})
            self.db.add(chat_entry)
            await self.db.commit()
            await self.db.refresh(chat_entry)
            return chat_entry
    ```

### Data Flow Patterns

*   **Request-Response (RESTful API)**:
    *   **MUST**: All client-server communication MUST follow a RESTful request-response pattern using JSON payloads.
    *   **Rationale**: Standard, stateless, and widely understood pattern for web services.
    *   **Example**: `POST /api/chat` for sending questions, `GET /api/news/search` for news retrieval.

*   **RAG Pipeline**:
    *   **MUST**: Implement the RAG pipeline within the `rag_pipeline.py` service. This service is responsible for:
        1.  Receiving user query.
        2.  Generating embeddings for the query.
        3.  Retrieving relevant document chunks from ChromaDB.
        4.  Constructing an augmented prompt.
        5.  Calling the Claude API.
        6.  Parsing and returning the LLM response.
    *   **Rationale**: Centralizes the core AI logic, making it maintainable and testable.

    ```python
    # app/services/rag_pipeline.py
    from app.crud.document_crud import DocumentCRUD
    from app.core.llm import LLMClient # Abstraction for Claude API
    from app.core.embedding import EmbeddingClient # Abstraction for Embedding model

    class RAGPipeline:
        def __init__(self, db_session: AsyncSession):
            self.document_crud = DocumentCRUD(db_session)
            self.llm_client = LLMClient()
            self.embedding_client = EmbeddingClient()

        async def generate_response(self, question: str, context: dict | None = None) -> tuple[str, list[str]]:
            # 1. Generate query embedding
            query_embedding = await self.embedding_client.embed(question)

            # 2. Retrieve relevant documents from ChromaDB (via document_crud)
            relevant_docs = await self.document_crud.search_vector_db(query_embedding, top_k=5)
            doc_contents = [doc.content for doc in relevant_docs]
            sources = [doc.source_id for doc in relevant_docs] # Assuming source_id is available

            # 3. Construct augmented prompt
            augmented_prompt = self._build_prompt(question, doc_contents)

            # 4. Call LLM API (with optional model routing)
            answer = await self.llm_client.generate_text(augmented_prompt, question_type="complex_analysis")

            return answer, sources

        def _build_prompt(self, question: str, documents: list[str]) -> str:
            # MUST: Define clear prompt templates
            context_str = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(documents)])
            return f"""You are an intelligent assistant for investment teams.
            Based on the following documents, answer the user's question.
            If the answer is not in the documents, state that you don't have enough information.

            Documents:
            {context_str}

            User Question: {question}
            """
    ```

### State Management Conventions (React Frontend)

*   **MUST**: Prefer local component state (`useState`) for UI-specific, ephemeral data.
*   **MUST**: Use `useContext` for global or shared state that needs to be accessed by multiple, non-directly related components (e.g., authentication status, user preferences).
*   **MUST**: Use custom hooks (`useReducer`, `useEffect`) to encapsulate complex state logic and side effects, promoting reusability.
*   **Rationale**: Keeps state management simple and predictable for the project's scale, avoiding over-engineering.

    ```javascript
    // MUST: Use useState for local component state
    import React, { useState } from 'react';

    function MessageInput() {
      const [message, setMessage] = useState('');
      const handleSend = () => { /* ... */ };

      return (
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
      );
    }

    // MUST: Use useContext for global state
    // src/contexts/AuthContext.jsx
    import React, { createContext, useContext, useState } from 'react';

    const AuthContext = createContext(null);

    export const AuthProvider = ({ children }) => {
      const [user, setUser] = useState(null);
      // ... login/logout functions ...
      return (
        <AuthContext.Provider value={{ user, setUser }}>
          {children}
        </AuthContext.Provider>
      );
    };

    export const useAuth = () => useContext(AuthContext);

    // In a component:
    // import { useAuth } from 'contexts/AuthContext';
    // const { user } = useAuth();
    ```

### API Design Standards (FastAPI)

*   **MUST**: Follow RESTful principles for API endpoint design (e.g., `GET /resources`, `POST /resources`, `GET /resources/{id}`).
*   **MUST**: Use clear, descriptive, and pluralized resource names in URLs.
*   **MUST**: Use appropriate HTTP status codes for responses (e.g., 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Internal Server Error).
*   **MUST**: Provide meaningful error messages in JSON format for client consumption.
*   **MUST**: Implement authentication and authorization using JWT tokens for protected endpoints.
*   **Rationale**: Ensures consistency, predictability, and ease of integration for API consumers.

    ```python
    # MUST: RESTful endpoint design with proper status codes and response models
    from fastapi import APIRouter, HTTPException, status
    from app.schemas.document_schemas import DocumentResponse, DocumentCreate
    from app.services.document_service import DocumentService

    router = APIRouter(prefix="/documents", tags=["Documents"])

    @router.get("/{doc_id}", response_model=DocumentResponse)
    async def get_document_by_id(doc_id: int, service: DocumentService = Depends()):
        document = await service.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return document

    @router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
    async def create_document(doc_data: DocumentCreate, service: DocumentService = Depends()):
        return await service.create_new_document(doc_data)
    ```

    ## Gemini CLI 연동 가이드

### 목적
사용자가 「Gemini와 상의하면서 진행해줘」 (또는 유사한 표현)라고 지시할 경우, Claude는 이후 작업을 Gemini CLI와 협력하여 진행한다.
Gemini로부터 받은 응답은 그대로 보여주고, Claude의 해설이나 통합 설명을 덧붙여 두 에이전트의 지식을 결합한다.

### 트리거
- 정규표현식: `/Gem.*상의하면서/`
- 예시:
  - 「Gem과 상의하면서 진행해줘」
  - 「이건 Gemini랑 이야기하면서 하자」

### Gemini CLI 사용법
```bash
# 기본 사용법
gemini -p "프롬프트 내용"

# 파일을 컨텍스트로 제공
gemini -p "프롬프트 내용" < input_file.md

# 여러 줄 프롬프트 (heredoc 사용)
export PROMPT="여러 줄의
프롬프트 내용"
gemini <<EOF
$PROMPT
EOF

# 주요 옵션
# -m, —model: 모델 선택 (기본: gemini-2.5-pro)
# -p, —prompt: 프롬프트 텍스트
# -d, —debug: 디버그 모드
# -y, —yolo: 자동 승인 모드
```

# Gemini CLI Commands (Updated 2025)

## Core Commands

### `/permissions`
Display and manage permission settings for Gemini CLI. Shows current tool permissions and authentication status.

### `/status` 
Check the current status of Gemini CLI including:
- Connection status to Gemini model
- Authentication method in use
- Rate limit information (60 requests/minute, 1000/day for free tier)
- Active MCP servers

### `/memory`
Manage the AI's instructional context from GEMINI.md files:
- `/memory` - Display current memory context
- `/memory add <text>` - Add text to AI's memory

### `/mcp`
Model Context Protocol server management:
- `/mcp` - List configured MCP servers and connection status
- `/mcp show` - Show detailed descriptions for servers and tools
- `/mcp hide` - Hide tool descriptions, show only names

### `/auth`
Switch between authentication methods:
- Google account login (free tier)
- API key authentication
- Vertex AI authentication

### `/stats`
Display usage statistics:
- Request count for current session
- Daily/minute rate limit usage
- Model being used (gemini-2.5-pro/flash)

### `/help`
Display help information about Gemini CLI commands and features

## Shell Integration

### `!` prefix
Execute shell commands directly:
- `!ls -la` - List files
- `!git status` - Check git status
- Commands run with user's shell permissions

## File Operations

### `@` symbol
Reference files in prompts:
- `@file.txt` - Include file content in prompt
- Supports multiple files with `read_many_files` tool

## Authentication Notes

1. **Free Tier (Google Login)**
   - 60 requests per minute
   - 1,000 requests per day
   - May switch to gemini-2.5-flash during high load

2. **API Key**
   - Higher rate limits available
   - Configure in settings

3. **Vertex AI**
   - Enterprise authentication option
   - Custom quotas

## Security Configuration

- `excludeTools`: String matching for command restrictions (can be bypassed)
- `coreTools`: Explicitly allowed commands (recommended)
- `allowedMcpServerNames`: Restrict available MCP servers
- Tool usage requires user permission before execution