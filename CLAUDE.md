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
- LLM 호출을 트랜잭션 안으로 옮기기 (§33 ⑦)
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