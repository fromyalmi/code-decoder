# CLAUDE.md — Code Decoder MVP

---
# 프로젝트: Code Decoder MVP

## 프로젝트 개요
비전공자 AI 학습자를 위한 코드 해설 웹앱.
코드를 입력하면 OpenAI API가 숲(전체 목적) / 나무(라인별 해설) / 돋보기(핵심 개념)
3단계로 구조화된 해설을 JSON으로 반환하고, 각 탭에서 렌더링한다.

## ⛔ 절대 규칙 (위반 금지)

1. `.env` 파일을 절대 생성·읽기·수정·커밋하지 마라. API 키는 사용자가 직접 관리한다.
2. `any` 타입 사용 금지. 모든 타입은 `src/types/index.ts`에서 가져온다.
3. `localStorage` 사용 금지. 영속 저장은 반드시 IndexedDB(`idb-keyval`)만 사용한다.
4. Redux, Zustand, Recoil 등 외부 상태 관리 라이브러리 설치 금지. `useReducer + Context`만 사용한다.
5. `console.log` 디버그 코드를 커밋에 남기지 마라. 에러 로깅은 `console.error`만 허용.
6. 컴포넌트 하나에 비즈니스 로직과 UI를 함께 작성하지 마라. 로직은 `hooks/`로 분리한다.
7. 새 패키지 설치 전 반드시 사용자에게 확인을 요청하라.
8. `SavedCard`와 `HistoryEntry`의 `userId` 필드는 MVP에서 반드시 `"local"` 문자열로 고정한다. 다른 값으로 채우거나 생략하지 마라.

---

## 🏗 아키텍처

### 기술 스택
- **Framework**: React 18 + TypeScript (strict mode)
- **Build**: Vite 5
- **Styling**: Tailwind CSS v3 (커스텀 토큰 포함, 아래 디자인 시스템 참조)
- **Icons**: `material-symbols` (Material Symbols Outlined) — Lucide 사용 금지
- **Storage**: `idb-keyval` (IndexedDB 래퍼)
- **AI**: OpenAI API `gpt-4o-mini`, `response_format: { type: "json_object" }`
- **Deploy**: Vercel

### 폴더 구조
```
src/
├── components/
│   ├── layout/       # AppShell, Header, Sidebar, BottomNav, MainLayout
│   ├── views/        # ForestView, TreeView, ConceptView, MyCardsView, HistoryView
│   └── ui/           # ConceptCard, TreeRow, ComplexityBadge, ErrorBanner,
│                     # LoadingOverlay, ToastNotification, TabNav, ExportButton
├── context/
│   └── AppContext.tsx # useReducer + Context (전역 상태)
├── hooks/
│   ├── useAnalyzer.ts   # OpenAI API 호출 오케스트레이션
│   ├── useCards.ts      # 도감 카드 CRUD
│   ├── useHistory.ts    # 히스토리 CRUD
│   └── useToast.ts      # 알림 상태 관리
├── services/
│   └── openaiService.ts # fetch + 재시도 로직 (Exponential Backoff)
├── db/
│   ├── stores.ts        # createStore (cards / history)
│   ├── cardDB.ts        # 카드 CRUD + 중복 체크
│   └── historyDB.ts     # 히스토리 CRUD + 50건 제한
├── utils/
│   ├── validateResponse.ts  # API 응답 스키마 검증
│   ├── exportMarkdown.ts    # MD 파일 생성 + 다운로드
│   └── clipboard.ts         # Clipboard API + 폴백
├── constants/
│   └── prompts.ts       # SYSTEM_PROMPT 상수, PROMPT_VERSION
└── types/
    └── index.ts         # 모든 공유 타입 (AnalysisResult, SavedCard 등)
```

### 레이아웃 구조
```
[데스크탑 lg+]
┌──────────────────────────────────────────────────┐
│ Header (fixed, h-16)                             │
├───────────┬──────────────────┬───────────────────┤
│ Sidebar   │  코드 에디터 패널  │  분석 결과 패널   │
│ (w-64)    │  + Analyze 버튼  │  (탭 + 카드)      │
└───────────┴──────────────────┴───────────────────┘

[모바일 ~ md]
┌──────────────────┐
│ Header (h-14)    │
├──────────────────┤
│ 코드 에디터       │
│ Analyze 버튼      │
│ 탭 네비           │
│ 분석 결과         │
├──────────────────┤
│ BottomNav (h-16) │
└──────────────────┘
```

---

## 🎨 디자인 시스템

### 컬러 토큰 (tailwind.config.ts에 반드시 등록)
```js
colors: {
  primary: "#3525cd",
  "primary-container": "#4f46e5",
  "on-primary": "#ffffff",
  "primary-fixed": "#e2dfff",
  secondary: "#4648d4",
  "secondary-container": "#6063ee",
  "on-surface": "#191c1d",
  "on-surface-variant": "#464555",
  surface: "#f8f9fa",
  "surface-container": "#edeeef",
  "surface-container-low": "#f3f4f5",
  "surface-container-lowest": "#ffffff",
  "surface-container-high": "#e7e8e9",
  "outline-variant": "#c7c4d8",
  error: "#ba1a1a",
}
```

