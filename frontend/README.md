# 포트폴리오 Q&A 챗봇 프론트엔드

React + TypeScript + Vite로 구축된 투자 포트폴리오 Q&A 챗봇의 프론트엔드입니다.

## 기술 스택

- **React 19** - UI 라이브러리
- **TypeScript** - 타입 안정성
- **Vite** - 빌드 도구
- **Tailwind CSS** - 스타일링
- **React Router** - 라우팅
- **Axios** - API 통신
- **Chart.js** - 데이터 시각화

## 시작하기

### 개발 환경 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행 (http://localhost:4000)
npm run dev
```

### 빌드

```bash
# 프로덕션 빌드
npm run build

# 빌드 미리보기
npm run preview
```

## 프로젝트 구조

```
src/
├── components/      # 재사용 가능한 컴포넌트
│   ├── chat/       # 채팅 관련 컴포넌트
│   ├── common/     # 공통 컴포넌트
│   └── charts/     # 차트 컴포넌트
├── contexts/       # React Context
├── pages/          # 페이지 컴포넌트
├── services/       # API 서비스
├── types/          # TypeScript 타입 정의
└── hooks/          # 커스텀 훅
```

## 주요 기능

### 1. 홈페이지 (`/`)
- 서비스 소개
- 주요 기능 안내
- 예시 질문 제공

### 2. 채팅 페이지 (`/chat`)
- 실시간 Q&A 채팅
- 응답 소스 표시
- 로딩 상태 표시

### 3. 테스트 페이지 (`/test`)
- API 연결 상태 확인
- 백엔드 서비스 헬스체크
- 샘플 API 테스트

## 환경 변수

`.env` 파일을 생성하고 다음 내용을 설정하세요:

```env
# API 서버 URL
VITE_API_URL=http://localhost/api
```

## API 연동

백엔드 API는 다음 엔드포인트를 사용합니다:

- `/api/chat` - 채팅 메시지 전송
- `/api/documents/search` - 문서 검색
- `/api/news/search` - 뉴스 검색
- `/api/health` - 헬스체크

## 개발 가이드

### 컴포넌트 추가

새로운 컴포넌트 추가 시:

1. `src/components` 내 적절한 폴더에 생성
2. TypeScript 인터페이스 정의
3. Tailwind CSS 클래스 사용

### API 추가

새로운 API 추가 시:

1. `src/services/api.ts`에 함수 추가
2. `src/types/index.ts`에 타입 정의
3. 에러 처리 로직 포함

## 문제 해결

### CORS 에러
개발 환경에서는 Vite 프록시가 자동으로 처리합니다.
프로덕션에서는 Nginx 설정을 확인하세요.

### 빌드 에러
```bash
# 캐시 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```