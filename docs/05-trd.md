# Code Decoder MVP — Stage 5 Technical Requirements Document (TRD)

> **문서명**: `05-trd.md`
> **버전**: v0.2 (§15~§20 통합 + Stage 6 보안 패치 반영)
> **작성**: 2026-05-17 ~ 2026-05-18
> **참조 SSoT**: `02-PRD.md`(v0.10) · `01-discovery-summary-v4.md`(v4) · `03-ux-flow.md`(v0.2) · `04-design-decisions.md`(v0.1) · `06-security.md`(v0.3)
> **소유자**: 코뉴 (제품 오너)
> **목적**: PRD가 정의한 "무엇을"을 "어떻게 구현하느냐"로 정밀화. 본 문서는 Stage 9 구현의 직접 청사진이다.

## 패치 로그

| 일자 | 버전 | 변경 내용 |
|---|---|---|
| 2026-05-18 | v0.1 | §15~§20 6개 섹션 통합 완료본. 배포 전략 = **Vercel + Railway 확정**(Pre-MVP·Closed Beta). §20에 백업(일 1회 `pg_dump`)·Open Beta 인프라 재평가 체크포인트 보강. TRD ↔ PRD v0.8 ↔ Discovery v4 3자 정합성 점검 완료. |
| 2026-05-19 | v0.2 | **Stage 6 보안/개인정보 설계(`06-security.md` §21~§29) 반영 — 부록 A 패치 ②·④.** (A-②) §20.6 백업 보강 2건 — (a) `pg_dump` 산출물은 DB 전체(코드+PII)의 평문 사본이므로 외부 스토리지 업로드 *전* 자체 키 암호화 + 버킷 접근 통제 요구 신설, (b) 백업 보존 주기 30일 명시(30일 경과 덤프 자동 폐기 → HC-10 hard delete 데이터의 백업 소멸 보장). §20.7 다시 숲 표 백업 행 동기화. (A-④) §16.2 FK 캐스케이드 맵에서 `consent_log`를 단순 CASCADE 대상에서 **제외** — 계정 hard delete 시 행을 삭제하지 않고 **변환(TRANSFORM)** 처리(IP·User-Agent 파기 + `user_id` 비가역 가명화, 동의 사실 코어는 보존). 사유: 단순 CASCADE는 NFR-7.11(동의 기록 영구 저장)과 충돌, 통째 보존은 HC-10(모든 PII 파기)과 충돌 — 가명처리로 양립. §16.2 설명 단락 보강 + §16.5 다시 숲 표 FK 행 동기화. **§·테이블·FR 식별자 불변, 스키마 컬럼 정의 불변(삭제 *정책*만 변경).** |

## 목차

| § | 섹션 | 핵심 |
|---|---|---|
| §15 | 기술 스택 | FastAPI · React+Vite · PostgreSQL · SQLModel |
| §16 | DB 스키마 | `leaf_counter` 신설 · `daily_limit` 티어 · 도감 개방형 |
| §17 | 백엔드 API 설계 | REST · 분석 단일 트랜잭션 · 쿠키 세션 |
| §18 | 프론트엔드 상세 | 디자인 토큰 CSS 변수 · 컴포넌트 트리 · Context |
| §19 | LLM 연동·프롬프트 | 2블록 캐싱 · Structured Outputs · 레벨 1·2·3 |
| §20 | 배포·인프라·운영 | Vercel+Railway · 시크릿 · 배치 · 백업 |

---

# §15. 기술 스택

## §15.1 스택 조감

```
        [사용자 브라우저]
              │ 코드 붙여넣기 → "분석하기"
              ▼
   프론트엔드 (Vercel)   React 19 + Vite + TypeScript (정적 SPA)
              │ HTTPS / JSON REST
              ▼
   백엔드 (Railway)      FastAPI + uvicorn (Python 3.12)
         │          │
         ▼          ▼
   PostgreSQL    OpenAI API
   (Railway)     GPT-5 mini · Python SDK
   SQLModel
```

원칙은 **한 언어로 등뼈 통일** — 백엔드·LLM 연동·DB 모델·입력 전처리가 전부 Python 한 언어 안에 있어, 비전공자가 한 채팅에서 디버깅할 때 언어를 갈아끼우지 않는다. 프론트엔드만 브라우저의 모국어 TypeScript를 쓴다.

## §15.2 백엔드 — FastAPI

**확정**: FastAPI (Python 3.12+) + ASGI 서버 uvicorn.

근거: ① 코뉴가 KDT에서 배우는 언어가 Python — 마감 직전 언어 전환 리스크 제거. ② Pydantic이 들어오는 요청이 약속한 모양인지 자동 검증 — `if`문 없이 문지기 확보. ③ `/docs`에 인터랙티브 API 문서가 자동 생성 — "내 API가 뭐였더라"의 목차 역할. uvicorn은 FastAPI(메뉴판)에 실제 주문을 나르는 웨이터다. Pre-MVP는 uvicorn 단독, Closed Beta 확장 시 `gunicorn + uvicorn worker`.

## §15.3 프론트엔드 — React + Vite

**확정**: React 19 + Vite + TypeScript.

근거: 분석 결과 화면은 "입력창 → 로딩 → 3계층 결과"로 같은 자리가 진화하는 구조라 상태 기반 렌더링(React)이 최적. Vite는 코드 한 줄 수정 시 화면을 즉시 갱신해 ADHD 페르소나의 짧은 피드백 루프에 유리. TypeScript는 백엔드 응답 JSON의 모양을 타입으로 선언해 `deep_leaves` 같은 필드 불일치를 컴파일 단계에서 차단.

**스타일링**: Tailwind는 디폴트 미감이 "둥근 카드+부드러운 그림자"(AI 슬롭)로 기운다. 순수 CSS + CSS 커스텀 프로퍼티로 04 디자인 토큰을 1:1 통제한다(상세 §18.2).

## §15.4 데이터베이스 & ORM

**확정**: PostgreSQL 15+ (Railway 매니지드) + **SQLModel + Alembic**.

SQLModel은 FastAPI 제작자가 만든 같은 계열 부품 — Pydantic 검증 모델과 DB 테이블 모델을 한 클래스로 통합해 비전공자 인지부하를 최소화한다. DB 스키마 변경 이력은 Alembic 마이그레이션으로 관리. ORM이 Python 객체 ↔ SQL 사이를 통역하므로 raw SQL 없이 NFR-7.4(SQL Injection 방지)도 자동 충족.

