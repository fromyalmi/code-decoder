# 🌲 Code Decoder

> **개발 비전공자를 위한 코드 해설 웹앱**  
> 코드를 '숲 → 나무 → 가지' 구조로 분해하고, 자동 태깅·아카이브로 학습 흔적을 쌓는다.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![OpenAI](https://img.shields.io/badge/OpenAI_API-GPT--4o-412991?style=flat-square&logo=openai)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)

---

## 📌 왜 만들었나

AI 학습 과정에서 코드를 처음 마주치는 개발 비전공자들은 공통적인 장벽을 겪는다.  
코드 한 줄을 이해하려다 전체 맥락을 잃고, 설명을 읽어도 어디서부터 어디까지가 '덩어리'인지 모른다.

**Code Decoder**는 이 문제를 계층적 해설로 푼다.  
전체 흐름(숲) → 핵심 블록(나무) → 세부 구현(가지)으로 쪼개서 보여주고,  
태그와 아카이브로 학습 이력을 누적한다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🌲 **Forest/Tree/Branch 해설** | 입력 코드를 3단계 계층으로 분해하여 설명 |
| 🏷️ **자동 태깅** | 코드 내 핵심 개념을 자동 추출·태그화 |
| 🗂️ **아카이브** | 분석 이력을 저장하고 검색 가능하게 유지 |
| 🔍 **키 컨셉 추출** | 학습에 필요한 개념어를 별도로 정리 |

---

## 🏗️ 기술 스택

```
Frontend   React 18
Backend    FastAPI (Python 3.11)
DB         PostgreSQL 15
AI         OpenAI API (GPT-4o)
```

---

## 🗄️ DB 스키마

```
code_entries          분석 요청된 코드 원문
    │
    ├── analysis_results    Forest/Tree/Branch 분석 결과
    ├── key_concepts        추출된 핵심 개념어
    └── code_tags (N:M)     태그 연결 테이블
             │
           tags             태그 마스터 테이블
```

---

## 🚀 로컬 실행

### 1. 레포 클론

```bash
git clone https://github.com/YOUR_USERNAME/code-decoder.git
cd code-decoder
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에서 아래 값 설정
# OPENAI_API_KEY=...
# DATABASE_URL=postgresql://...
```

### 3. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

---

## 🗓️ 개발 로드맵

| 주차 | 목표 |
|------|------|
| 1주차 | DB 스키마 확정, FastAPI 기본 구조 |
| 2주차 | OpenAI API 연동, 분석 엔진 구현 |
| 3주차 | 태깅·아카이브 기능 |
| 4주차 | React 프론트엔드 연결 |
| 5주차 | UI 완성, 통합 테스트 |
| 6주차 | 배포, 포트폴리오 정리 |

완료 목표: **2026년 5월 말**

---

## 👤 만든 사람

**Yalmi**  
개발 비전공자 출신 AI 학습자이자 독립 출판 경험자.  
AI 도구를 비개발자 관점에서 설계하고 상용화하는 데 관심이 있다.

---

## 📄 License

© 2026 Yalmi. All rights reserved.  
본 레포지토리의 코드 및 콘텐츠는 저작권자의 명시적 허가 없이 복제·배포·상업적 이용이 금지됩니다.
