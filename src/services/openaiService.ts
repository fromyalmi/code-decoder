// OpenAI API fetch + Exponential Backoff 재시도 로직

import type { AnalysisResult, TreeItem, ConceptItem } from '../types/index'

// ─── 상수 ─────────────────────────────────────────────────────────────────────

const API_URL = 'https://api.openai.com/v1/chat/completions'
const MODEL = 'gpt-4o-mini'
const MAX_RETRIES = 3
const BASE_DELAY_MS = 1000

const SYSTEM_PROMPT = `당신은 비전공자를 위한 코드 해설 AI입니다.
사용자가 코드를 제출하면 반드시 아래 JSON 형식으로만 응답하세요.
마크다운 코드 블록(\`\`\`)을 절대 사용하지 마세요. 순수 JSON만 반환하세요.

응답 형식:
{
  "language": "감지된 프로그래밍 언어명 (예: Python, JavaScript)",
  "complexity": "beginner | intermediate | advanced 중 하나",
  "forest_view": "코드 전체 목적을 비전공자가 이해할 수 있는 비유로 2-3문장 설명",
  "tree_view": [
    {
      "line_range": "1-3",
      "code_snippet": "해당 라인의 실제 코드",
      "explanation": "이 코드가 하는 일을 쉬운 말로 설명"
    }
  ],
  "concept_view": [
    {
      "term": "핵심 개념 용어",
      "description": "비전공자를 위한 개념 설명",
      "core_commands": ["관련 명령어 또는 키워드"]
    }
  ]
}

규칙:
- tree_view는 의미 단위로 묶어서 라인 범위(line_range)로 표현하세요.
- concept_view는 코드에서 등장하는 핵심 개념 3-5개를 골라주세요.
- 모든 설명은 한국어로 작성하세요.`

// ─── 스키마 검증 ──────────────────────────────────────────────────────────────

/** API 응답 데이터를 AnalysisResult로 검증 — 필수 필드 누락 또는 잘못된 값이면 Error throw */
function validateResponse(data: unknown): AnalysisResult {
  if (typeof data !== 'object' || data === null) {
    throw new Error('응답이 객체 형식이 아닙니다.')
  }

  const d = data as Record<string, unknown>

  if (typeof d['language'] !== 'string' || d['language'].trim() === '') {
    throw new Error('필수 필드 누락: language')
  }

  const validComplexity = ['beginner', 'intermediate', 'advanced'] as const
  if (!validComplexity.includes(d['complexity'] as (typeof validComplexity)[number])) {
    throw new Error(
      `complexity 값이 올바르지 않습니다: "${String(d['complexity'])}". beginner | intermediate | advanced 중 하나여야 합니다.`
    )
  }

  if (typeof d['forest_view'] !== 'string' || d['forest_view'].trim() === '') {
    throw new Error('필수 필드 누락: forest_view')
  }

  if (!Array.isArray(d['tree_view'])) {
    throw new Error('필수 필드 누락: tree_view (배열이어야 합니다)')
  }

  for (const item of d['tree_view'] as unknown[]) {
    if (typeof item !== 'object' || item === null) {
      throw new Error('tree_view 항목이 객체 형식이 아닙니다.')
    }
    const t = item as Record<string, unknown>
    if (typeof t['line_range'] !== 'string') throw new Error('tree_view 항목 누락: line_range')
    if (typeof t['code_snippet'] !== 'string') throw new Error('tree_view 항목 누락: code_snippet')
    if (typeof t['explanation'] !== 'string') throw new Error('tree_view 항목 누락: explanation')
  }

  if (!Array.isArray(d['concept_view'])) {
    throw new Error('필수 필드 누락: concept_view (배열이어야 합니다)')
  }

  for (const item of d['concept_view'] as unknown[]) {
    if (typeof item !== 'object' || item === null) {
      throw new Error('concept_view 항목이 객체 형식이 아닙니다.')
    }
    const c = item as Record<string, unknown>
    if (typeof c['term'] !== 'string') throw new Error('concept_view 항목 누락: term')
    if (typeof c['description'] !== 'string') throw new Error('concept_view 항목 누락: description')
    if (!Array.isArray(c['core_commands'])) throw new Error('concept_view 항목 누락: core_commands')
  }

  return {
    language: d['language'] as string,
    complexity: d['complexity'] as AnalysisResult['complexity'],
    forest_view: d['forest_view'] as string,
    tree_view: d['tree_view'] as TreeItem[],
    concept_view: d['concept_view'] as ConceptItem[],
  }
}

// ─── API 호출 (단일 시도) ─────────────────────────────────────────────────────

async function fetchAnalysis(code: string): Promise<AnalysisResult> {
  const apiKey = import.meta.env.VITE_OPENAI_API_KEY as string | undefined
  if (!apiKey) {
    throw new Error('VITE_OPENAI_API_KEY가 설정되지 않았습니다.')
  }

  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: MODEL,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: code },
      ],
    }),
  })

  if (!response.ok) {
    // 429: Rate limit — 재시도 가능 / 그 외: 즉시 에러
    const errorText = await response.text()
    throw new Error(`OpenAI API 오류 (${response.status}): ${errorText}`)
  }

  const json = (await response.json()) as {
    choices: Array<{ message: { content: string } }>
  }
  const content = json.choices[0]?.message?.content
  if (!content) {
    throw new Error('OpenAI 응답에 content가 없습니다.')
  }

  const parsed: unknown = JSON.parse(content)
  return validateResponse(parsed)
}

// ─── Exponential Backoff 재시도 ───────────────────────────────────────────────

/** 코드를 분석하고 AnalysisResult를 반환 — 최대 3회 재시도 (1s → 2s → 4s) */
export async function analyzeCode(code: string): Promise<AnalysisResult> {
  let lastError: Error = new Error('알 수 없는 오류')

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      return await fetchAnalysis(code)
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err))
      console.error(`분석 시도 ${attempt + 1}회 실패:`, lastError.message)

      // 마지막 시도였으면 대기 없이 루프 종료
      if (attempt < MAX_RETRIES - 1) {
        const delay = BASE_DELAY_MS * Math.pow(2, attempt) // 1000 → 2000 → 4000
        await new Promise((resolve) => setTimeout(resolve, delay))
      }
    }
  }

  throw lastError
}
