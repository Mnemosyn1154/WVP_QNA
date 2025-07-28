# 투자 포트폴리오 Q&A 챗봇

AI 기반 투자 포트폴리오 Q&A 시스템으로, 투자팀이 포트폴리오 기업의 재무 정보와 뉴스를 실시간으로 조회하고 분석할 수 있는 대화형 챗봇입니다.

## 주요 기능

- 📊 재무제표 PDF 문서 분석 및 검색
- 📰 기업 관련 뉴스 검색 및 요약
- 💬 자연어 기반 질의응답 시스템
- 🚀 Claude AI를 활용한 지능형 응답 생성
- 📈 벡터 데이터베이스를 활용한 의미 기반 검색

## 기술 스택

### Backend
- **Framework**: FastAPI 0.110
- **Language**: Python 3.11
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Vector DB**: ChromaDB
- **AI/LLM**: Claude 3 (Opus/Sonnet/Haiku)

### Infrastructure
- **Container**: Docker & Docker Compose
- **Web Server**: Nginx
- **Process Manager**: Gunicorn

## 시작하기

### 사전 요구사항

- Docker & Docker Compose
- Claude API Key

### 설치 및 실행

1. 저장소 클론
```bash
git clone <repository-url>
cd QnA_Agent
```

2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 CLAUDE_API_KEY 설정
```

3. Docker 컨테이너 실행
```bash
docker-compose up -d
```

4. API 문서 확인
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

## 프로젝트 구조

```
QnA_Agent/
├── app/                    # FastAPI 애플리케이션
│   ├── api/               # API 엔드포인트
│   ├── core/              # 핵심 설정 및 유틸리티
│   ├── crud/              # 데이터베이스 CRUD 작업
│   ├── models/            # SQLAlchemy 모델
│   ├── schemas/           # Pydantic 스키마
│   └── services/          # 비즈니스 로직
├── docker-compose.yml     # Docker 구성
├── Dockerfile            # 애플리케이션 Docker 이미지
├── requirements.txt      # Python 의존성
└── init-db/             # PostgreSQL 초기화 스크립트
```

## API 엔드포인트

### 채팅
- `POST /api/chat` - 질문에 대한 AI 응답 생성
- `GET /api/chat/history` - 대화 기록 조회

### 문서
- `GET /api/documents/search` - 재무 문서 검색
- `GET /api/documents/{id}` - 특정 문서 조회
- `POST /api/documents/index` - 문서 인덱싱

### 뉴스
- `GET /api/news/search` - 뉴스 검색
- `GET /api/news/{id}` - 특정 뉴스 조회
- `POST /api/news/index` - 뉴스 인덱싱

### 헬스체크
- `GET /health` - 기본 헬스체크
- `GET /health/detailed` - 상세 헬스체크

## 개발 가이드

### 로컬 개발 환경 설정

1. Python 가상환경 생성
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 개발 서버 실행
```bash
uvicorn app.main:app --reload --port 8080
```

### 코드 스타일

- Python: PEP 8 준수
- 타입 힌트 사용 필수
- Docstring 작성 (Google 스타일)

## 라이센스

이 프로젝트는 비공개 소프트웨어입니다.

## 문의

프로젝트 관련 문의사항은 투자팀으로 연락주세요.