# Code Decoder MVP — Stage 4·8 Design Decisions

> **문서 상태**: Stage 4 와이어프레임 1차 + Stage 8 디자인 2차 결정 통합본 (경량 참조용)
> **버전**: v0.2 (Stage 8 패치 — D-1·D-2 닫힘 + 디자인 토큰 2차 확정 + O-10 닫힘)
> **작성일**: 2026-05-26 (v0.1: 2026-05-17 Stage 4 시점)
> **출처**:
>   - `Code_Decoder_Wireframe_Full_UC-1_Flow_v2.pdf` (UC-1 Flow, 7페이지 — 13p LEGEND) — Stage 4 1차
>   - `Code_Decoder___Stage_8___PRINT.pdf` (Stage 8 디자인 2차, 30페이지 — 안건 A·B·C·D) — Stage 8 2차
> **참조 SSoT**:
>   - `01-discovery-summary-v4.md` (v4)
>   - `02-PRD.md` (v0.10 — §5.6 FR-GAME · §5.7 FR-BILLING · NFR-8 픽셀 미학)
>   - `03-ux-flow.md` (v0.2 — Flow-1~5 + EC-1~5)
>   - `07-technical-design.md` (v0.1 — 특히 §35 프론트 6대 원칙 · §35.2 컴포넌트 분해 · §38.3 Stage 9 진입 게이트 · §38.4 후속 단계 인계)
> **소유자**: 코뉴(제품 오너)

> **이 문서의 목적**: 와이어프레임·시안 PDF 원본은 토큰 비용이 크다. Stage 9(TDDev) 세션이 PDF를 매번 읽지 않고도 디자인 토큰·레이아웃·페이지 props를 참조할 수 있도록 핵심만 텍스트로 추출한 경량 SSoT. **PDF 원본은 보관용**, 상시 참조는 이 파일.

> **HC-8 표기 규약**: 본 문서에서 *Stage 7 = TDDoc* (`07-technical-design.md`), *Stage 9 = TDDev* (구현 단계). 약어 "TDD" 단독 사용 금지 — 매번 *TDDoc* 또는 *TDDev*로 명시.

---

## §1. 와이어프레임·시안 산출물 범위

Stage 4(1차)는 UC-1 해피패스만 다뤘고 검색·아카이브·설정·도감 화면이 미작성으로 남았던 게 §8 D-2의 핵심 부채였다. Stage 8(2차)에서 그 부채를 청산했고, 추가로 데스크톱 레이아웃 4-옵션 비교(D-1) · 디자인 토큰 6항목 2차 확정(TRD §18.2 B-3) · Flow-1 온보딩 시퀀스(03 ①-1·①-2) · 시스템 컴포넌트(Toast 8종·Tooltip 4종) 까지 한 번에 처리했다. 두 단계 산출물을 안건 단위로 정리하면 아래 표가 된다.

| 단계 | 안건 | 화면 수 | 범위 | 닫힌 결정 |
|---|---|---|---|---|
| Stage 4 | UC-1 해피패스 + LEGEND | 7 | 로그인 · 3종 대시보드(A/B/C) · Loading · Analyzed · LEGEND | (초안) |
| Stage 8 — 안건 A | 데스크톱 레이아웃 4-옵션 + 변형 | 5 | Triptych / Code Center / **Zoom Pillars ✅** / Zoom Pillars · LEAF 중앙 변형 / Workbench Split | **D-1** |
| Stage 8 — 안건 B | UC-2/UC-3 + 상태 모달 + 반응형 | 9 | 검색 모달 ⌘K · 검색 결과(+빈 결과) · 아카이브 · 도감 · 설정 · 분석 진행 · 차단·결정 모달 4종 · 반응형 1-col | **D-2 (부분)** |
| Stage 8 — 안건 C | 디자인 토큰 2차 확정 | 6 | 중립색 9-step · 액센트+상태 · 간격 4px · 픽셀 보더 · 모션 steps() · reduced-motion fallback | **B-3 (TRD §18.2)** |
| Stage 8 — 안건 D | Flow-1 온보딩 + 누락 화면·시스템 | 10 | Landing · 회원가입/로그인 · 환영 · 학습자 레벨 4지선다 · 분석 상세 페이지 · EC-2 에러 · EC-4 방패 풀스크린 · EC-5 14일 복구 · Toast 8종 · Tooltip 4종 | **D-2 (잔여)** |

Stage 8 30화면 모두 1280×800 기본(반응형 변형은 별도 표기)이고 안건 B8(반응형 1-col)이 `<900px` 브레이크포인트 검증용이다.

---

## §2. 레이아웃 — Zoom Pillars (1× → 4× → 12× 좌→우) · D-1 ✅ 닫힘

> **Stage 4 미결**: 데스크톱 레이아웃 A(Triptych) vs B(Code Center) 택1 — Stage 8에서 *4-옵션 + 변형 비교* 후 **새 후보 C 채택**.

Stage 4 시점의 A·B 두 후보(Triptych 동등 비중 / Code Center 잎 중심)는 *왜 3계층인가*라는 메타포를 시각 위계로 충분히 설명하지 못했다. Triptych는 세 컬럼이 동등해서 어디부터 봐야 하는지 모호하고, Code Center는 잎이 거대해진 만큼 숲·나무가 주변부로 밀려 *전체 그림 먼저*라는 학습 흐름과 어긋났다. Stage 8에서 4개 옵션(A1 Triptych · A2 Code Center · A3 Zoom Pillars · A4 Workbench Split)에 LEAF-중앙 변형(A3b)까지 펼쳐 보고, **A3 Zoom Pillars** 가 확정안으로 채택됐다.

