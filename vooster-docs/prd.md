# 투자 포트폴리오 Q&A 챗봇 PRD v0.1

**문서 버전**: 0.1  
**작성일**: 2025-07-25  
**작성자**: AI Assistant  
**상태**: 초안

---

## 1. 제품 개요

### 1.1 제품명
투자 포트폴리오 Intelligence Assistant (가칭)

### 1.2 비전
투자팀이 120~250개 포트폴리오 기업의 뉴스와 재무 정보를 실시간으로 조회하고 인사이트를 얻을 수 있는 AI 기반 대화형 시스템

### 1.3 핵심 가치
- **즉시성**: 3초 내 필요한 정보 획득
- **정확성**: 원본 문서 기반 팩트 체크
- **효율성**: 수동 검색 시간 90% 감소

### 1.4 성공 지표 (KPI)
- 일일 활성 사용자(DAU): 3명 이상
- 평균 응답 시간: 3초 이하
- 월 API 비용: 10만원 이내
- 시스템 가용성: 99%

## 2. 사용자 요구사항

### 2.1 타겟 사용자
- **주 사용자**: 투자팀 전 직원 (약 10명)
- **사용 환경**: 데스크톱 웹 브라우저
- **기술 수준**: 일반 비즈니스 사용자

### 2.2 핵심 사용 시나리오

#### 시나리오 1: 재무 정보 조회
```
사용자: "A기업 2024년 매출은?"
시스템: A기업의 2024년 재무제표를 찾아 분석
응답: "A기업의 2024년 매출은 1,234억원입니다. (2024년 사업보고서 p.23 기준)"
```

#### 시나리오 2: 뉴스 검색
```
사용자: "B기업 최근 인수합병 관련 뉴스 있어?"
시스템: 최근 3년 내 B기업 관련 뉴스에서 M&A 키워드 검색
응답: "B기업은 2024년 12월 C사를 500억원에 인수했습니다. 관련 뉴스 3건을 찾았습니다."
```

#### 시나리오 3: 문서 요약
```
사용자: "D기업 작년 주주총회 내용 요약해줘"
시스템: 주주총회 관련 문서 검색 및 분석
응답: "2024년 3월 주주총회 주요 안건: 1) 배당금 주당 500원 승인 2) 신규 이사 선임..."
```

### 2.3 기능 요구사항

#### Must Have (Week 1-2)
- [ ] FR-001: 웹 기반 채팅 인터페이스
- [ ] FR-002: 기업명 기반 문서 검색
- [ ] FR-003: Claude API를 통한 PDF 분석
- [ ] FR-004: 뉴스 검색 및 표시
- [ ] FR-005: 기본적인 질의응답 처리

#### Should Have (Week 3)
- [ ] FR-006: 사용자 로그인 시스템
- [ ] FR-007: 검색 결과 캐싱
- [ ] FR-008: 재무 데이터 차트 시각화
- [ ] FR-009: 응답 출처 표시

#### Could Have (Week 4)
- [ ] FR-010: 두레이 연동 인터페이스
- [ ] FR-011: 대화 히스토리 저장
- [ ] FR-012: 고급 검색 필터
- [ ] FR-013: 다중 문서 비교 분석

### 2.4 비기능 요구사항

#### 성능
- NFR-001: 평균 응답 시간 3초 이내
- NFR-002: 동시 사용자 5명 지원
- NFR-003: 파일 크기 50MB까지 처리 가능

#### 가용성
- NFR-004: 99% 가용성 (계획된 유지보수 제외)
- NFR-005: 24/7 서비스 제공

#### 보안
- NFR-006: 사용자 인증 필요
- NFR-007: HTTPS 통신
- NFR-008: 민감 정보 암호화 저장

#### 확장성
- NFR-009: 250개 기업까지 확장 가능
- NFR-010: 두레이/ERP 연동 가능한 아키텍처

## 3. 시스템 아키텍처

### 3.1 기술 스택

#### Frontend
```yaml
Framework: React.js 18
Styling: Tailwind CSS 3.0
Charts: Chart.js 4.0
Build Tool: Vite
State Management: Context API
```

#### Backend
```yaml
Framework: FastAPI 0.110
Language: Python 3.11
Database: PostgreSQL 15
Cache: Redis 7
Vector DB: ChromaDB
Queue: Celery (optional)
```

#### AI/ML
```yaml
Primary LLM: Claude 3 Opus
Fallback LLM: Gemini Pro
Embeddings: sentence-transformers (jhgan/ko-sroberta-multitask)
```

#### Infrastructure
```yaml
Container: Docker
Web Server: Nginx
Process Manager: Gunicorn
Monitoring: Prometheus + Grafana (optional)
```

