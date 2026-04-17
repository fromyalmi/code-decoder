// src/types/index.ts
// Code Decoder MVP — 전체 타입 정의
// MVP에서 userId는 "local" 고정 / v2.0~에서 실제 유저 ID 사용 예정

/** 탭 타입 */
export type TabType = 'forest' | 'tree' | 'concept' | 'myCards' | 'history'

/** 나무 탭: 라인별 설명 아이템 */
export interface TreeItem {
  line_range: string        // 예: "1-3", "5"
  code_snippet: string
  explanation: string
}

/** 개념 탭: 개념카드 아이템 */
export interface ConceptItem {
  term: string
  description: string
  core_commands: string[]
}

/** OpenAI API 응답 스키마 — validateResponse에서 검증 */
export interface AnalysisResult {
  language: string
  complexity: 'beginner' | 'intermediate' | 'advanced'
  forest_view: string
  tree_view: TreeItem[]
  concept_view: ConceptItem[]
}

/** 저장된 개념카드 — IndexedDB cards 스토어에 저장 */
export interface SavedCard {
  id: string
  userId: 'local'           // MVP: "local" 고정 (미래 태스크 #8)
  term: string
  description: string
  core_commands: string[]
  savedAt: number           // Date.now() 타임스탬프
  sourceCodePreview: string // 저장 시점의 코드 앞 100자
  promptVersion: string     // 예: "v1.0"
}

/** 히스토리 엔트리 — IndexedDB history 스토어에 저장 */
export interface HistoryEntry {
  id: string
  userId: 'local'           // MVP: "local" 고정 (미래 태스크 #8)
  preview: string           // 코드 앞 50자 (목록 표시용)
  code: string
  result: AnalysisResult
  savedAt: number           // Date.now() 타임스탬프
  language: string
  promptVersion: string     // 예: "v1.0"
}