## §15.5 LLM 연동

**확정**: OpenAI Python SDK · 모델 GPT-5 mini 단일(HC-5). 프롬프트 캐싱(NFR-1)·`max_tokens` 8,000 하드캡(NFR-2)·`finish_reason` 로깅을 SDK 호출에 적용(상세 §19).

## §15.6 인프라

Railway(백엔드+DB+Cron) / Vercel(프론트엔드) / Resend(이메일, Closed Beta). 호스팅 업체는 Python·정적 SPA를 표준 지원. 배포 전략 최종 확정은 §20 참조.

## §15.7 빌드타임 의존성 (Python 환산)

`passlib[bcrypt]`(NFR-7.2 해싱) · `SQLModel`+`Alembic` · OpenAI Python SDK · DOMPurify(프론트, NFR-7.5 XSS) · JetBrains/IBM Plex Mono·Pretendard(self-host).

## §15.8 다시 숲 — §15 정리

| 레이어 | 확정 |
|---|---|
| 백엔드 | FastAPI (Python 3.12+) + uvicorn |
| 프론트엔드 | React 19 + Vite + TypeScript |
| 스타일링 | 순수 CSS + CSS 변수 |
| DB / ORM | PostgreSQL 15+ / SQLModel + Alembic |
| LLM | OpenAI Python SDK · GPT-5 mini |
| 호스팅 | Railway(BE/DB) · Vercel(FE) · Resend |

> ※ PRD §9의 Node 생태계 placeholder 표기는 PRD v0.5 패치로 정정 완료(Railway→Python/FastAPI, Vercel→React+Vite, ORM→SQLModel, OpenAI Python SDK).

---

# §16. DB 스키마

## §16.0 선결 3대 안건 (확정)

**안건 ① `leaf_counter`** — FR-ANALYSIS-007의 추가 Leaf 5:1 차감 카운터. **User 테이블에 사용자 전역 롤링 카운터**(0~4)로 둔다. 분석별이 아니라 전역이라야 "분석 여러 개 열어 각 4회씩 무료 확장" abuse 우회가 막힌다.

**안건 ② `daily_limit`** — User 컬럼 유지, DB DEFAULT **10**(Closed Beta 동기 테스터 기준), 코뉴 본인 행은 시드 시 50 명시 주입. 플랜 티어:

| 단계 | 대상 | `daily_limit` |
|---|---|---|
| Pre-MVP | 코뉴 본인 (시드 행) | 50 |
| Closed Beta | 동기 테스터 | 10 |
| Open Beta | 공개 무료 | 3 (Discovery §12) |
| Open Beta | 공개 유료 | 10 (Discovery §12) |

> Open Beta 무료 3·유료 10은 Discovery §12 확정 비즈니스 모델이며, Billing 후속 PRD에서 plan 연동으로 명시 할당. DB DEFAULT 10은 Pre-MVP·Closed Beta용 폴백값.

**안건 ③ 도감 슬롯** — **상한 없음·개방형 누적**. 시드 테이블 불필요. LLM 자유 텍스트를 고정 정원에 정규화하는 문제(마감 리스크)를 회피하고, 도파민 훅은 "N개 수집" + 1·10·30 마일스톤으로 충족. → 신규 테이블 0개, PRD §7.0 ERD 골격 불변.

## §16.1 횡단 정밀화 4종

**(1) ENUM 전략** — 네이티브 PG ENUM 대신 **앱 레벨 Python `str, Enum` + VARCHAR 저장**(+ 필요 시 CHECK). 네이티브 ENUM은 값 추가 시 `ALTER TYPE`이 까다롭고, `plan`·`category`는 Open Beta에서 늘어날 게 확실하다.

**(2) FK ON DELETE** — §16.2 캐스케이드 맵에서 확정.

**(3) UUID 생성** — `gen_random_uuid()` (PostgreSQL 13+ 코어 내장). `uuid-ossp` 확장 불필요.

**(4) 시간·날짜** — 전부 `TIMESTAMPTZ`로 UTC 저장, "오늘" 판정은 앱에서 KST(UTC+9) 환산. `streak_last_date`처럼 날짜 비교가 본질인 컬럼만 `DATE`(기록 시점 KST 환산값).

**Pre-MVP 실사용 vs 스키마만**:

| 분류 | 테이블 |
|---|---|
| 실사용 (8) | User, Analysis, LineExplanation, KeyConcept, Reward, analysis_cache, daily_limit_log, cost_daily |
| 스키마만 (3) | Subscription, consent_log, notification_queue |
| 테이블 없음 (1) | Tag — Analysis.tags JSONB로 대체(Pre-MVP) |

## §16.2 핵심 테이블 정밀화

안건 ①②를 반영한 User 변경분 (전체 필드는 PRD §7.1 v0.8):

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    # ... nickname, learner_level(1·2·3), theme 등 PRD §7.1 ...
    daily_limit: int  = Field(default=10)   # 자유 티어 기준값
    daily_used:  int  = Field(default=0)    # 자정 KST 리셋
    leaf_counter: int = Field(default=0)    # 추가 Leaf 0~4 롤링 (5번째에만 0 리셋)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = Field(default=None)
```

`leaf_counter`: `SMALLINT NOT NULL DEFAULT 0`, `CHECK 0~4`. 두 카운터의 리셋 주기가 다르다 — `daily_used`는 자정 KST, `leaf_counter`는 5번째 확장 발생 시에만 0.

**FK 삭제 정책 캐스케이드 맵** (HC-10 14일 hard delete 실현):

```
User ──CASCADE────▶ Analysis, Reward, KeyConcept, Subscription,
        │            notification_queue, daily_limit_log
        ├──TRANSFORM─▶ consent_log — 계정 hard delete 시 행을 삭제하지 않고 변환:
        │              IP·User-Agent 파기 + user_id 비가역 가명화, 동의 사실(종류·버전·일시) 보존
        ▼
   Analysis ──CASCADE──▶ LineExplanation, analysis_cache
        └──SET NULL──▶ KeyConcept.first_seen_analysis_id
