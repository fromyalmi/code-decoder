# 개발 일지 (devlog)

세션별 부채 발견→상환·실측 검증·배운점 기록. 시간 역순(최신이 위).
현재 유효 지침·라우팅은 `CLAUDE.md` 참조.

---

## 2026-05-31 세션3 이어서 (3-B-1 / 3-B-2 결과 시각화)

### 산출물

- **3-B-1**: `components/result/` 디렉토리 신설 — ResultView + ForestPanel + TreePanel. DashboardPage showing 분기에서 ResultView 단독 렌더(DashboardLayout 내장). pillar1=forest 텍스트, pillar4=tree 텍스트 + key_concepts 카드.
- **3-B-2**: LeafColumn + LeafLine + FolderTree 추가. pillar1에 FolderTree(tags 칩) 적층, pillar12에 LeafColumn(라인별 박스: 코드↑ short↓ 조건부 deep). EmptyPlaceholder 제거(사용처 0).

### TDDoc 가정 vs 실제 schema 차이 정책 결정 (4건)

- **`tree: TreeCard[]` 가정 → 실제 string** — 자유 줄글 단일 문단(토큰상한에 잘리기도). 카드 정체성은 `key_concepts[]`로 실현(TreePanel = tree 텍스트 + 카드 그리드). 백엔드 무수정.
- **`tier` enum 가정 → schema 부재** — 프론트가 `line_explanations` + `deep_leaves`를 `line_no`로 병합해 도출(deep 존재→deep_core, 없으면→short). `deep_pinned`는 3-C로 미룸.
- **`TagItem` 가정 → 실제 string[]** — FolderTree 단순화(칩 나열만). 트리 구조(├─ fn...)·카테고리·user_edited는 백엔드 schema 보강 시 가능, post-MVP.
- **`LeafExpansion` 타입 미정의** — leaf expand 콜백·Map<lineNo, LeafExpansion>·LeafExpandModal 모두 3-C로 미룸. 본 세션 LeafLine은 표시 전용.

### 검증 메서드

- **mock 보강** — vi.hoisted + Promise 외부 resolve 패턴(이후 페이지 테스트의 본). globals:false 환경에서 `afterEach(cleanup)` 명시 등록.
- **가짜 GREEN 점검** — 신규 단언 텍스트가 다른 위치(forest/key_concepts 등)와 겹치는지 표로 확인 후 RED 진입. 3-B-2에서 7개 단언 모두 우연 매치 0 검증.
- **line_mapping 사전 검증** — 백엔드 code_cleaner + LLM 프롬프트 발췌로 `line_no`가 original 기준임을 확인. `codeOriginal.split('\n')[lineNo-1]`로 충분, line_mapping 미사용 결정. 라인 어긋남 버그 사전 차단.

### 실측 관찰 (post-MVP 후보)

- **tags 칩(1×) ↔ key_concepts 카드(4×) 내용 겹침** — 백엔드 LLM이 유사 항목을 두 자리에 출력하는 데이터 특성. post-MVP: tags 개수/길이 제한 또는 역할 분리 검토.
- **12× LeafColumn deep 본문 길이로 스크롤 부담** — 라인 많고 deep_core 많을수록 누적. 3-C에서 deep 접힘/펼침 인터랙션으로 해소 예정.
- **(3-B-1 잔여) 카드 본문 코드조각 미분리** — `key_concepts` schema에 코드 필드 없음. 자연어와 코드(예: `from openai import ...`)가 같은 definition 문자열에 섞여 렌더. post-MVP: schema 보강 + monospace 코드박스 분리.
- **(3-B-2) FolderTree 트리 구조(├─ fn...) 데이터 부재** — tags가 단순 string[]. 카테고리/관계 보강 시 트리 구조 가능, post-MVP.

### 배운점