확정안의 핵심은 컬럼 자체가 *줌 레벨을 시각화*한다는 점이다. 좌측 FOREST 컬럼 헤더에 `1×`, 중앙 TREE 컬럼 헤더에 `4×`, 우측 LEAF 컬럼 헤더에 `12×` 가 라벨로 박혀 있어 *왼쪽에서 오른쪽으로 갈수록 확대*된다는 메타포가 컬럼 배치 자체로 전달된다. 이게 Triptych의 *동등 비중* 모호함과 Code Center의 *중앙 비대칭* 둘 다를 해결한다. 좌측에 코뉴 마스코트가 *"여기까지 보면 전체 그림이 와닿아 🦜"* 라는 인-라인 코칭 메시지를 띄워, 비전공자에게 *Forest를 먼저 보라*는 학습 동선을 픽셀-네이티브하게 강제한다.

컬럼 너비 비율은 균등 분할(약 1:1:1)에서 출발하되, *내용물 차이로 자연 강조*된다 — FOREST는 짧은 텍스트 + 폴더 트리 + TAGS, TREE는 5개 구조 카드 + 도감 4슬롯, LEAF는 9~12 라인 + 라인별 해설로 LEAF가 시각적으로 가장 정보 밀도 높다. *명시적 너비 강조 없이도 LEAF가 자연스럽게 작업 중심이 되는* 균형이 Triptych보다 우위.

반응형 동작은 변경 없음 — `<900px`에서 1-컬럼 세로 적층(안건 B8에서 검증). 컬럼 순서는 모바일에서도 FOREST → TREE → LEAF 그대로 (역순 X). CTA는 Sticky Bottom.

### §2.1 미채택 옵션 보존 사유

A1·A2·A4는 *왜 안 채택됐는지*를 같이 적어둬야 Stage 9 진입 후 *"왜 A3로 했더라"* 라는 재의문이 차단된다.

- **A1 Triptych (동등 비중)** — 세 컬럼 너비 균등 + 줌 라벨 없음. *진입점이 모호*하다는 게 핵심 약점. 사용자가 어디부터 읽어야 할지 신호 부재.
- **A2 Code Center (Hero 코드)** — 중앙 코드 영역이 너무 거대해서 숲·나무가 *마진 노트* 처럼 종속됨. 학습 흐름(Forest 먼저)과 정반대 위계.
- **A3b Zoom Pillars · LEAF 중앙 변형** — A3와 동일한 줌 메타포지만 LEAF를 중앙으로 보냄. *작업 중심 흐름*에는 합리적이나 학습자 입장에서 *Forest 먼저* 라는 우선순위가 시각적으로 약해지고, 코칭 메시지 위치도 어색해 비채택.
- **A4 Workbench Split (IDE 2-pane)** — 좌측 사이드바 + 우측 3계층 탭의 IDE 풍 구조. *비전공자 페르소나*(코딩 1개월 차)에게 IDE 풍은 과하다고 판단. Closed Beta 이후 *고급 모드*로 재검토 여지는 있음.

### §2.2 ⓘ 컨테이너 구현 — O-9 자동 닫힘

D-1이 *Zoom Pillars 단일 채택*으로 닫히면서 TDDoc §35.2 운영 안건 **O-9**(`<DashboardLayout>` Triptych vs Code Center 분기 구현)도 자동 닫힌다 — *분기 자체가 없어졌다.* `<DashboardLayout>`은 *Zoom Pillars 단일 구현*으로 단순화되고, 자식 컴포넌트(`<ForestPillar>` · `<TreePillar>` · `<LeafPillar>`) 인터페이스는 변동 없음. 컨테이너 prop 차원도 줌 라벨(`1× / 4× / 12×`)을 *고정 상수*로 두면 됨 — 사용자 토글 불필요.

---

## §3. 3계층 줌 메타포 (3 Zoom Levels)

변경 없음 — Stage 4 v0.1과 동일. *Zoom Pillars 레이아웃이 이 메타포의 시각 구현*임이 v0.2에서 비로소 명시됐다는 점만 추가.

| 계층 | 줌 | 역할 | Zoom Pillars 위치 |
|---|---|---|---|
| 🌲 숲 FOREST | `1×` | 전체 목적 요약 (Overview) | 좌측 컬럼 |
| 🌳 나무 TREE | `4×` | 핵심 개념 = 구조 (Key Concepts) | 중앙 컬럼 |
| 🍃 잎 LEAF | `12×` | 라인별 해설 — 한 줄 = 한 잎사귀 | 우측 컬럼 |

명칭 변경 기록은 v0.1과 동일 — 세 번째 층 `가지(Branch)` → `잎(Leaf)`. 사유는 Tree/Branch 깊이감 혼동 해소 + "1라인 = 1잎사귀" 1:1 매핑. (PRD v0.4 이후·UX Flow v0.2·Discovery v2.1 이후에 모두 반영 완료.)

---

## §4. 색상 토큰 — 액센트 (Accent Roles) · 안건 C2

> PRD NFR-8의 추상 4색 팔레트(orange/yellow/green/black)를 구체 hex로 확정한 것 — NFR-8과 충돌 없는 구체화. v0.1 4색에 *soft 변형(alpha 22)* 을 추가해 배경 채움까지 토큰화.

| 토큰 | hex | soft 변형 | 역할 | 금지 |
|---|---|---|---|---|
| ORANGE | `#E8631A` | alpha 22 (bg fill) | CTA · Active · Link · Hover Border · Primary 컬럼 스트립 · DEEP 좌보더 | — |
| YELLOW | `#F5C200` | alpha 22 (bg fill) | 🐛 캐러필러 · 🔥 Streak · 배지 · 강조 인라인 · ◐ ANALYZING | — |
| GREEN | `#5BA020` | alpha 22 (bg fill) | ● Analyzed / Success 상태에만 | **CTA·내비 사용 금지** |
| BASE DARK | `#1A1A1A` | — | 베이스 다크 테마 (PRD NFR-8) · 본문 bg | — |

