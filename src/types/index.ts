// 모든 공유 타입 정의 — 이 파일 외부에서 타입을 인라인으로 정의하지 마라

/** 탭 종류 */
export type TabType = 'forest' | 'tree' | 'concept'

/** OpenAI API 응답 스키마 — 이 형태가 아니면 validateResponse에서 에러 */
export interface AnalysisResult {
  forest_view: string
  complexity: 'low' | 'medium' | 'high'
  language: string
  tree_view: Array<{
    line: number
    code: string
    explanation: string
    logic_type: string
  }>
  concept_view: Array<{
    term: string
    description: string
    core_commands: string[]
  }>
}

/** concept_view 단일 항목 편의 타입 */
export type ConceptItem = AnalysisResult['concept_view'][number]

/** tree_view 단일 항목 편의 타입 */
export type TreeItem = AnalysisResult['tree_view'][number]

/** 저장된 개념 카드 — IndexedDB cards 스토어에 저장 */
export interface SavedCard {
  id: string
  userId: 'local'           // MVP에서는 반드시 "local" 고정 (절대 규칙 #8)
  term: string
  description: string
  core_commands: string[]
  savedAt: number           // Date.now() 타임스탬프
}

/** 히스토리 항목 — IndexedDB history 스토어에 저장 (최대 50건) */
export interface HistoryEntry {
  id: string
  userId: 'local'           // MVP에서는 반드시 "local" 고정 (절대 규칙 #8)
  code: string
  result: AnalysisResult
  createdAt: number         // Date.now() 타임스탬프
}
