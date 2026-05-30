# Code Decoder — Project Guide for Claude Code

## SSoT 파일 위치
- PRD: `docs/02-PRD.md` (v0.10)
- TDDoc: `docs/07-technical-design.md` (v0.1)
- UX Flow: `docs/03-ux-flow.md` (v0.2)
- Design: `docs/04-design-decisions.md` (v0.2)
- TRD: `docs/05-trd.md` (v0.2)
- Security: `docs/06-security.md` (v0.3)
- Discovery: `docs/01-discovery-summary-v4.md` (v4)

## 표기 규약 (HC-8)
- Stage 7 = TDDoc, Stage 9 = TDDev. 약어 "TDD" 단독 사용 금지 — *TDDev* 또는 *TDDoc*으로 명시.
- 새 FR 작업 시 PRD의 해당 FR 본문 먼저 읽고 TDDoc 관련 §도 확인.

## 워크플로우 (모든 FR 작업 동일)
1. PRD의 FR-XXXX-NNN 본문 + Acceptance Criteria 읽기
2. **실패하는 테스트만** 먼저 작성 (구현 금지)
3. 테스트 통과시키는 최소 구현
4. `pytest` / `npm test` 전체 그린 확인
5. 커밋 메시지에 FR 번호 포함 (예: `feat(auth): FR-AUTH-001 회원가입 핸들러`)

## 절대 금지 (TDDoc §38.4 8개 함정)
- routers에서 `HTTPException` 직접 던지기 → DomainError 사용 (§32·§36.2)
- services에서 `Request`/`Response` 받기 → HTTP 무지 원칙 (§31)
- §33.7 프롬프트 BLOCK A/B 조립 원칙 무시하기 (§33.7) ← §33.4 (a): LLM 호출은 트랜잭션 안이 정상
- 프론트 컴포넌트에서 `fetch` 직접 호출 → `useApi` 단일 진입 (§35 F-1)
- Alembic `downgrade` 작성 → forward-only (§37.4)
- `.env`에 시크릿 커밋 → `.env.local`만, `.gitignore` 확인
- AI 슬롭: `border-radius` 사용 / `ease`·`cubic-bezier` / 4px 그리드 외 값

## 환경
- OS: Windows 10/11 · 셸: CMD (PowerShell 가능)
- Backend: Python 3.12, venv는 `backend/.venv/`, `py -3.12 -m venv` 로 생성
- Frontend: Node 24, Vite + React + TypeScript, `frontend/` 디렉토리
- DB: Railway PostgreSQL (개발 + 배포 동일)
- 배포: Vercel(프론트) + Railway(백엔드)

## 테스트·린트 명령
- Backend: `pytest`, `ruff check`, `mypy app/`
- Frontend: `npm test`, `npm run lint`, `tsc --noEmit`

## 페르소나
- 제품 타겟 페르소나: 코딩 0-1개월 차 비전공자 (PRD §3 페르소나 정의)
- 제품 오너(코뉴): AI 교육 4-5개월 차 — 타겟에 가까운 dogfooder 위치
- 픽셀 미학(NFR-8): radius 0 강제, `steps()` 강제, 4px 그리드
- D-3 체크포인트(5/29) = K-Digital 발표일, P0 27개 미달 시 자동 강등 룰 발동

## [TODO] Alembic 초기화 — Railway 배포 전 필수

현재: 미초기화 상태, 테스트는 SQLite create_all로 동작 중
작업:
  alembic init alembic
  alembic revision --autogenerate -m "initial schema"
  alembic upgrade head

시점: LLM 연동 완료 후 Railway 첫 배포 직전

## [TODO] ★발표 전 필수★ TS6 ↔ openapi-typescript peer 충돌 — Vercel 배포 가드

현황: typescript@~6.0.2 vs openapi-typescript@7.13.0 (peer typescript@^5.x)
노출 시점: 2026-05-30 vitest 셋업 install 중 ERESOLVE
사전 부채: b7d2f06부터 묵인되던 충돌 — 이번이 첫 노출, 임시 --legacy-peer-deps 상환

★발표 전 필수 (배포 데모 블로커 가능)★:
  Vercel 빌드가 npm install이면 동일 ERESOLVE로 배포 실패 가능.
  세션 7 배포 전 반드시 둘 중 하나 처리:
  (a) Vercel install 명령에 --legacy-peer-deps 부착, 또는
  (b) repo 루트 .npmrc에 legacy-peer-deps=true (.npmrc는 로컬+CI 동시 적용 — 권장)

근본 해결 (발표 후): openapi-typescript가 TS6 지원 메이저 릴리스 시 bump,
  또는 TS 5 라인으로 회귀. 빌드/타입 생성 자체는 현재 정상(실측 그린).

dev log: 2026-05-30 vitest 셋업 중 사전 부채 발견, --legacy-peer-deps로 임시 상환.