soft 변형의 용도는 *주황 카드 배경* · *노랑 배지 배경* · *초록 완료 토스트 배경* 같이 *액센트 색의 약한 면 채움*. 알파값 `0x22`(약 13%)를 일괄 적용해 다크 위에서도 색감이 자연스러우면서 색맹·HSP 사용자에게 과도하지 않게 함.

---

## §5. 색상 토큰 — 중립색 9-step (N00~N80) · 안건 C1 신규

다크 테마는 *검은색 한 가지*로 절대 안 끝난다 — 패널·보더·텍스트·디스에이블이 전부 다른 명도를 요구한다. v0.1은 BASE DARK(`#1A1A1A`)·EMPTY(`#3C3C3C`)·READY(`#888888`) 3톤만 박혀 있어 카드 stacking · 호버 bg · 텍스트 muted 등이 *구현자 재량*으로 흩어질 위험이 있었다. 안건 C1에서 9-step 스케일로 박아 *모든 그레이는 N00~N80 중 하나*가 되도록 했다.

| 토큰 | hex | 용도 |
|---|---|---|
| N00 | `#0E0E0E` | void · canvas behind everything |
| N10 ⭐ | `#1A1A1A` | **BASE** · body bg · NFR-8 강제 |
| N20 | `#222222` | raised panel · code slot |
| N30 | `#2C2C2C` | hover bg · interactive |
| N40 | `#3C3C3C` | border · **EMPTY slot** (§6 참조) |
| N50 | `#5A5A5A` | text muted · disabled |
| N60 | `#888888` | text dim · **READY 상태** (§6 참조) |
| N70 | `#B0B0B0` | label · secondary text |
| N80 | `#E5E5E5` | text primary |

WCAG AA(명도 대비 ≥ 4.5) 검증치는 N80 on N10 = 15.3:1 (본문), N60 on N10 = 5.6:1 (디스에이블 텍스트도 통과), N50 on N10 = 3.0:1 (본문 사용 금지·플레이스홀더 전용). 즉 *N50은 디자인 토큰이지만 본문 텍스트에 쓰면 접근성 위반* — 이 규칙을 디자이너·구현자 모두 기억해야 한다.

---

## §6. 상태 토큰 (State Tokens)

v0.1에서 이미 잘 박혔던 5개 토큰을 안건 C2에서 *중립색 9-step과의 연결*까지 명시해 재확정.

| 상태 | hex | 매핑 | 적용 |
|---|---|---|---|
| READY | `#888888` | N60 | 대시보드 분석 전 |
| ◐ ANALYZING | `#F5C200` | YELLOW | 로딩 — 프로그레스 + 스켈레톤 시머 |
| ● ANALYZED | `#5BA020` | GREEN | 완료 상태에만 |
| ▌ DEEP | `#E8631A` | ORANGE 3px 좌보더 | 핵심 5개 깊은 해설 (Leaf deep_core·deep_pinned) |
| —— EMPTY | `#3C3C3C` | N40 | 대기 슬롯 |

---

## §7. 게이미피케이션 토큰 (Gamification Tokens)

변경 없음 — Stage 4 v0.1과 동일. 상세 규칙은 PRD §5.6 FR-GAME 본체, 본 §는 시각 표현 요약.

| 토큰 | 시각 동작 |
|---|---|
| 🐛 CATERPILLAR | 분석 1회 → +1 · 결과 1초 후 픽셀 애니메이션 (motion-pop · steps(8) · 1200ms) |
| 🛡 SHIELD | 캐러필러 20 → 자동 변환 · Streak 끊김 1회 방어 |
| 🔥 STREAK | 매일 분석 1회로 유지 · 자정 KST 배치 |
| 📘 도감 (Key Concepts) | 새 개념 UPSERT · 누적 컬렉션 (5축 분류 — 🔁 패턴 · 📦 라이브러리 · 📐 자료/함수 · ⚙ 알고리즘 · 🏠 도메인) |
| 📁 ARCHIVE | 분석 자동 저장 · UUID URL 북마크 |
| 🔍 ADDITIONAL N/5 | 추가 깊은 해설 카운터 · 5번째에 분석 1회 차감 |
| 「호칭」 | 레벨 + 진척에 따라 동적 변경 (예: 코뉴 해치기 L1 → 가지의 코뉴 L2 → 첫 비행 코뉴 L3 → 왕관 코뉴 L4) |

STATS BAR 원칙은 변경 없음 — 분석 전 빈 상태에서도 누적 자산(Streak·캐러필러·도감·아카이브)은 상단 Stats Bar에 *상시 노출*.

---

## §8. 간격 토큰 — 4px Base (space-0 ~ space-8) · 안건 C3 신규

픽셀 미학(NFR-8)에서 간격은 *32×32 sprite 그리드의 정수배 정렬*이 필수다. 4px가 기본 단위인 이유 — 32×32 sprite가 8개의 4px 칸으로 떨어지고, sprite 픽셀 정렬이 깨지지 않아야 *AI 슬롭*(둥글둥글한 anti-aliased UI)이 차단된다. 9-step 스케일을 박아 *모든 간격은 space-0~space-8 중 하나*가 되도록 강제.

| 토큰 | 값 | 용도 |
|---|---|---|
| space-0 | `0px` | 인접 없음 |
| space-1 | `4px` | 아이콘 + 라벨 갭 |
| space-2 | `8px` | 인라인 그룹 · 칩 간격 |
| space-3 | `12px` | 카드 내부 패딩 (compact) |
| space-4 ⭐ | `16px` | **카드 패딩 · 컬럼 갭 (디폴트)** |
| space-5 | `24px` | 섹션 사이 간격 |
| space-6 | `32px` | 1 sprite · 헤더 높이 |
| space-7 | `48px` | 큰 카드 패딩 |
| space-8 | `64px` | 2 sprite · 페이지 여백 |

