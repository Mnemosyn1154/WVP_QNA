# Multi-LLM Q&A System Documentation

## 시스템 개요
포트폴리오 Q&A 시스템은 비용 효율성과 성능을 최적화하기 위해 **Gemini 1.5 Flash**와 **Claude 3.5 Sonnet**을 조합한 다단계 LLM 처리 구조를 사용합니다.

## 핵심 아키텍처

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Analysis  │
└────┬───────┬────┘
     │       │
     ▼       ▼
┌─────────┐ ┌─────────┐
│ Gemini  │ │ Claude  │
│  70-80% │ │  20-30% │
└─────────┘ └─────────┘
```

## LLM 선택 로직

### 1. Gemini 사용 조건 (기본값)
- ✅ 단순 사실 확인 질문
- ✅ 텍스트 기반 PDF 문서
- ✅ 단일 회사 정보 조회
- ✅ 일반적인 재무 정보 요청

### 2. Claude 사용 조건 (자동 전환)
- 🔄 비교 분석 (키워드: "비교")
- 📷 스캔된/이미지 기반 PDF
- 🏢 특정 회사 (설로인, 우나스텔라)
- 🔢 복잡한 계산이나 분석
- ❌ Gemini 텍스트 추출 실패 시

## 처리 흐름

### Step 1: 쿼리 분석
```python
# 비교 질문 감지
if "비교" in question:
    use_claude = True

# 스캔 문서 회사 감지
if any(company in question for company in ["설로인", "우나스텔라"]):
    use_claude = True
```

### Step 2: 문서 타입 확인
```python
# PDF 텍스트 추출
text_content = extract_text_from_pdf(pdf_content)

# 텍스트 품질 확인
if len(text_content.strip()) < 100:
    # 스캔된 문서로 판단
    use_claude = True
```

### Step 3: LLM 라우팅
```python
if use_claude:
    # Claude로 직접 PDF 처리
    result = await claude_service.analyze_pdf()
else:
    # Gemini로 텍스트 기반 처리
    result = await gemini_service.ask_simple_question()
```

## 비용 최적화

| 구분 | Gemini 1.5 Flash | Claude 3.5 Sonnet | 비용 차이 |
|------|------------------|-------------------|-----------|
| Input | $0.075/1M tokens | $3.00/1M tokens | 40배 |
| Output | $0.30/1M tokens | $15.00/1M tokens | 50배 |
| 사용 비율 | 70-80% | 20-30% | - |

**예상 비용 절감: 85-90%**

## 실제 사용 예시

### 1. Gemini 처리 (단순 질문)
```bash
Q: "마인이스의 2024년 매출액은?"
→ Gemini: 텍스트 추출 → 답변 생성
→ 비용: ~$0.001
```

### 2. Claude 처리 (비교 분석)
```bash
Q: "설로인과 마인이스 매출 비교해줘"
→ Claude: PDF 직접 분석 → 상세 비교
→ 비용: ~$0.06
```

### 3. 자동 전환 (스캔 문서)
```bash
Q: "설로인의 영업이익은?"
→ Gemini 시도 → 텍스트 추출 실패
→ Claude 전환 → PDF 분석
```

## 구현 파일

### 1. 핵심 서비스
- `/app/services/gemini_service.py` - Gemini API 통합
- `/app/services/claude_service.py` - Claude API 통합
- `/app/services/chat_service.py` - LLM 라우팅 로직

### 2. 지원 모듈
- `/app/services/pdf_processor.py` - PDF 텍스트 추출
- `/app/services/pdf_optimizer.py` - PDF 최적화

## 환경 설정

```bash
# .env 파일
GEMINI_API_KEY=your_gemini_api_key
CLAUDE_API_KEY=your_claude_api_key
USE_GEMINI_DEFAULT=true
```

## 모니터링 지표

### 1. 사용률 추적
- Gemini 사용 비율
- Claude 전환 비율
- 평균 응답 시간

### 2. 비용 분석
- 일일 API 비용
- 쿼리당 평균 비용
- LLM별 비용 분포

### 3. 품질 지표
- 응답 정확도
- 사용자 만족도
- 오류 발생률

## 향후 개선 계획

### Phase 1: 지능형 라우팅
- [ ] ML 기반 쿼리 복잡도 분석
- [ ] 동적 임계값 조정
- [ ] 사용자별 선호도 학습

### Phase 2: OCR 통합
- [ ] 스캔 문서 OCR 처리
- [ ] Gemini에서 OCR 텍스트 활용
- [ ] 정확도 향상

### Phase 3: 하이브리드 처리
- [ ] Gemini 초기 요약 + Claude 상세 분석
- [ ] 결과 통합 및 품질 향상
- [ ] 비용-품질 최적화

### Phase 4: 캐싱 강화
- [ ] 의미적 유사도 기반 캐싱
- [ ] 자주 묻는 질문 사전 처리
- [ ] Redis 기반 분산 캐시

## 문제 해결

### 1. Gemini 텍스트 추출 실패
- 원인: 스캔된 PDF, 복잡한 레이아웃
- 해결: 자동으로 Claude로 전환

### 2. 응답 시간 지연
- 원인: 대용량 PDF 처리
- 해결: PDF 최적화 적용

### 3. 비용 초과
- 원인: Claude 과다 사용
- 해결: 쿼리 패턴 분석 및 캐싱

## 결론

이 Multi-LLM 아키텍처는 다음을 제공합니다:
- **90% 비용 절감** (단순 쿼리)
- **높은 정확도 유지** (복잡한 분석)
- **자동 품질 보장** (폴백 메커니즘)
- **확장 가능한 구조** (새로운 LLM 추가 용이)

시스템은 사용자가 인지하지 못하는 사이에 최적의 LLM을 선택하여 비용 효율적이면서도 정확한 답변을 제공합니다.