```

`first_seen_analysis_id`만 SET NULL — 분석 하나(FR-ARCHIVE-007)를 지워도 도감 개념(누적 학습 자산)은 보존해야 하므로 포인터만 끊는다.

`consent_log`는 단순 CASCADE에서 **제외 — 변환(TRANSFORM) 처리**한다. 계정 hard delete 시 행을 통째로 삭제하면 동의 증빙이 사라지고(NFR-7.11 "동의 기록 영구 저장"과 충돌), 통째로 보존하면 탈퇴자의 IP·User-Agent를 영구 보관하게 되어(HC-10 "모든 PII 파기"와 충돌) — 둘 다 글자 그대로는 성립하지 않는다. 따라서 PII(IP·User-Agent)는 파기하고 `user_id`는 비가역 가명값으로 치환하되, 동의 사실의 코어(동의 종류·약관 버전·동의 일시)는 가명 형태로 보존한다. 식별 불가능해진 동의 사실은 더 이상 개인정보가 아니므로 HC-10과 충돌하지 않으면서 NFR-7.11의 증빙 보존 의도를 살린다. (근거: `06-security.md` §26.6·§28.4 — 부록 A 패치 ④.)

## §16.3 부가 테이블 정밀화

- **`analysis_cache`** (NFR-3): `UNIQUE (user_id, code_sha256)`로 사용자별 분리, `expires_at = created_at + 7일`. 조회 시 `WHERE expires_at > now()` + 자정 배치로 만료 행 삭제. `hit_count`로 적중률 집계.
- **`daily_limit_log`**: `reason` ENUM(VARCHAR) — `'analysis'`/`'leaf_5th'`/`'rollback'`/`'midnight_reset'`. Pre-MVP부터 실사용(롤백 디버깅).
- **`cost_daily`** (NFR-5): `date` PK, 전일 집계 1행. 스키마 처음부터, 알림 발효는 Closed Beta.
- **`consent_log`**(NFR-7.11)·**`notification_queue`**(FR-SETTINGS-008 P1): 스키마만, Pre-MVP 미사용.

## §16.4 Alembic 마이그레이션 순서 + 인덱스

생성 순서: ① User → ② Analysis → LineExplanation → ③ Reward/KeyConcept/Subscription → ④ 부가 5종 → ⑤ 시드(코뉴 본인 User `daily_limit=50` + 대응 Reward).

| 인덱스 | 테이블·컬럼 | 떠받치는 FR |
|---|---|---|
| `idx_user_email` (UNIQUE) | User(email) | FR-AUTH-001 |
| `idx_analysis_user_created` | Analysis(user_id, created_at DESC) | FR-ARCHIVE-005 |
| `idx_analysis_sha256` | Analysis(user_id, code_sha256, created_at DESC) | NFR-3 |
| `idx_analysis_tags_gin` (GIN) | Analysis(tags) | FR-SEARCH-002 |
| `idx_analysis_search_text` (GIN) | Analysis(to_tsvector) | FR-SEARCH-002 |
| `idx_line_analysis_lineno` | LineExplanation(analysis_id, line_no_original) | FR-OUTPUT-003 |
| `idx_keyconcept_user_name` (UNIQUE) | KeyConcept(user_id, name) | FR-GAME-007 |
| `idx_cache_user_sha` (UNIQUE) | analysis_cache(user_id, code_sha256) | NFR-3 |

## §16.5 다시 숲 — §16 정리

| 항목 | 결정 |
|---|---|
| `leaf_counter` | User 테이블, 전역 롤링 0~4 |
| `daily_limit` | User 컬럼, DEFAULT 10, 본인 시드 50 |
| 도감 상한 | 없음·개방형, 신규 테이블 0개 |
| ENUM | 앱 레벨 Enum + VARCHAR |
| FK | User→자식 CASCADE / consent_log는 TRANSFORM(가명화) / first_seen만 SET NULL |
| UUID | `gen_random_uuid()` 코어 내장 |
| 시간 | UTC TIMESTAMPTZ 저장, KST는 앱 환산 |

> ※ §16 결정은 PRD v0.6 패치(Q-1~Q-3)로 §7.1·FR-ARCHIVE-006에 반영 완료.

---

# §17. 백엔드 API 설계

## §17.1 REST 설계 5대 원칙 + 요청 생애주기

(1) 모든 경로 `/api/v1/` 프리픽스 — 향후 `/v2/` 병행으로 구버전 보호. (2) 자원은 명사, 행동은 HTTP 동사(`GET/POST/PATCH/DELETE`). (3) 인증은 HTTP-only 쿠키 세션. (4) 응답은 일관 봉투 — 성공은 자원 JSON, 실패는 `{error:{code, message}}`(`message`는 코뉴 말투). (5) 모든 요청 본문은 Pydantic이 자동 검증.

```
[요청] → ① HTTPS → ② Rate Limit → ③ 쿠키 세션 검증
       → ④ Pydantic 입력 검증 → ⑤ 핸들러 → ⑥ DB 트랜잭션
       → ⑦ 응답 봉투 직렬화 → [응답]
