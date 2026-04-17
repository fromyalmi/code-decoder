// 돋보기 뷰 — 핵심 개념 카드 목록 렌더링
import type { AnalysisResult, ConceptItem } from '../../types/index'

interface ConceptViewProps {
  result: AnalysisResult | null
}

const ConceptCard = ({ item }: { item: ConceptItem }) => (
  <div className="rounded-xl border border-outline-variant bg-surface p-4 flex flex-col gap-2">
    {/* 제목 */}
    <h3 className="font-headline font-semibold text-on-surface text-base">{item.term}</h3>

    {/* 설명 */}
    <p className="text-sm text-on-surface-variant leading-relaxed">{item.description}</p>

    {/* core_commands 태그 목록 */}
    {item.core_commands.length > 0 && (
      <div className="flex flex-wrap gap-1.5 pt-1">
        {item.core_commands.map((cmd) => (
          <span
            key={cmd}
            className="rounded-md bg-surface-container px-2 py-0.5 font-mono text-xs text-on-surface"
          >
            {cmd}
          </span>
        ))}
      </div>
    )}
  </div>
)

export const ConceptView = ({ result }: ConceptViewProps) => {
  if (result === null) {
    return (
      <p className="text-sm text-on-surface-variant">
        코드를 입력하고 분석하기를 눌러주세요.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {result.concept_view.map((item, index) => (
        <ConceptCard key={index} item={item} />
      ))}
    </div>
  )
}
