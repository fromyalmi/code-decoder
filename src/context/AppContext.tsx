// 전역 상태 관리 — useReducer + Context (외부 상태 라이브러리 사용 금지)

import { createContext, useContext, useReducer } from 'react'
import type { ReactNode } from 'react'
import type { TabType, AnalysisResult } from '../types/index'

// ─── State ──────────────────────────────────────────────────────────────────

interface AppState {
  activeTab: TabType
  rawCode: string
  analysisResult: AnalysisResult | null
  isLoading: boolean
  error: string | null
}

const initialState: AppState = {
  activeTab: 'forest',
  rawCode: '',
  analysisResult: null,
  isLoading: false,
  error: null,
}

// ─── Actions ─────────────────────────────────────────────────────────────────

type Action =
  | { type: 'SET_CODE'; payload: string }
  | { type: 'SWITCH_TAB'; payload: TabType }
  | { type: 'ANALYSIS_START' }
  | { type: 'ANALYSIS_SUCCESS'; payload: AnalysisResult }
  | { type: 'ANALYSIS_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }

// ─── Reducer ─────────────────────────────────────────────────────────────────

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_CODE':
      return { ...state, rawCode: action.payload }

    case 'SWITCH_TAB':
      return { ...state, activeTab: action.payload }

    case 'ANALYSIS_START':
      return { ...state, isLoading: true, error: null }

    case 'ANALYSIS_SUCCESS':
      return {
        ...state,
        isLoading: false,
        analysisResult: action.payload,
        activeTab: 'forest',
        error: null,
      }

    case 'ANALYSIS_ERROR':
      return { ...state, isLoading: false, error: action.payload }

    case 'CLEAR_ERROR':
      return { ...state, error: null }
  }
}

// ─── Context ──────────────────────────────────────────────────────────────────

interface AppContextValue {
  state: AppState
  dispatch: React.Dispatch<Action>
}

export const AppContext = createContext<AppContextValue | null>(null)

// ─── Provider ────────────────────────────────────────────────────────────────

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider = ({ children }: AppProviderProps) => {
  const [state, dispatch] = useReducer(appReducer, initialState)

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}

// ─── Hook ────────────────────────────────────────────────────────────────────

export const useAppContext = (): AppContextValue => {
  const context = useContext(AppContext)
  if (context === null) {
    throw new Error('useAppContext는 AppProvider 내부에서만 사용할 수 있습니다.')
  }
  return context
}
