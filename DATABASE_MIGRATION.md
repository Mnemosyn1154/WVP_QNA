# 데이터베이스 마이그레이션 가이드

## 개요

이 프로젝트는 Alembic을 사용하여 데이터베이스 스키마를 관리합니다. 
현재는 개발 환경에서 SQLite를 사용하고 있지만, 프로덕션 환경에서는 PostgreSQL로 쉽게 전환할 수 있도록 설계되었습니다.

## 현재 데이터베이스 구조

### 테이블 목록
- `users` - 사용자 정보
- `financial_docs` - 재무문서 메타데이터
- `news` - 뉴스 정보
- `chat_history` - 채팅 이력
- `portfolio_companies` - 포트폴리오 기업 정보 (모델은 있지만 아직 사용 안 함)
- `news_articles` - 뉴스 기사 상세 (모델은 있지만 아직 사용 안 함)

## 초기 설정

### 1. 데이터베이스 초기화
```bash
# 새로운 데이터베이스 생성 (첫 실행 시)
./scripts/init_db.sh
```

### 2. 데이터베이스 리셋 (주의: 모든 데이터 삭제)
```bash
# 기존 데이터베이스를 삭제하고 새로 생성
./scripts/reset_db.sh
```

## Alembic 사용법

### 새로운 마이그레이션 생성
```bash
# 모델 변경 후 자동으로 마이그레이션 생성
alembic revision --autogenerate -m "설명"
```

### 마이그레이션 적용
```bash
# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade <revision>
```

### 마이그레이션 롤백
```bash
# 이전 버전으로 롤백
alembic downgrade -1

# 특정 버전으로 롤백
alembic downgrade <revision>
```

### 현재 버전 확인
```bash
alembic current
```

### 마이그레이션 히스토리 확인
```bash
alembic history
```

## SQLite에서 PostgreSQL로 전환

### 1. PostgreSQL 설치 및 실행
```bash
# Docker Compose 사용 (권장)
docker compose up -d postgres

# 또는 로컬 PostgreSQL 사용
brew install postgresql
brew services start postgresql
```

### 2. 환경 변수 업데이트
`.env` 파일에서 DATABASE_URL 변경:
```env
# SQLite (현재)
DATABASE_URL=sqlite:///./data/portfolio_qa.db

# PostgreSQL (프로덕션)
DATABASE_URL=postgresql://portfolio_user:portfolio_pass@localhost:5432/portfolio_qa_db
```

### 3. PostgreSQL 드라이버 설치
```bash
pip install psycopg2-binary
```

### 4. 마이그레이션 실행
```bash
alembic upgrade head
```

## 주의사항

1. **데이터 백업**: 프로덕션 환경에서는 마이그레이션 전 반드시 백업
2. **테스트**: 새로운 마이그레이션은 개발 환경에서 충분히 테스트
3. **동시성**: SQLite는 동시 쓰기 제한이 있으므로 10명 이상 사용 시 PostgreSQL 권장

## 문제 해결

### "database is locked" 오류
SQLite의 동시성 제한으로 발생. PostgreSQL로 전환 권장.

### 마이그레이션 충돌
```bash
# 마이그레이션 파일 삭제 후 재생성
rm alembic/versions/*
alembic revision --autogenerate -m "Initial migration"
```

### 스키마 불일치
```bash
# 데이터베이스 리셋 후 재생성
./scripts/reset_db.sh
```