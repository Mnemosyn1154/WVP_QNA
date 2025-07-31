# 샘플 데이터 가이드

## 개요
이 프로젝트는 개발 및 테스트를 위한 샘플 데이터를 제공합니다.
실제 포트폴리오 기업의 PDF 파일과 테스트용 뉴스, 채팅 이력이 포함되어 있습니다.

## 샘플 데이터 구성

### 1. 포트폴리오 기업 (3개)
- **마인이스** - IT/소프트웨어 (AI 빅데이터 분석)
- **설로인** - 식품/유통 (프리미엄 한우)
- **우나스텔라** - 헬스케어 (디지털 헬스케어)

### 2. 재무 문서 (5개)
```
data/financial_docs/
├── 마인이스/
│   ├── 2023/마인이스_2023_재무제표.pdf
│   └── 2024/마인이스_2024_재무제표.pdf
├── 설로인/
│   ├── 2023/설로인_2023_재무제표.pdf
│   └── 2024/설로인_2024_재무제표.pdf
└── 우나스텔라/
    └── 2024/우나스텔라_2024_재무제표.pdf
```

### 3. 샘플 뉴스 (각 기업별 3개씩, 총 9개)
- 최근 한 달 이내의 날짜로 생성
- 각 기업의 특성에 맞는 뉴스 내용

### 4. 샘플 채팅 이력 (3개)
- 재무 정보 질문
- 기업 정보 질문
- 뉴스 조회 질문

## 초기 설정

### 방법 1: 한 번에 초기화 (권장)
```bash
# 데이터베이스를 리셋하고 샘플 데이터를 추가
./scripts/init_dev_data.sh
```

### 방법 2: 단계별 실행
```bash
# 1. 데이터베이스 리셋
./scripts/reset_db.sh

# 2. 샘플 데이터 추가
python scripts/seed_data.py
```

### 방법 3: 기존 데이터 유지하며 추가
```bash
# 데이터베이스 리셋 없이 샘플 데이터만 추가
python scripts/seed_data.py
```

## 데이터 확인

### 데이터베이스 내용 확인
```python
from app.db.session import SessionLocal
from app.models.financial_doc import FinancialDoc
from app.models.news import News
from app.models.portfolio_company import PortfolioCompany

db = SessionLocal()

# 포트폴리오 기업 확인
companies = db.query(PortfolioCompany).all()
for company in companies:
    print(f"{company.name} - {company.industry}")

# 재무문서 확인
docs = db.query(FinancialDoc).all()
for doc in docs:
    print(f"{doc.company_name} {doc.year} {doc.doc_type}")

# 뉴스 확인
news_list = db.query(News).all()
for news in news_list:
    print(f"{news.company_name}: {news.title}")

db.close()
```

## 테스트 시나리오

### 1. 재무 정보 조회
```
Q: "마인이스의 2024년 매출은?"
A: PDF 파일에서 실제 매출 정보를 추출하여 답변
```

### 2. 기업 비교
```
Q: "설로인과 마인이스의 매출을 비교해줘"
A: 두 기업의 재무제표를 분석하여 비교 답변
```

### 3. 뉴스 검색
```
Q: "우나스텔라의 최근 뉴스는?"
A: 데이터베이스의 뉴스 정보를 조회하여 답변
```

## 주의사항

1. **개발 환경 전용**: 이 샘플 데이터는 개발과 테스트 목적으로만 사용해야 합니다.
2. **실제 데이터**: PDF 파일은 실제 재무제표이므로 민감한 정보가 포함될 수 있습니다.
3. **재실행 가능**: seed_data.py는 중복 체크를 하므로 여러 번 실행해도 안전합니다.

## 문제 해결

### "portfolio_companies table not found" 오류
```bash
# 마이그레이션 재실행
alembic upgrade head
```

### 데이터가 비어있는 경우
```bash
# 전체 초기화
./scripts/init_dev_data.sh
```

### PDF 파일을 찾을 수 없는 경우
- `data/financial_docs/` 디렉토리 구조 확인
- 파일명이 정확한지 확인