### 타이포그래피
- **Headline**: `font-family: 'Manrope', sans-serif` — 카드 제목, 섹션 타이틀
- **Body/Label**: `font-family: 'Inter', sans-serif` — 설명, 태그, 버튼

### 개념 카드 구조 (ConceptCard 컴포넌트)
```
┌─────────────────────────────────────────┐
│ [아이콘 아바타 48px]  카드 제목           │ ← bookmark_add 버튼 우상단
│                     [태그1] [태그2]      │
│                                         │
│ 설명 텍스트 (on-surface-variant, sm)     │
│                                         │
│ ─────────────────────────────────────── │
│ CORE COMMANDS                           │
│ [split()]  [for..in]  [complexity++]    │ ← 코드 블럭 스타일
└─────────────────────────────────────────┘
```

### 탭 네비게이션 스타일
- 컨테이너: `bg-surface-container-high rounded-full p-1.5`
- 비활성 탭: `text-on-surface-variant hover:bg-white/50`
- 활성 탭: `text-primary bg-surface-container-lowest` + 그림자

---

## 🔌 도메인 컨텍스트

### 핵심 비즈니스 용어
| 용어 | 의미 |
|------|------|
| 숲 (Forest) | 코드 전체 목적 요약 (1~3문장) |
| 나무 (Tree) | 라인별 코드 해설 타임라인 |
| 돋보기 (Concept) | 핵심 개념 카드 3~5개 |
| 도감 (MyCards) | 사용자가 저장한 개념 카드 컬렉션 |
| 히스토리 (History) | 과거 분석 결과 목록 (최대 50건) |
| logic_type | 코드 라인 분류: 선언/조건/반복/함수호출/API호출/반환/임포트/설정/기타 |

### OpenAI 응답 스키마 (이 형태가 아니면 에러)
```typescript
interface AnalysisResult {
  forest_view: string;
  complexity: "low" | "medium" | "high";
  language: string;
  tree_view: Array<{
    line: number;
    code: string;
    explanation: string;
    logic_type: string;
  }>;
  concept_view: Array<{
    term: string;
    description: string;
    core_commands: string[];
  }>;
}
```

### 데이터 흐름
```
CodeEditor (입력) → useAnalyzer → openaiService.analyze()
  → validateResponse() → AppContext dispatch("ANALYSIS_SUCCESS")
  → 각 View 렌더링

ConceptCard "저장" 클릭 → useCards.save() → cardDB.save() → IndexedDB
히스토리 자동 저장 → useHistory.save() → historyDB (50건 초과 시 자동 삭제)
```

### 환경 변수
```
VITE_OPENAI_API_KEY   # .env에 존재, Claude는 절대 건드리지 않음
```

---

## 🛠 빌드 & 개발 명령어

```bash
npm run dev        # 개발 서버 (http://localhost:5173)
npm run build      # 프로덕션 빌드 → dist/
npm run preview    # 빌드 결과 로컬 미리보기
npm run test       # Vitest 단위 테스트
npm run typecheck  # tsc --noEmit (타입 에러 확인)
```

### 설치 명령어 (패키지 추가 시 참고)
```bash
npm install idb-keyval @material-symbols/font
npm install -D tailwindcss postcss autoprefixer vitest @testing-library/react
```

---

## 📐 코딩 컨벤션

### 네이밍
- **컴포넌트 파일**: PascalCase (`ConceptCard.tsx`)
- **훅 파일**: camelCase, `use` 접두사 (`useAnalyzer.ts`)
- **상수**: UPPER_SNAKE (`SYSTEM_PROMPT`, `MAX_HISTORY`)
- **타입/인터페이스**: PascalCase, `I` 접두사 없음 (`AnalysisResult`)
- **이벤트 핸들러**: `handle` 접두사 (`handleAnalyze`, `handleSaveCard`)

### 컴포넌트 패턴
```tsx
// ✅ 올바른 패턴: Props 타입 명시, 기본값 포함
interface ConceptCardProps {
  concept: ConceptItem;
  isSaved: boolean;
  onSave: (concept: ConceptItem) => void;
}
export const ConceptCard = ({ concept, isSaved, onSave }: ConceptCardProps) => { ... };

// ❌ 금지: props: any, 인라인 타입, default export만 (named export 병행 권장)
```

### 커밋 메시지 (Conventional Commits)
```
feat: 개념 카드 저장 기능 추가
fix: API 재시도 로직 429 처리 버그 수정
style: ConceptCard 레이아웃 조정
refactor: useAnalyzer 에러 처리 분리
chore: idb-keyval 패키지 설치
```

### 주석 규칙
- 모든 주석은 한국어로 작성
- 함수/훅 상단에 한 줄 역할 설명 필수
- 복잡한 로직(재시도, 스키마 검증 등)은 인라인 주석 추가

---

*CLAUDE.md v1.1 | Code Decoder MVP | BBLB | 2026.04.16 (절대 규칙 #8 추가)*
