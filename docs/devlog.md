# 개발 일지 (devlog)

세션별 부채 발견→상환·실측 검증·배운점 기록. 시간 역순(최신이 위).
현재 유효 지침·라우팅은 `CLAUDE.md` 참조.

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