```

①②③④는 미들웨어·의존성 주입으로 한 번 짜서 공유한다.

## §17.2 엔드포인트 카탈로그 (Pre-MVP P0)

| 그룹 | 메서드·경로 | 연결 FR | 인증 |
|---|---|---|---|
| 인증 | `POST /api/v1/auth/signup` | FR-AUTH-001 | — |
| 인증 | `POST /api/v1/auth/login` | FR-AUTH-001 (쿠키 발급) | — |
| 인증 | `POST /api/v1/auth/logout` | FR-AUTH-002 | ✓ |
| 부트스트랩 | `GET /api/v1/me` | FR-AUTH-004·ANALYSIS-008·GAME-001~005 | ✓ |
| 설정 | `PATCH /api/v1/users/me` | FR-AUTH-010·SETTINGS-002~008 | ✓ |
| **분석** | `POST /api/v1/analyses` | FR-ANALYSIS-005·006·011 | ✓ |
| **분석** | `POST /api/v1/analyses/{id}/leaves/expand` | FR-ANALYSIS-007 | ✓ |
| 아카이브 | `GET /api/v1/analyses?cursor=&limit=20` | FR-ARCHIVE-005 | ✓ |
| 아카이브 | `GET /api/v1/analyses/{id}` | FR-ARCHIVE-006 | ✓ |
| 아카이브 | `PATCH /api/v1/analyses/{id}` | FR-ARCHIVE-003·008·009 | ✓ |
| 아카이브 | `DELETE /api/v1/analyses/{id}` | FR-ARCHIVE-007 | ✓ |
| 아카이브 | `PATCH /api/v1/analyses/{id}/leaves/{line_no}/pin` | FR-ARCHIVE-004 | ✓ |
| 검색 | `GET /api/v1/search?q=` | FR-SEARCH-002 | ✓ |
| 게임 | `GET /api/v1/encyclopedia` | FR-GAME-007 | ✓ |

`GET /api/v1/me`는 부트스트랩 엔드포인트 — 헤더가 필요한 닉네임·남은 횟수·캐러필러·Streak·칭호를 페이지 로드 시 1회에 받아 왕복을 줄이고 깜빡임을 막는다.

## §17.3 핵심 플로우 ① — 분석 생성 `POST /api/v1/analyses`

요청 본문 `{code, language?}`. 처리 순서:

1. **인증** — 쿠키 세션 → 현재 사용자.
2. **Rate Limit** — IP 분당 5회 초과 시 `429` (NFR-7.7).
3. **입력 검증 (1단계, 전처리 전 raw size)** — 입력 토큰 4,000 컷(HC-1)을 `validator.check_raw_size`로 검증. 초과 시 `400 InputTooLarge`.
4. **일일 한도 사전 체크** — `daily_used < daily_limit`? 소진 시 `429` (UX용 빠른 실패).
5. **입력 전처리(서버) + 검증 2단계** — 주석·공백 제거, 원본↔실질 라인 매핑 테이블 생성. 전처리 *후* 실질 라인 200줄 컷(HC-1)을 `validator.check_processed_lines`로 검증. 초과 시 `400 InputTooLarge`. *(③·⑤ 모두 같은 `InputTooLarge` 도메인 예외로 합류 — `07-technical-design.md` §33.1 참조.)*
6. **캐시 조회** — SHA-256 해시로 `analysis_cache` 조회. **HIT → 캐시 반환, 한도 차감 X, 캐러필러 X, 종료.** MISS → 계속.
7. **LLM 호출** — GPT-5 mini 1회, `max_tokens=8000`, 캐싱 prefix 정렬, 레벨 변수 주입(§19).
8. **응답 파싱·검증** — JSON을 Pydantic 검증, 깨지면 재시도(최대 3회), 3회 실패 → 운영자 알림 + `500`.
9. **단일 DB 트랜잭션** — Analysis INSERT + LineExplanation 다건 INSERT + KeyConcept UPSERT + analysis_cache INSERT(7일) + `User.daily_used` **조건부** +1(`WHERE daily_used < daily_limit`, 0행이면 롤백 + `429`) + Reward UPDATE(캐러필러+1, Streak) + daily_limit_log INSERT. **하나라도 실패 시 전체 롤백.**
10. **`201 Created`** + 분석 결과 JSON.

**설계 결정 둘.** ① 한도 차감을 LLM 호출 *뒤*, 저장과 *같은* 트랜잭션에 둔다 — LLM 실패 시 차감된 적 없고, 저장 실패 시 트랜잭션이 통째 롤백되며 차감도 되돌아간다. "롤백 로직" 없이 트랜잭션 원자성만으로 FR-ANALYSIS-010·FR-ARCHIVE-001 의도가 충족된다. ② 분석은 동기(synchronous) 처리 — 분석은 OpenAI 단일 호출이라 서버가 보고할 중간 단계가 없고("단계별 메시지"는 프론트 타이머 연출), P95 30초 안에 든다. 작업 큐는 Open Beta 부하 시 SSE로 검토.

## §17.4 핵심 플로우 ② — 추가 Leaf 확장

요청 본문 `{line_no}`. ① 인증+소유권 확인(아니면 `404`). ② **LLM 호출 먼저** — 그 라인의 깊은 해설만 생성하는 작은 호출. ③ `leaf_counter` 트랜잭션 — `==4`면 5번째: 한도 조건부 -1(0행이면 `429` 차단) + 카운터 0 리셋 + log(`leaf_5th`) / `<4`면 +1. ④ `200 OK` + `{line_no, deep_text}`. **DB 미저장** — 핀(📌) 전까지 브라우저 메모리에만(NFR-4). 핀 시 별도 `PATCH .../pin`이 `LineExplanation(tier='deep_pinned')`로 영구 저장.

## §17.5 횡단 관심사 + 스케줄 배치

**인증 — 서명된 쿠키 세션.** 로그인 성공 시 `user_id`를 담은 서명 HTTP-only 쿠키 발급(30일, `Secure`+`SameSite=Lax`). 서버 세션 테이블 불필요. 모든 보호 엔드포인트는 `get_current_user` 의존성 공유:

```python
from fastapi import Depends, HTTPException, Cookie

async def get_current_user(session: str | None = Cookie(default=None)) -> User:
    if not session:
        raise HTTPException(401, {"code": "NO_SESSION", "message": "🦜 로그인이 필요해"})
    user_id = verify_signed_cookie(session)   # 서명 검증 실패 시 예외
    return await load_user(user_id)