⚠ **4px 그리드 외 값(예: 6px, 10px, 14px) 사용 금지** — sprite 픽셀 정렬이 깨진다. 폰트 `line-height`만 예외 허용(가독성을 위해 1.4·1.5 등 비-4px 배율 필요).

---

## §9. 보더·라디우스 토큰 · 안건 C4 신규

픽셀 미학의 가장 가시적 규약 — **`border-radius` 사용 금지**(NFR-8 AI 슬롭 차단의 1순위). 모든 모서리는 *radius 0*. 보더는 두께만 3단계로 구분.

| 토큰 | 값 | 용도 |
|---|---|---|
| border-thin | `1px solid` | 보조 패널 · 인라인 칩 |
| border-base ⭐ | `2px solid` | **주 패널 · 카드 경계 (디폴트)** |
| border-emph | `3px solid` | DEEP 좌측 보더 · 포커스 상태 |

부수 규약 — `box-shadow`는 *픽셀 그림자만 허용* (`blur: 0`, `spread: 0`). 예: CTA hover의 `box-shadow: -3px 3px 0 0 #F5C200` 는 합법, `box-shadow: 0 4px 12px rgba(0,0,0,0.3)` 같이 blur 들어간 부드러운 그림자는 금지.

---

## §10. 모션 토큰 — steps() 강제 · 안건 C5 신규

CSS 트랜지션·애니메이션의 `timing-function`을 *`steps(N)` 으로 강제*하는 게 픽셀 끊김 효과의 핵심이다. `ease`·`cubic-bezier` 같은 부드러운 곡선은 *부드러운 곡선 자체가 픽셀 정체성 위반* — 사용 금지. 6개 토큰으로 모든 움직임을 커버.

| 토큰 | duration | steps() | 용도 |
|---|---|---|---|
| motion-instant | `0ms` | — | state 토글 · CTA 클릭 즉시 |
| motion-fast | `80ms` | `steps(4)` | 칩 hover · 토스트 페이드 |
| motion-base ⭐ | `120ms` | `steps(6)` | **CTA hover · 포커스 보더 (§11 기존 규약과 일치)** |
| motion-pop | `1200ms` | `steps(8)` | 🐛 캐러필러 +1 보상 팝업 (FR-GAME-002 — 페이드 0.3 + 유지 0.6 + 페이드아웃 0.3 합) |
| motion-walk | `600ms` | `steps(4)` | ∞ 코뉴 sprite 아이들 · 로딩 walk (4-frame, 150ms/frame) |
| motion-flash | `1000ms` | `steps(4)` × 2회 | 헤더 카운터 1초 점멸 (Flow-5 ⑤-2 차감 직후 토스트와 동기) |

❌ **금지**: `ease` · `cubic-bezier` · `linear`(스무딩되는 보간) — 부드러운 곡선은 모두 위반.

---

## §11. 인터랙션·접근성 (Interaction · A11y)

v0.1의 §7 인터랙션 규약을 보존하면서 안건 C6(`prefers-reduced-motion` fallback)를 흡수.

기본 인터랙션 규약은 그대로 — Textarea Focus는 보더가 `#E8631A`(ORANGE)로 전환되며 `motion-base` (120ms·`steps(6)`) 적용. CTA Hover는 `translate(3px, -3px)` + `box-shadow: -3px 3px 0 0 #F5C200` 픽셀 그림자, 역시 `motion-base`. 애니메이션은 모두 §10의 `steps()` 토큰을 사용하고, 반응형은 `<900px`에서 1-컬럼 세로 + CTA Sticky Bottom. 접근성은 태그 카테고리에서 *색상 + 아이콘 이중화*를 강제 — 📦 라이브러리 / 🔁 패턴 / 🏠 도메인 / 📐 자료구조 / ⚙ 알고리즘 (색맹 사용자가 색만으로 구분할 수 없을 때 아이콘이 보강).

### §11.1 `prefers-reduced-motion` Fallback · 안건 C6 신규

WCAG 2.3.3 + HSP·전정 민감 사용자 보호 (NFR-6 a11y). HSP 페르소나가 *디폴트 사용자*인 본 제품에서는 *필수 안전망*이지 선택지가 아니다. 전역 룰은 모든 애니메이션·트랜지션을 0.01ms로 사실상 정지:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

그러나 전역 룰은 *안전망*일 뿐이고, *의미 있는 모션*(예: 캐러필러 +1 발생)은 *최종 상태만 즉시 노출* 해야 한다 — 그렇지 않으면 *움직임이 사라진 게 아니라 피드백이 사라진 것*이 되어 UX가 무너진다. 토큰별 fallback 동작:

| 토큰 | reduced 시 동작 |
|---|---|
| motion-pop (보상 팝업) | 0.6초 정지 노출 후 사라짐 (스케일·이동 없음) |
| motion-walk (sprite) | 아이들 프레임 1장 고정 |
| motion-flash (점멸) | 1초 색 변경(노랑→주황) 정적 표시 |
| motion-base (CTA hover) | `translate` 제거, 색·보더만 변경 |
| motion-fast (페이드) | 즉시 표시/숨김 (`opacity: 0` → `1`) |
| Streak 풀스크린 축하 | 메시지 + 정적 sprite 1.5초, 폭죽 없음 |

---

## §12. 보강 화면 결정 — 안건 B + D · D-2 ✅ 닫힘