### 3.2 시스템 구성도

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   Nginx     │────▶│  FastAPI    │
│   Web UI    │     │  (Reverse   │     │   Server    │
└─────────────┘     │   Proxy)    │     └──────┬──────┘
                    └─────────────┘              │
                                                 │
                    ┌─────────────────────────────┴─────────────────────────┐
                    │                                                       │
                    ▼                           ▼                           ▼
            ┌─────────────┐             ┌─────────────┐            ┌─────────────┐
            │ PostgreSQL  │             │    Redis    │            │  ChromaDB   │
            │   (Meta)    │             │   (Cache)   │            │  (Vectors)  │
            └─────────────┘             └─────────────┘            └─────────────┘
                                                                            
                    ┌─────────────┐             ┌─────────────┐
                    │ File System │             │ Claude API  │
                    │   (PDFs)    │             │   (LLM)     │
                    └─────────────┘             └─────────────┘
```

### 3.3 데이터 모델

#### 데이터베이스 스키마
```sql
-- 뉴스 메타데이터
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    content_url TEXT,
    source VARCHAR(100),
    published_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_company_date (company_name, published_date DESC)
);

-- 재무제표 인덱스
CREATE TABLE financial_docs (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    doc_type VARCHAR(50), -- '사업보고서', '반기보고서', '분기보고서'
    year INTEGER NOT NULL,
    quarter INTEGER,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_company_year (company_name, year DESC)
);

-- 사용자 (확장성 고려)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    password_hash TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- 대화 히스토리 (선택적)
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    question TEXT NOT NULL,
    answer TEXT,
    context JSONB, -- 검색된 문서 정보
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 파일 시스템 구조
```
/data/
├── financial_docs/
│   ├── {company_name}/
│   │   ├── 2024/
│   │   │   ├── annual_report_2024.pdf
│   │   │   ├── Q1_report_2024.pdf
│   │   │   └── ...
│   │   └── ...
│   └── ...
└── cache/
    └── embeddings/
```

### 3.4 API 설계

#### 주요 엔드포인트
```yaml
# 채팅
POST /api/chat
Request: { "question": string, "context": object? }
Response: { "answer": string, "sources": array, "charts": array? }

# 문서 검색
GET /api/documents/search
Query: { "company": string, "year": number?, "type": string? }
Response: { "documents": array, "total": number }

# 뉴스 검색
GET /api/news/search
Query: { "company": string, "keyword": string?, "from": date?, "to": date? }
Response: { "news": array, "total": number }

# 사용자 인증
POST /api/auth/login
Request: { "email": string, "password": string }
Response: { "token": string, "user": object }
```

## 4. 구현 계획

### 4.1 개발 일정 (4주)

#### Week 1: 기초 인프라 구축
| 일차 | 작업 내용 | 산출물 |
|------|-----------|---------|
| Day 1-2 | 개발 환경 설정<br>- Docker 환경 구성<br>- PostgreSQL, Redis 설치<br>- FastAPI 프로젝트 생성 | Docker Compose 파일<br>기본 프로젝트 구조 |
| Day 3-4 | 파일 시스템 구축<br>- 재무제표 폴더 구조화<br>- 파일 인덱싱 스크립트<br>- 메타데이터 DB 구축 | 파일 인덱서<br>DB 스키마 |
| Day 5-7 | Claude API 연동<br>- PDF 처리 함수<br>- 프롬프트 템플릿<br>- 기본 채팅 API | Claude 연동 모듈<br>채팅 API v0.1 |

#### Week 2: 검색 시스템 구현
| 일차 | 작업 내용 | 산출물 |
|------|-----------|---------|
| Day 8-10 | 벡터 검색 구현<br>- ChromaDB 설정<br>- 뉴스 임베딩 파이프라인<br>- 검색 API 구현 | 벡터 검색 모듈<br>뉴스 검색 API |
| Day 11-12 | 캐싱 시스템<br>- Redis 캐싱 로직<br>- 응답 시간 최적화 | 캐싱 레이어 |
| Day 13-14 | 통합 테스트<br>- 전체 플로우 테스트<br>- 버그 수정 | 테스트 결과서 |

#### Week 3: 프론트엔드 개발
| 일차 | 작업 내용 | 산출물 |
|------|-----------|---------|
| Day 15-17 | 채팅 인터페이스<br>- React 채팅 컴포넌트<br>- 실시간 응답 표시<br>- 에러 처리 | 채팅 UI |
| Day 18-19 | 데이터 시각화<br>- Chart.js 통합<br>- 재무 데이터 차트 | 차트 컴포넌트 |
| Day 20-21 | 인증 시스템<br>- 로그인 페이지<br>- JWT 토큰 관리 | 인증 시스템 |

#### Week 4: 최적화 및 배포
| 일차 | 작업 내용 | 산출물 |
|------|-----------|---------|
| Day 22-23 | 성능 최적화<br>- 쿼리 최적화<br>- 동시성 처리 | 성능 개선 보고서 |
| Day 24-25 | 배포 준비<br>- 프로덕션 설정<br>- 배포 스크립트 | 배포 가이드 |
| Day 26-28 | 문서화<br>- 사용자 매뉴얼<br>- API 문서<br>- 운영 가이드 | 문서 세트 |