```

**에러·Rate Limit** — 4xx/5xx는 봉투 형식, 기계용 `code` + 코뉴 말투 `message`. Rate limit은 Pre-MVP 인메모리, Closed Beta+ Redis.

**자정 KST 스케줄 배치(비-엔드포인트)** — 매일 00:00 KST 단일 배치가 ① 전 사용자 `daily_used` 0 리셋, ② Streak 평가(어제 0건 + 방패 보유 → 자동 발동 / 없으면 Streak 0), ③ `cost_daily` 집계. PRD §7.8·NFR-5가 이미 전제한 모델이라 스키마 변경 불필요. 멱등 재실행으로 복구.

## §17.6 응답·상태 코드 표준

| 코드 | 의미 | 대표 상황 |
|---|---|---|
| `200` | 조회·수정 성공 | `GET /me`, Leaf 확장 |
| `201` | 자원 생성 | `POST /analyses` |
| `400` | 입력 자체 오류 | 200줄·4K 토큰 초과 |
| `401` | 인증 없음·만료 | 쿠키 없음/위조 |
| `404` | 자원 없음·소유 아님 | 남의 분석 접근 |
| `429` | 한도·빈도 초과 | 일일 한도 소진, Rate Limit |
| `500` | 서버·LLM 실패 | LLM 3회 재시도 실패 |

> ※ 각 status에 대응하는 백엔드 도메인 예외(`DomainError` 6종)와 프론트 `ApiError.code`의 전체 매핑은 `07-technical-design.md` §36.1 SSoT 표 참조. 본 표는 HTTP 응답 코드 차원만 다룬다.

일일 한도 소진은 `403`이 아니라 `429` — "권한 없음"이 아니라 "지금 너무 많이 함, 자정에 풀림"이 정확하다. 프론트는 `429`+`code`로 한도 소진과 Rate Limit을 구분.

## §17.7 다시 숲 — §17 정리

| 구분 | 결정 |
|---|---|
| API 스타일 | REST, `/api/v1/`, 명사 자원 + HTTP 동사 |
| 인증 | 서명 HTTP-only 쿠키, `get_current_user` 공유 (세션 테이블 없음) |
| 부트스트랩 | `GET /api/v1/me` 1회 |
| 분석 생성 | 동기, 캐시 우선, 한도 차감을 저장과 단일 트랜잭션 |
| Leaf 확장 | LLM 먼저 → `leaf_counter` 트랜잭션, 미핀은 DB 미저장 |
| 스케줄 배치 | 자정 KST 단일 배치 |
| 에러 | `{error:{code,message}}`, 한도 소진은 `429` |

---

# §18. 프론트엔드 상세

## §18.1 아키텍처 조감

Vite 빌드 산출물(정적 HTML+JS+CSS)을 Vercel CDN 배포. React SPA는 ① 부팅 시 `GET /api/v1/me` 1회로 인증+게이미피케이션 부트스트랩, ② React Router 클라이언트 라우팅(페이지 전환 시 서버 왕복 없음), ③ 라우트별 페이지 렌더링.

```
/login → LoginPage(공개)  ·  / → DashboardPage(보호, 분석 메인)
/analysis/:uuid → AnalysisDetail  ·  /archive → ArchivePage
/search → SearchPage  ·  /encyclopedia → EncyclopediaPage  ·  /settings → SettingsPage
```

## §18.2 디자인 토큰 → CSS 변수 시스템

04 §4·§5·§7 토큰을 `:root` CSS 커스텀 프로퍼티로 등록. 토큰을 한 곳에 모으면 색 변경이 변수 한 줄이고, 라이트 테마(FR-OUTPUT-010, Closed Beta)는 `[data-theme="light"]` 오버라이드로 끝난다.

```css
:root {
  /* ── 브랜드 액센트 — 04 §4 확정 ── */
  --color-orange:  #E8631A;   /* CTA·Active·Link·Hover Border */
  --color-yellow:  #F5C200;   /* 🐛캐러필러·🔥Streak·배지·강조 */
  --color-green:   #5BA020;   /* ●Analyzed/Success 전용 (CTA·내비 금지) */
  --color-base:    #1A1A1A;   /* 베이스 다크 (NFR-8) */
  /* ── 상태 토큰 — 04 §5 확정 ── */
  --state-ready:     #888888;
  --state-analyzing: var(--color-yellow);
  --state-analyzed:  var(--color-green);
  --slot-empty:      #3C3C3C;
  /* ── 타이포 — FR-OUTPUT-008 확정 ── */
  --font-code: "JetBrains Mono", "IBM Plex Mono", monospace;
  --font-ui:   "Pretendard", system-ui, sans-serif;
  /* ── 모션 — 04 §7 확정 ── */
  --motion-fast:   120ms;
  --motion-steps:  steps(8, end);          /* 픽셀 끊김 (N=8 제안값) */
  --shadow-pixel:  -3px 3px 0 0 var(--color-yellow);
  --hover-shift:   translate(3px, -3px);
  /* ── 다크 중립색 — TRD 제안, Stage 8 확정 대상 ── */
  --surface:       #242424;
  --border-pixel:  #3C3C3C;
  --text-primary:  #EAEAEA;
  --text-muted:    var(--state-ready);
  /* ── 간격 스케일 — TRD 제안 (8px 그리드) ── */
  --space-1: 4px; --space-2: 8px; --space-3: 16px;
  --space-4: 24px; --space-6: 48px;
  --border-width: 2px;
}
```

> "확정" 그룹(액센트·상태·타이포·모션)은 04·PRD 직접 인용. "TRD 제안" 그룹(중립색·간격·`steps()` N)은 작동하는 다크 테마를 위한 보강분 — Stage 8 디자인 2차 확정 대상.

## §18.3 컴포넌트 구조 (레이아웃 비의존)

```
<App>
 ├ <AppDataProvider>          ← 전역 상태 (사용자+게이미피케이션)
 └ <Router>
     ├ <LoginPage>
     └ <ProtectedRoute>
         ├ <DashboardPage>     ★ 분석 메인
         │   ├ <StatsBar>          헤더 — 캐러필러·Streak·도감·아카이브·칭호·남은 횟수
         │   ├ <CodeInput>         🍃 중앙 — textarea + 분석 CTA
         │   ├ <LoadingSkeleton>
         │   └ <ResultView>        ├ <ForestPanel> <TreePanel>
         │                         ├ <LeafColumn> ├ <LeafLine> └ <LeafExpandModal>
         │                         └ <FolderTree>
         ├ <AnalysisDetailPage>  ← <ResultView> 재사용
         ├ <ArchivePage> <SearchPage> <EncyclopediaPage> <SettingsPage>
 └ <Conu>                      ← 픽셀 앵무새 마스코트