Stage 4 v0.1 시점에 *UC-2/UC-3·설정·도감 화면이 미작성*이었던 부채를 Stage 8 안건 B(9화면) + 안건 D(10화면)로 청산. 각 화면은 *어느 PRD FR을 시각화하는가* 와 *어느 03 UX Flow 노드에 대응하는가*가 명시돼 있어 Stage 9 진입 시 *어느 컴포넌트를 어디부터 짤지*가 추적된다.

### §12.1 UC-2 검색 (Flow-3) — 안건 B1·B2·B2b

검색은 *모달 진입(⌘K)* + *전용 페이지* 이원화. **B1 모달**은 `⌘K`로 어디서나 호출 가능하고 최근 검색 기록(`recent_searches` DB·디바이스 횡단)을 5축 OR 가중치 정렬로 보여줌. ESC로 닫고 `↑↓` 이동·`↵` 열기·`⇥` 정렬 토글 키 동작 기본. **B2 결과 페이지**는 무한 스크롤(20개씩) + 정렬 토글(관련도/최근순/⭐ 즐겨찾기) + 5축 필터(🏷 태그 · 📘 KC · 📄 코드 · 🌲 요약 · 📝 메모). **B2b 빈 결과** variant는 별도 카피로 *"X는 아직 본 적 없어 — 빈 결과는 새 분석으로 채워가는 게 가장 빨라"* 라며 행동 유도 — 0건 화면을 *막다른 골목*이 아니라 *시작점*으로 재프레이밍.

### §12.2 UC-3 도감 (Key Concepts) — 안건 B4

5축 카테고리 탭(전체/🔁 패턴/📦 라이브러리/📐 자료·함수/⚙ 알고리즘/🏠 도메인) + ✨ NEW 배지로 *새로 추가된 개념*만 별도 강조. 각 개념 카드에는 *본 횟수*(누적 회수) + *첫 만남* 일자/분석 명이 박혀 *처음 본 코드가 어디였는지*가 시간순으로 추적 가능. 우측에 선택된 개념의 정의 패널이 펼쳐지고, *처음 만난 분석* + *다시 만난 분석(×N)* 이 카드 형태로 나열 — 즉 도감은 *컬렉션 + 출처 역추적 인덱스* 이중 기능.

### §12.3 설정 (Settings) — 안건 B5

8 카테고리 좌측 사이드바(🎓 학습자 · 👤 프로필 · 🐛 게이미피케이션 · 🔔 알림 · 💳 결제 · 💾 데이터 · 📖 도움말 · ℹ 정보) + 우측 상세 패널. 게이미피케이션 카테고리에 *현재 누적 자산*(🔥 Streak·🐛 캐러필러·🛡 방패·📘 도감) 박스 + *FR-SETTINGS-003 동작 옵션* 5종(보상 사운드 디폴트 OFF·풀스크린 축하·캐러필러 20 → 자동 방패 변환·🐛 +1 픽셀 애니메이션 강조·풀스크린 길이 조정) + *호칭 진척* 4단계 시각화. HSP 배려로 *보상 사운드 디폴트 OFF*가 박혀 있는 게 핵심.

### §12.4 아카이브 (이력) — 안건 B3

23건 무한 스크롤(20개씩) + 카드/목록 뷰 토글 + 정렬(최근순/이름/⭐) + 필터(📌 핀 only / ⭐ 즐겨 / 📝 메모 / 🔁 패턴 / 📐 자료구조). 각 카드에 코드 thumbnail(3-line 미리보기) + 태그 칩 + 메타(작성 시점·줄 수·분석 회차) + … 메뉴(편집·삭제·내보내기).

### §12.5 분석 진행 + 차단·결정 모달 — 안건 B6·B7

**B6 분석 진행**(`ANALYZING` 상태)은 P95 25초 표시 + skeleton + 시머(`steps(8)`)·*"코뉴가 코드 읽는 중… 3계층으로 정리해줄게"* 카피·캐시 hit/miss 표시·`daily_used +1` 디스플레이. 실패 시 3회 재시도 → EC-2 fallback. **B7 차단·결정 모달 4종**:

- *EC-1 · 200줄 초과 → AST 분할* — 287줄·4520토큰 입력 시 AST 파서가 3개 의미 단위로 자동 분할, *블록 A/B/C* 중 선택해서 첫 블록만 분석 또는 직접 자르기 옵션.
- *Flow-5 모달 A · 카운터 0~3/5* — 깊은 해설 진입 직전, 카운터 노출만.
- *Flow-5 모달 B · 카운터 4/5 직전* — *"5번째야 — 분석 1회 차감될 거야"* 경고 + 차감 후 카운터 미리보기(0/5) + 오늘 남은 분석 미리보기(4 → 3회). ⑤-2 시각 표시: 차감 직후 토스트 + 헤더 카운터 1초 점멸 (motion-flash).
- *EC-3 · 한도 0 차단* — *"오늘 한도 다 썼어 — 내일 자정(KST)에 다시 만나자"* + *자정 푸시 X (수면 보호)* 명시.

### §12.6 반응형 1-col — 안건 B8

`<900px`에서 3 컬럼이 세로 1 컬럼으로 적층 (FOREST → TREE → LEAF 순서 유지). CTA Sticky Bottom. READY/ANALYZED 양 상태 검증.

### §12.7 Flow-1 온보딩 — 안건 D1·D2·D3·D4

랜딩(D1) → 회원가입/로그인 분기(D2) → 환영(D3) → 학습자 레벨 4지선다(D4) → 첫 분석. 03 UX Flow의 ①-1·①-2 마이크로 결정이 모두 시각화됐다.

