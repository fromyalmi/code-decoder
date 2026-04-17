// OpenAI API 호출 오케스트레이션 — 분석 요청, 로딩 상태, 에러 처리
import { useAppContext } from '../context/AppContext'
import { analyzeCode } from '../services/openaiService'

export const useAnalyzer = () => {
  const { state, dispatch } = useAppContext()

  const analyze = async () => {
    if (state.rawCode.trim() === '') return

    dispatch({ type: 'ANALYSIS_START' })
    try {
      const result = await analyzeCode(state.rawCode)
      dispatch({ type: 'ANALYSIS_SUCCESS', payload: result })
    } catch (err) {
      const message = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
      dispatch({ type: 'ANALYSIS_ERROR', payload: message })
    }
  }

  return { analyze }
}