- **TDDoc 가정 vs 실제 schema 사전 검증의 가치** — 4건의 차이를 Plan 진입 전 결정해 "TDDoc 시그니처 그대로 구현"의 함정 회피. 특히 TreeCard 폐기 → key_concepts로 정체성 이전이 결정적.
- **시안 베끼기 가드** — 카드 둥근 모서리/보라 톤은 SSoT 토큰(픽셀 미학·radius 0·--shadow-pixel)이 우선. 시안은 정체성 참고용이지 픽셀 사본 아님.
- **`cache_hit` JSON 덤프 단언의 한계** — 3-A에 임시로 박은 단언이 3-B-1 RED에 정확히 교체 필요(TODO 주석 효과). 임시 단언엔 항상 교체 시점 주석 필수.
- **A안 단언 결함(getAllByText 정확매칭 vs 여러 줄 단일노드의 substring 매치)** — 3-B-2.5에서 `getAllByText('def hi():').toHaveLength(2)`로 LeafLine + CodeBlock 동시 검증을 시도했으나, testing-library default exact match는 노드 전체 textContent와 정확 비교라 여러 줄 든 CodeBlock `<code>` 노드의 substring을 매치하지 못함(length 영원히 1). 정규식 `/def hi\(\):/`로 substring 매치하여 정정. Plan 단계에서 이 정책을 정확히 인지하고도 A안으로 결론낸 추론 오류 — **사실 인지와 추론 결과의 정합성**을 항상 점검해야 함. 구현 자체는 RED 시점부터 정상이었고 단언만 결함.

---

## 2026-05-30 세션3 (3-A DashboardPage)

### 부채 발견→상환 (4건)

- **vitest 셋업 중 TS6↔openapi-typescript peer 충돌 발견** — `--legacy-peer-deps`로 임시 상환. 근본 해결(openapi-typescript TS6 지원 메이저 / Vercel install 가드)은 발표 전 필수 TODO(`CLAUDE.md` 참조).
- **@testing-library/dom peer 누락** (legacy-peer-deps 부작용으로 install 시 미수렴) — `npm install --save-dev --legacy-peer-deps @testing-library/dom`로 명시 보강(별도 chore 커밋).
- **globals:false 정책 시 testing-library 자동 cleanup 미등록** — `src/test-setup.ts`에 `afterEach(cleanup)` 명시 등록으로 테스트 간 DOM 누적 해소(별도 chore 커밋).
- **refreshMe→ProtectedRoute splash 통합 버그** — mock 10/10 그린이었으나 실측 시 분석 성공 직후 DashboardPage 언마운트로 입력코드·JSON 덤프 0프레임 소실. 원인: `isBootstrapping`이 최초 부트스트랩이 아니라 모든 refreshMe에 토글되는데 ProtectedRoute가 user 유무와 무관하게 splash 띄움. 상환: `(isBootstrapping && !user)`로 가드 1줄 보강.

### 실측 검증 (골든패스)

- **9번 (429 인라인)**: `daily_used=10` DB 수정 후 분석 클릭 → "🦜 오늘 분석은 다 썼어" 인라인 표시 + idle 유지 확인. DAILY_LIMIT_EXCEEDED code→카피 매핑 실측 검증.
- **10번 (라우팅)**: 보호 라우트 "준비 중" 정상, `/login`·`/`·각 페이지 정상, 미정의 `/foo`만 빈 화면(404 fallback 라우트 부재 — 3-A 범위 외, MVP 마무리 항목).

### 배운점

- **mock 그린은 필요조건이지 충분조건 아님** — 통합 버그(부모 라우트의 BootSplash 가드 같은 환경 결합)는 mock 단위에선 잡히지 않는다. 실측 골든패스를 RED/GREEN 사이클과 분리 운영해야 한다.
- **이름·의도 불일치는 잠재 결함의 씨앗** — `isBootstrapping`이 "최초 부트스트랩"을 의도한 이름이지만 "모든 me 갱신"에 토글되며 splash를 잘못 띄웠다. silent refresh 개념의 명시적 분리 필요(후속).
- **조사 단계 체크리스트에 `package.json`(scripts·devDeps) 필수 포함** — "명령 존재 가정"이 무너지면 RED/GREEN 시작 자체가 막힌다. 인프라 점검을 코드 점검과 동등하게 다룬다.