- **D1 Landing** — 좌측 hero 헤드라인 *"AI가 만든 코드, 3계층으로 풀어볼래?"* + 30초 무료 시작 CTA + 무료 일일 10회·카드 등록 없음·AI 슬롭 없음 3 promise. 우측에 *6일 전 가입한 어느 코뉴* STATS 박스 + 호칭 진척 + 코뉴 mascot pixel art. 비로그인 진입점.
- **D2 회원가입/로그인** — 좌측 신규(🥚 처음 와 봤어), 우측 재방문(🪶 이미 코뉴야). 이메일 8자 + bcrypt cost 12 (NFR-7.2) + 닉네임 2~12자 · 이용약관/개인정보 처리방침 동의(NFR-7.11 기록) · Closed Beta 활성(FR-AUTH-008/009). 5회 실패 → 15분 잠금(NFR-7.7). 카카오·구글 소셜 로그인 버튼.
- **D3 환영** — *①-1 마이크로 결정* 시각화. *첫 접속*은 [다음] 클릭 대기 능동 진행 + *재방문*은 2초 자동 페이드. HSP 배려로 무음(`sound_enabled = FALSE` 디폴트).
- **D4 학습자 레벨 4지선다** — *①-2 마이크로 결정* + 각 레벨 미리보기 펼침(🔍). 4지선다 카피가 *심리적 부담을 낮추는 톤* — *01 python? 뱀이라는 풍문은 들어봄 (level=1) / 02 Hello world 정도는 띄워봄 (level=2) / 03 저장한 py 파일이 20개는 넘는달까~ (level=3) / 04 코뉴, 니가 알아서 좀 골라줘라! (level=2 + auto=TRUE)*. 미리보기는 *같은 코드, 다른 톤* 으로 레벨별 해설 차이를 보여줌 (FR-ANALYSIS-012·NFR-1과 1:1 매핑). 건너뛰기 = 디폴트 `level=1`. 자동 선택 시 5회 후 + 30일마다 자동 재추천(FR-ANALYSIS-013).

### §12.8 분석 상세 페이지 (/analysis/{uuid}) — 안건 D5

Flow-3·4 종착점. `/analysis/0c2f-9a1d` 같은 UUID URL로 영구 접근 가능 → 북마크·공유·메모 누적. FOREST 요약 + TREE 구조 카드 + LEAF 라인별 해설(deep_pinned 라인은 영구 저장·NFR-4) + 📝 MEMO(2000자·1초 디바운스 자동 저장) + 🏷 TAGS(5/15) + 📘 KEY CONCEPTS + 🔗 META(타임스탬프·토큰 in/out·비용·SHA). 📤 .md 내보내기 + 🗑 삭제 액션.

### §12.9 EC-2·EC-4·EC-5 — 안건 D6·D7·D8

- **EC-2 분석 실패 3회** (D6) — *"미안, 지금 좀 문제가 생겼어 / OpenAI 서버랑 통신이 잘 안 되네"* 자기비하 톤 ⑥-4 (ADHD 좌절 차단). `daily_used -1 롤백 완료 ✓` 명시 + Sentry + 이메일 이중 알림 + REQ-ID 노출 + exp backoff(1s·3s·9s).
- **EC-4 방패 발동 풀스크린** (D7) — *"방패가 막아줬어! / 어제 쉬어도 🔥 Streak 7일이 유지됐어"* + 1.5초(스킵 가능·무음·FR-GAME-005). DB 동작: `shield -1` · `streak_current 유지` · 어제분 `+1` 처리.
- **EC-5 14일 복구 모달** (D8) — `users.deleted_at + 14일 > NOW()` 시 자동 모달. *"14일 동안 너 기다리고 있었어 / 9일 남았어"* 카운트다운 + 복구 시 자동 처리(`deleted_at = NULL` · 🐛 캐러필러 +14 보너스 ⑥-8 · 분석 이력 그대로). 9일 안에 안 오면 영구 삭제 + 동일 이메일 재가입 가능.

### §12.10 시스템 컴포넌트 — Toast 8종 / Tooltip 4종 — 안건 D9·D10

**Toast 8종** (우상단 stack · 페이드 인 0.3 + 유지 1.4~2.4s + 아웃 0.3 · 동시 표시 max 3):

| Toast | 메시지 카피 | 트리거 |
|---|---|---|
| `cache_hit` | 💡 전에 본 코드라 빠르게 보여줄게 🦜 | SHA-256 캐시 hit (NFR-3) |
| `leaf_5_charged` | 🔔 분석 1회 차감됐어 🦜 | 5번째 깊은 해설 (FR-ANALYSIS-007) |
| `pin_saved` | 📌 저장 완료! | `tier=deep_pinned` 핀 (FR-ARCHIVE-004) |
| `kc_new` | ✨ 새 개념 *X* 도감에 추가됨! | 도감 슬롯 +1 (FR-GAME-007) |
| `shield_made` | 🛡 방패가 생겼어! | 캐러필러 -20 자동 변환 (FR-GAME-005) |
| `streak_milestone` | 🐛 +3 캐러필러 보너스! | 7일 마일스톤 1~5 랜덤 분포 (FR-GAME-006) |
| `copy_done` | 📋 복사 완료 🦜 | Forest 요약 클립보드 (FR-OUTPUT-011) |
| `retry_soft` | ⚠ 잠깐, 다시 시도할게 | EC-2 soft retry (자동 재시도 1/3) |

Toast 규약 — 사운드 디폴트 OFF(HSP), 다크 위 dim 5% scrim 없음(overlay 아님), 색맹 배려 아이콘+텍스트 이중화, 좌측 accent border + 좌하 box-shadow 2-step, 에러 색은 `#E85555` (orange와 분리해 사고 방지).

**Tooltip 4종** (지연 600ms hover · ESC로 닫힘 · once 플래그 활용):