```

`<ResultView>`는 한 번 만들어 갓 분석한 결과(`DashboardPage`)와 아카이브 상세(`AnalysisDetailPage`)에 재사용 — 데이터 출처만 다르고 화면은 동일. `<Conu>`는 Pre-MVP에서 칭호 4단계 이모지 조합(🥚🪶🌲🎩×🦜)으로 렌더링, P1에 캐릭터 자산으로 내부만 교체.

## §18.4 상태 관리

전역 상태가 작아(사용자 + 카운터) **React Context + hooks**로 충분 — Redux는 보일러플레이트 과잉, Zustand는 불필요한 추가 의존성. `AppDataProvider`가 부팅 시 `GET /me`로 ①사용자 ②게이미피케이션 카운터를 채우고, 분석 성공마다 갱신. 데이터 페칭은 `fetch` 래퍼 커스텀 훅(`useApi`), React Query는 Closed Beta 검토.

## §18.5 라우팅

React Router + `<ProtectedRoute>` 래퍼 — 사용자 미로드 / `GET /me` `401`이면 `/login` 리다이렉트. `/analysis/:uuid`는 UUID URL(FR-ARCHIVE-006)로 북마크 가능·일련번호 비노출. **프론트 가드는 보안이 아니라 UX** — 진짜 차단은 §17.5 백엔드 쿠키 검증. JavaScript는 사용자가 조작 가능하므로 프론트엔드를 보안으로 신뢰하지 않는다.

## §18.6 AI 슬롭 차단 — CSS 규율

| 항목 | ❌ 금지 (AI 슬롭) | ✅ 강제 (픽셀아트) |
|---|---|---|
| 모서리 | `border-radius` 둥근 알약 | 직각/1~2px 픽셀 코너 |
| 그림자 | 흐릿한 blur 그림자 | 하드 오프셋 `--shadow-pixel`(blur 0) |
| 배경 | 그라데이션·글래스모피즘 | `--color-base` 단색 다크 |
| 모션 | 매끄러운 `ease` | `--motion-steps`(`steps()`) |
| 폰트 | 제네릭 Inter/Roboto | `--font-code`/`--font-ui`만 |
| 색 | 무지개 팔레트 | 브랜드 3색 + 중립색만 |

## §18.7 다시 숲 — §18 정리

| 구분 | 결정 |
|---|---|
| 앱 형태 | React SPA, Vite 빌드 → Vercel 정적 배포 |
| 디자인 토큰 | 04 → `:root` CSS 변수 (확정분/제안분 명시) |
| 테마 | Pre-MVP 다크, 라이트는 `[data-theme]` 오버라이드 |
| 컴포넌트 | 레이아웃 비의존, `<ResultView>` 재사용 |
| 상태 관리 | React Context + hooks |
| 라우팅 | React Router, `<ProtectedRoute>`(UX), UUID URL |
| AI 슬롭 | NFR-8을 CSS 6항목 규율로 |

> ※ 데스크톱 레이아웃 A(Triptych) vs B(Code Center) 택1(04 D-1)은 Stage 8 디자인 2차 — §18은 비의존 골격만.

---

# §19. LLM 연동 · 프롬프트 아키텍처

## §19.1 LLM 호출 1건 조감

분석은 **단 1회의 LLM 호출** — Forest·Tree·모든 짧은 해설·핵심 깊은 Leaf 5개·태그·Key Concepts가 한 응답에 전부 담겨 온다(FR-ANALYSIS-006). 계층별로 쪼개지 않는다 — 쪼개면 비용·지연이 N배이고 계층 간 맥락이 끊긴다.

## §19.2 프롬프트 2블록 + 캐싱 prefix

NFR-1("시스템 프롬프트~800 + Few-shot~1,200 = ~2,000 토큰을 캐싱, 적중률 ≥90% 목표")을 2블록 배치로 실현:

- **BLOCK A — 캐싱 prefix (~2,000T, 절대 불변)**: 시스템 프롬프트(역할·3계층 방법론·출력 규칙·JSON 스키마·AI 슬롭/톤) + Few-shot 예시. 모든 호출·사용자·레벨에서 동일.
- **BLOCK B — 변동부**: 학습자 레벨 지시(1·2·3 중 1개) + 전처리된 코드.

불변 BLOCK A를 맨 앞에 둬 레벨 1·2·3 호출이 동일 prefix를 공유한다. 레벨을 앞에 두면 레벨 변경 시 그 뒤 캐시가 어긋난다.

> **단서**: 적중률 ≥90%는 Beta 정상 트래픽 기준(prefix가 hot 유지). Pre-MVP 단독 사용은 캐시 TTL 만료로 미달이 정상 — 무료 API라 무관, 비용 절감 주축은 NFR-3 SHA 캐시.

## §19.3 출력 JSON 계약

LLM 반환 형태: `{forest, tree, line_explanations:[{line_no, short}], deep_leaves:[{line_no, deep}], tags, key_concepts}` (FR-ANALYSIS-006). **OpenAI Structured Outputs(`response_format: json_schema`) 강제** — 스키마 출처는 §17.3의 Pydantic 모델(백엔드 검증 모델과 LLM 출력 계약이 단일 소스). 형식 위반은 거의 사라진다. 단 `max_tokens` 절단(`finish_reason='length'`)은 스키마 강제로도 못 막으므로 §19.6 절단 처리가 필요.

> **SSoT 명시**: JSON 스키마의 단일 진실은 `backend/schemas/llm.py:LLMAnalysisOutput`(Pydantic 모델). OpenAI 호출 시 이 모델로부터 JSON 스키마를 *자동 추출*해 `response_format=json_schema`에 주입한다. *스키마 변경 = Pydantic 모델 변경 = 자동 반영* — 양쪽에 따로 적지 않는다. (`07-technical-design.md` §34 데이터 계약 28개 모델 참조.)

## §19.4 학습자 레벨 주입

BLOCK B에 `{level_instruction}` 슬롯 — `User.learner_level`(**1·2·3**) 값에 따라 4개가 아닌 **3개** 지시 블록 중 하나 주입. 레벨 콘텐츠 SSoT는 Discovery §6 레벨 정의 표.

| 항목 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|
| 자가진단 | "python? 뱀이라는 풍문" | "Hello world 띄워봄" | "py파일 늘었음" |
| 용어 풀이 | 전부 괄호 풀이 | 핵심·중급만 | 고급 개념만 |
| 비유 | 모든 깊은 해설 필수 | 가끔 | 거의 없음 |
| 출력 길이 | 길게 | 표준 | 압축 |

> 메뉴 4번(자동 추천)은 레벨값이 아니라 `learner_level_auto=TRUE` 모드 — 시스템이 1·2·3 중 할당. 칭호(누적 횟수 4단계)와 레벨(자가진단 3단계)은 별개 체계.

## §19.5 입력 포맷 — 원본 라인 번호 태깅

전처리된 코드를 각 라인에 **원본 라인 번호 태깅**해 전달(`L1: ...`, `L5: ...` — 주석 제거로 번호 건너뜀). LLM은 `line_no`에 원본 번호를 직접 반환 — 백엔드 되번역 불필요(FR-ANALYSIS-006 "원본 번호 보존"). 원본↔실질 매핑 테이블은 프론트 구조 렌더링용으로 별도 유지.

## §19.6 LLM 실패 처리

| 실패 모드 | 신호 | 처리 |
|---|---|---|
| 출력 절단 | `finish_reason=='length'` | 재시도. NFR-2가 <1% 감시 |
| API 오류 | OpenAI 5xx·타임아웃·rate limit | 지수 백오프 재시도 |
| 스키마 위반 | Pydantic 검증 실패 | 거의 없음, 발생 시 재시도 |

최대 3회 재시도 → 실패 시 운영자 알림 + `500` + 코뉴 말투 안내. §17.3 설계상 LLM 끝까지 실패 시 한도 미차감(차감이 LLM 성공 뒤라 자동).

## §19.7 다시 숲 — §19 정리

| 구분 | 결정 |
|---|---|
| 호출 | 분석 = LLM 1회, 3계층 한 응답 |
| 프롬프트 | BLOCK A(불변·캐싱) + BLOCK B(변동) |
| JSON | Structured Outputs 강제, Pydantic 단일 소스 |
| 레벨 | `{level_instruction}` 슬롯, 레벨 1·2·3 |
| 입력 | 원본 라인 번호 태깅 |
| 실패 | 3회 재시도 → 운영자 알림, 한도 미차감 |

> ※ §19 결정은 PRD v0.8 패치(FR-ANALYSIS-012 상세 블록·NFR-1 비고·레벨 1·2·3)에 반영 완료.

---

# §20. 배포 · 인프라 · 운영

## §20.1 배포 토폴로지

```
[사용자] ─ HTTPS ─→ Vercel CDN ──→ React SPA (정적 번들)
         ─ HTTPS ─→ Railway ──┬─→ FastAPI 앱 (uvicorn)
                               ├─→ PostgreSQL (매니지드)
                               └─→ Cron 서비스 (자정 KST 배치)
              FastAPI ──→ OpenAI API (GPT-5 mini)  ·  Resend (이메일, Closed Beta)