### 4.2 MVP 범위 (2주차 완료 목표)

#### 포함 기능
- ✅ 기본 채팅 인터페이스 (터미널/간단한 웹)
- ✅ 재무제표 PDF 검색 및 분석
- ✅ 뉴스 메타데이터 검색
- ✅ Claude API 연동
- ✅ 기본 캐싱

#### 제외 기능
- ❌ 고급 UI/UX
- ❌ 사용자 인증
- ❌ 차트/시각화
- ❌ 두레이 연동

## 5. 비용 관리

### 5.1 예상 사용량 계산
```
일일 예상 질문 수: 50개
평균 토큰/질문:
- 입력: 2,000 토큰 (컨텍스트 포함)
- 출력: 500 토큰

월간 토큰 사용량:
50 질문/일 × 30일 × 2,500 토큰 = 3,750,000 토큰

캐싱 적용 시 (50% 절감):
실제 API 호출: 1,875,000 토큰
```

### 5.2 API 비용 최적화 전략

#### 라우팅 로직
```python
def select_llm_model(question_type, complexity):
    if question_type == "simple_lookup":
        return "claude-3-haiku"  # 저렴
    elif complexity > 0.7:
        return "claude-3-opus"   # 고급 분석
    else:
        return "claude-3-sonnet" # 중간
```

#### 예상 월 비용 분배
- Claude Opus (30%): 6만원
- Claude Sonnet (50%): 3만원  
- Claude Haiku (20%): 1만원
- **총 예상: 10만원/월**

### 5.3 비용 모니터링
```python
# 일일 비용 한도 설정
DAILY_COST_LIMIT = 3500  # 원
current_cost = await redis.get("daily_api_cost")
if current_cost > DAILY_COST_LIMIT:
    return "일일 API 한도 초과. 내일 다시 시도해주세요."
```

## 6. 리스크 관리

### 6.1 기술적 리스크

| 리스크 | 영향도 | 발생확률 | 대응 방안 |
|--------|--------|----------|-----------|
| Claude API 장애 | 높음 | 낮음 | Gemini/GPT 폴백 구현 |
| 대용량 PDF 처리 실패 | 중간 | 중간 | 페이지 분할 처리 |
| 응답 시간 초과 | 중간 | 중간 | 프로그레시브 로딩 |
| 벡터 DB 성능 저하 | 낮음 | 낮음 | 인덱스 최적화 |

### 6.2 프로젝트 리스크

| 리스크 | 영향도 | 발생확률 | 대응 방안 |
|--------|--------|----------|-----------|
| 1인 개발 일정 지연 | 높음 | 중간 | MVP 범위 축소 |
| 요구사항 변경 | 중간 | 높음 | 애자일 접근, 주간 리뷰 |
| 서버 리소스 부족 | 중간 | 낮음 | 클라우드 이전 검토 |

## 7. 향후 확장 계획

### 7.1 Phase 2 (2개월 후)
- 두레이 메신저 통합
- 고급 분석 기능 (트렌드, 비교)
- 멀티 언어 지원 (영문 문서)

### 7.2 Phase 3 (6개월 후)
- KIIPS ERP 연동
- 자동 리포트 생성
- AI 기반 투자 인사이트 제공

### 7.3 확장성 고려사항
```python
# 메시징 인터페이스 추상화
class MessageInterface(ABC):
    @abstractmethod
    async def send_message(self, message: str) -> str:
        pass

class WebInterface(MessageInterface):
    # 현재 구현

class DoorayInterface(MessageInterface):
    # 향후 구현

class KakaoWorkInterface(MessageInterface):
    # 향후 구현
```

## 8. 성공 기준

### 8.1 단기 (1개월)
- [ ] 5명 이상의 활성 사용자
- [ ] 일일 50개 이상의 질문 처리
- [ ] 평균 만족도 4.0/5.0 이상

### 8.2 중기 (3개월)
- [ ] 전 직원 사용
- [ ] 월 API 비용 10만원 이내 유지
- [ ] 두레이 통합 완료

### 8.3 장기 (6개월)
- [ ] 250개 기업 커버리지
- [ ] 자동화된 인사이트 제공
- [ ] ROI 증명 (시간 절감 측정)

---

## 부록 A: 주요 기술 결정 사항

### A.1 Claude 선택 이유
- PDF 네이티브 지원
- 한국어 성능 우수
- 컨텍스트 윈도우 크기 (200K)
- 비용 대비 성능

### A.2 ChromaDB 선택 이유
- 설치 및 사용 간편
- 로컬 실행 가능
- 한국어 임베딩 지원
- 충분한 성능

### A.3 FastAPI 선택 이유
- 빠른 개발 속도
- 자동 API 문서화
- 비동기 지원
- Python 생태계 활용

---

**문서 끝**