1. *짧은 해설 첫 호버* — `users.has_seen_leaf_intro = FALSE` 일 때만 1회 노출. *"클릭하면 더 깊은 설명을 볼 수 있어! / 5번 보면 분석 1회 차감되니까 신중하게~"*
2. *📌 핀 호버 (학습용)* — FR-ARCHIVE-004 · 핀 가능한 라인(추가 확장분)만. *"📌 누르면 영구 저장돼! 나중에 다시 볼 수 있어 🦜"*
3. *헤더 호칭 호버* — 단순 정보 툴팁(once X · 항상 노출). *"첫 비행 코뉴 / L3 · 11~30회 · 너는 23회 / 다음 호칭 왕관 코뉴 🎩까지 8회 + 7일"*
4. *Deep 라인 재호버 차단* (이미 본 라인) — *"이미 깊게 본 라인이야 🦜 / 다른 라인 봐볼까?"* ⑤-4 시각 표시: 📖 + 배경색·색맹 배려 이중화.

---

## §13. 페이지 컴포넌트 props 정밀화 — TDDoc §35.2 O-10 ✅ 닫힘

TDDoc(`07-technical-design.md`) §35.2 운영 안건 **O-10**(*4개 페이지 props 정밀화 — Stage 9 진입 시 각 페이지 구현 직전에 결정*)은 *지연 결정으로 인지부하 절감*이 원래 정신이었다. Stage 8 안건 B에서 *4개 페이지 시안이 모두 그려졌으므로* 지연할 이유가 사라졌고, **닫힘** 처리. 각 페이지의 *외부 진입 props*만 고정하고, *내부 상태(`useState`·`useReducer`)는 컴포넌트 자유* — 이 분리가 TDDoc §35 F-3(상태는 *가장 가까운 공통 조상* 원칙)과 일치.

### §13.1 `<ArchivePage>` (안건 B3 → /archive)

```ts
type ArchivePageProps = {
  // 외부에서 결정되는 것
  initialSort?: 'recent' | 'name' | 'star';  // default 'recent'
  initialView?: 'card' | 'list';              // default 'card' (모바일은 자동 'list')
  initialFilter?: ArchiveFilter;              // pin/star/memo/pattern/structure null-able
  // URL 파라미터로부터 hydrate (Flow-3 진입 시)
  searchQuery?: string;                       // ?q=fib 같은 쿼리 hydrate
};

type ArchiveFilter = {
  pinOnly?: boolean;
  starOnly?: boolean;
  hasMemo?: boolean;
  tagCategories?: Array<'pattern' | 'library' | 'domain' | 'structure' | 'algorithm'>;
};
```

내부 상태(컴포넌트 자유): 무한 스크롤 커서·로딩 phase·선택된 카드 ID·확장 메뉴 열림 여부. 데이터 패칭은 `useApi('/api/v1/archive', { cursor, limit: 20, sort, filter })`로 단일 진입(TDDoc §35 F-1).

### §13.2 `<SearchPage>` (안건 B2·B2b → /search)

```ts
type SearchPageProps = {
  query?: string;                              // ?q= 또는 ⌘K 모달에서 hydrate
  initialSort?: 'relevance' | 'recent' | 'star';  // default 'relevance'
  initialAxes?: SearchAxes;                    // 5축 필터 hydrate
};

type SearchAxes = {
  tags?: boolean;        // 🏷 태그 검색 (default true)
  keyConcepts?: boolean; // 📘 KC 검색 (default true)
  code?: boolean;        // 📄 코드 텍스트 검색 (default true)
  forest?: boolean;      // 🌲 요약 검색 (default true)
  memo?: boolean;        // 📝 메모 검색 (default true)
};
```

내부 상태: 무한 스크롤 커서·일치 건수·정렬 토글 상태. 빈 결과 시 `<EmptyResult variant="search" query={query} />` 분기 (안건 B2b 컴포넌트화).

### §13.3 `<EncyclopediaPage>` (안건 B4 → /encyclopedia)

```ts
type EncyclopediaPageProps = {
  activeCategory?: EncyclopediaCategory;  // default 'all'
  selectedConceptId?: string;             // URL ?concept=recursion 등으로 hydrate
};

type EncyclopediaCategory =
  | 'all'
  | 'pattern'      // 🔁
  | 'library'      // 📦
  | 'structure'    // 📐
  | 'algorithm'    // ⚙
  | 'domain';      // 🏠
```

내부 상태: 정의 패널 펼침 여부·`<RelatedAnalyses>` 페이징. `selectedConceptId`가 있으면 우측 정의 패널 자동 펼침 + *처음 만난 분석* + *다시 만난 분석(×N)* 로딩.

### §13.4 `<SettingsPage>` (안건 B5 → /settings)

```ts
type SettingsPageProps = {
  initialSection?: SettingsSection;  // default 'learner'
};

type SettingsSection =
  | 'learner'        // 🎓
  | 'profile'        // 👤
  | 'gamification'   // 🐛
  | 'notification'   // 🔔
  | 'billing'        // 💳
  | 'data'           // 💾
  | 'help'           // 📖
  | 'info';          // ℹ
```

내부 상태: 각 섹션의 form dirty 여부·저장 phase·확인 모달 열림 여부. 저장은 섹션별 PATCH API 호출 (FR-SETTINGS 전체 — TDDoc §31 모듈 경계 준수).

### §13.5 보너스 — `<AnalysisDetailPage>` (안건 D5 → /analysis/{uuid})

O-10 범위 밖이지만 안건 D5에서 함께 시각화됐으므로 props 표기만 추가 (실제 결정은 Stage 9 첫날 분석 페이지 구현 직전):

```ts
type AnalysisDetailPageProps = {
  analysisId: string;  // UUID — URL 필수 파라미터
};
```