```

프론트엔드(Vercel)와 백엔드(Railway)는 별개 deployment. 따라오는 둘: ① **CORS** — FastAPI가 프론트 도메인 요청을 허용 명시. ② **쿠키 도메인** — 커스텀 도메인 1개를 사 서브도메인으로 분리(`codedecoder.app` / `api.codedecoder.app`)하면 세션 쿠키가 퍼스트파티라 `SameSite=Lax`로 안전. 기본 도메인(`vercel.app`/`railway.app`)은 크로스사이트라 쿠키 처리가 까다롭다.

## §20.2 배포 파이프라인

- **프론트엔드**: git push → Vercel 자동 `vite build` → CDN 배포. 브랜치별 미리보기 배포.
- **백엔드**: git push → Railway가 Python 감지 → 의존성 설치 → uvicorn 기동.
- **DB 마이그레이션**: 새 앱이 트래픽을 받기 *전*에 `alembic upgrade head`를 배포 단계에서 실행 — 코드가 기대하는 스키마(예: `leaf_counter`)를 DB에 선반영. 새 가구를 들이기 전 방 구조를 맞추는 순서.

## §20.3 환경변수 · 시크릿 인벤토리

**철칙: 시크릿은 git에 올리지 않는다.** 플랫폼 env 저장소에만 두고 코드엔 `.env.example`(빈 자리표시자)만 커밋.

| 시크릿 | 용도 | 위치 | 단계 |
|---|---|---|---|
| `OPENAI_API_KEY` | LLM 호출 | Railway env (BE) | Pre-MVP |
| `DATABASE_URL` | Postgres 접속 | Railway 자동 주입 (BE) | Pre-MVP |
| `SESSION_SECRET` | 쿠키 서명 키 | Railway env (BE) | Pre-MVP |
| `RESEND_API_KEY` | 이메일 | Railway env (BE) | Closed Beta |
| `KAKAO`/`GOOGLE_OAUTH_SECRET` | 소셜 로그인 | Railway env (BE) | Closed Beta |
| `TOSS_SECRET_KEY` | 결제 | Railway env (BE) | Open Beta |
| `VITE_API_BASE_URL` | 백엔드 주소 | Vercel env (FE, 빌드타임) | Pre-MVP |

**`VITE_` 변수는 전부 공개** — 정적 번들에 구워져 누구나 열어본다. 프론트엔드에는 진짜 비밀을 두지 않고, `OPENAI_API_KEY` 등은 백엔드에만 둔다. 이것이 모든 LLM 호출을 백엔드가 중개하는 이유이자 BYOK를 버린 구조적 근거.

## §20.4 스케줄 배치 운영

§17.5의 자정 KST 단일 배치(daily_used 리셋 + Streak·방패 + cost_daily)를 Railway Cron으로 **00:00 KST = 15:00 UTC** 실행. ① **멱등성** — 두 번 돌려도 안전(이미 0인 값 재리셋은 무해). ② **실패 감시** — 배치 미실행 시 한도가 안 풀려 사용자가 묶이므로 성공/실패 로깅 + 실패 시 운영자 알림.

## §20.5 모니터링 · 관측 (NFR-5)

| 지표 | 출처 | 무엇을 보나 |
|---|---|---|
| 일별 비용·호출·토큰 | `cost_daily` (§16.3) | NFR-5 비용선(₩400/₩600 알림) |
| 출력 절단율 | `finish_reason='length'` 로그 | NFR-2 — <1% 목표 |
| 프롬프트 캐시 적중 | `usage.prompt_cache_hit_tokens` | NFR-1 — Beta 기준 ≥90% |
| SHA 캐시 적중 | `analysis_cache.hit_count` | NFR-3 절감 효과 |
| LLM 3연속 실패 | §17.3·§19.6 알림 | 즉시 운영자 알림 |

데이터는 Pre-MVP부터 테이블·로그에 적재, ₩400/₩600 알림·대시보드 UI는 Closed Beta 발효(NFR-5). 센서는 처음부터 켜고 계기판은 나중에 단다.

## §20.6 백업·복구 + 인프라 재평가

**배포 전략 확정** — **Vercel + Railway** (Pre-MVP·Closed Beta). Render와 비교 검토 결과: Render의 강점(PITR 백업, Cron 1등급)은 *Open Beta 가치*이고, 지금 전환은 §15·§17·§20 재작성 + 마감 리스크를 부른다. 백엔드 호스트 이전은 락인이 거의 없어(둘 다 FastAPI 컨테이너 + Postgres + Vercel 100% 프록시) 나중에 해도 저렴 — 결정을 미루는 비용이 거의 0이다.

**백업·복구 (DB 유실 방어)** — 데이터 유실 방어의 실제 해답은 플랫폼이 아니라 백업 규율이다:
- **일 1회 `pg_dump`를 외부 스토리지에 떨군다** (Pre-MVP부터). 스키마는 Alembic(코드)으로, 데이터는 pg_dump로 이중 보관.
- **백업 산출물 암호화·접근 통제** — `pg_dump` 산출물은 DB 전체(사용자 코드 + PII)의 평문 사본이므로, 외부 스토리지에 업로드하기 *전*에 자체 보유 키로 암호화하고 스토리지 버킷에 접근 통제를 적용한다. 백업 파일이 유출되거나 스토리지 사업자 측에서 접근당해도 키 없이는 복호화 불가. (근거: `06-security.md` §24.4 — 부록 A 패치 ②.)
- **백업 보존 주기 30일** — 최근 30일치 일일 덤프만 보관하고 그보다 오래된 덤프는 자동 폐기. HC-10으로 라이브 DB에서 hard delete된 탈퇴자 데이터가 백업 사본에서도 늦어도 30일 내 완전 소멸함을 보장한다. (근거: `06-security.md` §28.5.)
- Pre-MVP·Closed Beta 규모(본인 + 동기 3-5명 테스트 데이터)는 일 1회 덤프로 완전히 커버. PITR(1초 단위 복구)은 유료 고객 이력이 쌓이는 Open Beta의 가치.

**Open Beta 인프라 재평가 체크포인트** — 실결제·사업자등록 시점에 Railway 현행 백업 역량 vs Render PITR vs 기타를 재비교. PITR·비용 예측이 진짜 값하는 그 단계에 다시 판단한다. (플랫폼 가격·백업 정책은 수시 변동 — 재평가 시 공식 페이지로 재확인.)

## §20.7 다시 숲 — §20 정리

| 구분 | 결정 |
|---|---|
| 토폴로지 | FE=Vercel / BE·DB·Cron=Railway, 별개 deployment |
| 도메인·쿠키 | 커스텀 도메인 + 서브도메인 → 퍼스트파티 쿠키 |
| 배포 | git push 자동 빌드, `alembic upgrade head`를 배포 단계에 |
| 시크릿 | 플랫폼 env에만, git 금지. `VITE_`는 공개 — 진짜 키는 BE |
| 배치 | 자정 KST Railway Cron, 멱등 + 실패 감시 |
| 모니터링 | 데이터는 Pre-MVP부터, 대시보드·알림은 Closed Beta |
| 배포 전략 | **Vercel + Railway 확정** (Pre-MVP·Closed Beta) |
| 백업 | 일 1회 `pg_dump` 외부 보관(업로드 전 암호화 + 접근통제) · 30일 보존 주기 · Alembic 스키마 |
| 재평가 | Open Beta 시점에 Railway vs Render 재비교 |

---

# 부록 — 정합성 점검 · 후속 안건

## A. TRD ↔ PRD v0.10 ↔ Discovery v4 정합성 점검

| 영역 | TRD | 상호 SSoT | 상태 |
|---|---|---|---|
| 기술 스택 | §15 FastAPI·React+Vite·SQLModel | PRD §9(v0.5 패치)·Discovery §15(v4) | ✅ 일치 |
| `leaf_counter`·`daily_limit` | §16 | PRD §7.1(v0.6 패치) | ✅ 일치 |
| `max_tokens` 8,000 | §17·§19 | PRD NFR-2·FR-ANALYSIS-006·FR-OUTPUT-003/004(v0.7 패치) | ✅ 일치 |
| 학습자 레벨 1·2·3 | §19 | PRD FR-ANALYSIS-012·NFR-1(v0.8 패치)·Discovery §6(v4) | ✅ 일치 |
| 디자인 토큰 | §18.2 | 04-design-decisions §4·§5·§7 | ✅ 일치 |
| 배포 | §20 Railway | PRD §9·Discovery §15(v4) | ✅ 일치 |

PRD v0.5~v0.10 / Discovery v3~v4 패치가 TRD 작성 중 발견된 충돌을 그때그때 정정한 결과, 3자 정합성 클린.

## B. 후속 안건 (TRD 범위 밖, 별도 처리)

| # | 안건 | 처리 시점 |
|---|---|---|
| 1 | Open Beta 인프라 재평가 (Railway vs Render·PITR·비용) | Open Beta 진입 시 (§20.6) |
| 2 | 데스크톱 레이아웃 A(Triptych) vs B(Code Center) 택1 | Stage 8 디자인 2차 (04 D-1) |
| 3 | UC-2/UC-3·설정·도감 화면 와이어프레임 보강 | Stage 8 (04 D-2) |
| 4 | Discovery §17 모바일 OOS 범위 ↔ PRD §11.1 divergence 정리 | 다음 Discovery 갱신 |
| 5 | 칭호 명칭 ↔ PRD FR-GAME-003 본문 일치 확인 | 다음 PRD 갱신 (minor) |
| 6 | 학습자 레벨 2~4 자동 재추천 알고리즘 상세 (FR-ANALYSIS-013) | Closed Beta 전 |

---

*Code Decoder MVP — Stage 5 TRD v0.2 (2026-05-19 · §15~§20 통합 완료본 + Stage 6 보안 패치 ②·④ 반영 · 참조 PRD v0.10 · Discovery v4 · security v0.3)*
