// 숲 뷰 — 코드 전체 목적 요약 렌더링
import type { AnalysisResult } from '../../types/index'

interface ForestViewProps {
  result: AnalysisResult | null
}

const COMPLEXITY_STYLE: Record<AnalysisResult['complexity'], string> = {
  beginner:     'bg-green-100 text-green-700',
  intermediate: 'bg-yellow-100 text-yellow-700',
  advanced:     'bg-red-100 text-red-700',
}

const COMPLEXITY_LABEL: Record<AnalysisResult['complexity'], string> = {
  beginner:     '초급',
  intermediate: '중급',
  advanced:     '고급',
}

export const ForestView = ({ result }: ForestViewProps) => {
  if (result === null) {
    return (
      <p className="text-sm text-on-surface-variant">
        코드를 입력하고 분석하기를 눌러주세요.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {/* 언어 + 복잡도 */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-on-surface">{result.language}</span>
        <span
          className={[
            'rounded-full px-2.5 py-0.5 text-xs font-semibold',
            COMPLEXITY_STYLE[result.complexity],
          ].join(' ')}
        >
          {COMPLEXITY_LABEL[result.complexity]}
        </span>
      </div>

      {/* 전체 목적 요약 */}
      <p className="text-sm leading-relaxed text-on-surface">{result.forest_view}</p>
    </div>
  )
}