나머지(메모 자동 저장 디바운스·tier 표시·메타 표시 토글)는 모두 내부 상태. URL이 SSoT이고 외부 진입은 `analysisId` 하나.

---

## §14. 닫힌 결정 / 후속 안건 (Closed · Forward)

v0.1의 §8(미결 결정) 표를 *닫힌 결정 일람* + *후속 안건* 두 갈래로 분기.

### §14.1 Stage 8에서 닫힌 결정

| # | 결정 내용 | 닫힘 신호 (Stage 8 산출물) | 본 문서 위치 |
|---|---|---|---|
| **D-1** | 데스크톱 레이아웃 = **A3 Zoom Pillars** (1× → 4× → 12× 좌→우) | 안건 A 페이지 3 *"✅ 확정안"* 라벨 | §2 |
| **D-2** | UC-2/UC-3·설정·도감·온보딩·EC-2/4/5·시스템 화면 보강 = 19화면 (안건 B 9개 + 안건 D 10개) | 안건 B + D 전체 | §12 |
| **B-3** | 디자인 토큰 2차 확정 = 6항목 (중립색 9-step · 액센트+상태 · 간격 4px · 픽셀 보더 · 모션 steps() · reduced-motion fallback) | 안건 C 페이지 25~30 | §4·§5·§8·§9·§10·§11 |
| **O-10** | 4개 페이지 props 정밀화 = ArchivePage·SearchPage·EncyclopediaPage·SettingsPage | 안건 B 페이지 7·9·10·11 + 본 §13 | §13 |
| **O-9** | `<DashboardLayout>` 컨테이너 분기 구현 = *Zoom Pillars 단일 구현*(분기 사라짐) | D-1 자동 따라옴 | §2.2 |

### §14.2 잔여 미결·후속 안건

| # | 결정 | 처리 시점 | 비고 |
|---|---|---|---|
| ~~D-3~~ | 도감 슬롯 상한 | PRD §5.6 FR-GAME에서 *∞(상한 없음)* 으로 확정 | v0.2에서 닫힘 표시 |
| O-7 | 도메인 훅 분리 시점 | Closed Beta 진입 후 1주차 (코드 리뷰 시점) | TDDoc §35.4 — 본 문서 범위 밖 |
| O-8 | Stylelint AI 슬롭 6항목 자동 감지 | Closed Beta 진입 직전 (5/28) | TDDoc §35.5 — 본 문서 범위 밖 |
| (잔) | 칭호 명칭 ↔ FR-GAME-003 본문 일치 확인 | 다음 PRD 갱신 (minor) | TRD 부록 B-5 |

도감 슬롯 상한(D-3)은 PRD v0.10에서 *상한 없음(∞)* 으로 결정됐으므로 v0.2에서 명시적 닫힘 처리. 안건 B4 도감 페이지의 *"9 / 누적 ∞"* 표기가 그 결정의 시각 구현.

---

## §15. 다시 숲 — v0.1 → v0.2 변경 요약

Stage 4(v0.1)는 *UC-1 해피패스만 알고 있던 문서*였고, Stage 8(v0.2)에서 *나머지 19화면 + 디자인 토큰 6항목 + 페이지 props 4종*이 모두 박혀 *Stage 9 진입 게이트의 게이트 B 3건이 동시에 닫혔다*. 이 결과로 *Stage 9 첫 줄 코드 짜기 전에 합의돼야 할 디자인 차원의 부채는 0건*이 됐다 — TDDoc §38.3 진입 게이트 B-1·B-2·B-3 모두 ✅.

| 축 | v0.1 (Stage 4) | v0.2 (Stage 8) | 비고 |
|---|---|---|---|
| 산출 화면 수 | 7 (UC-1 해피패스만) | 7 + 30 = 37 | 안건 A 5 + B 9 + C 6 + D 10 추가 |
| 데스크톱 레이아웃 | 미결 (A vs B) | **A3 Zoom Pillars 확정** | §2 + §2.1 미채택 사유 보존 |
| 색상 토큰 | 액센트 4색만 | 액센트 4색 + soft 변형 + 중립색 9-step | §4 + §5 (신규) |
| 간격·보더·모션 | (없음) | space 9-step + border 3단 + motion 6 토큰 + reduced-motion | §8·§9·§10·§11.1 (신규) |
| UC-2/UC-3 화면 | 미작성 | 검색 모달·결과·아카이브·도감 완비 | §12.1·§12.2·§12.4 |
| 온보딩·EC 화면 | 미작성 | Landing·회원가입·환영·레벨 선택·EC-2/4/5 완비 | §12.7·§12.9 |
| 시스템 컴포넌트 | (없음) | Toast 8종 + Tooltip 4종 | §12.10 (신규) |
| 페이지 props | (없음) | 4 + 1 페이지 props 정밀화 | §13 (신규) — O-10 닫힘 |
| 닫힌 결정 수 | 0 | **5** (D-1·D-2·B-3·O-10·O-9 동반) | §14.1 |

다음 단계는 **Stage 9 TDDev** 진입 — TDDoc §38.4의 *시점별 작업·주 참조 §* 표(D-7 환경 세팅부터 D-0 출시까지)를 따라 코드를 짠다. 디자인 차원에서 *코드가 의지할 합의*는 v0.2로 모두 박혔으므로, Stage 9 첫 줄 코드부터 *디자인 결정 부재로 인한 블록*은 없을 것이다.

---

*Stage 4·8 Design Decisions — v0.2 (2026-05-26 · Stage 8 PRINT 30화면 흡수 + D-1·D-2·B-3·O-10·O-9 동반 닫힘). 참조 PRD v0.10 · Discovery v4 · UX Flow v0.2 · TDDoc v0.1 §35·§38.3·§38.4.*
