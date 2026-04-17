// 나무 뷰 — 라인별 코드 해설 타임라인 렌더링
import type { AnalysisResult, TreeItem } from '../../types/index'

interface TreeViewProps {
  result: AnalysisResult | null
}

const TreeCard = ({ item }: { item: TreeItem }) => (
  <div className="rounded-xl border border-outline-variant bg-surface p-3 flex flex-col gap-2">
    {/* 라인 범위 배지 + 코드 스니펫 */}
    <div className="flex items-start gap-2">
      <span className="mt-0.5 shrink-0 rounded-md bg-primary-fixed px-2 py-0.5 text-xs font-mono font-semibold text-primary">
        {item.line_range}
      </span>
      <code className="text-xs font-mono text-on-surface leading-relaxed whitespace-pre-wrap break-all">
        {item.code_snippet}
      </code>
    </div>

    {/* 해설 */}
    <p className="text-sm text-on-surface-variant leading-relaxed">{item.explanation}</p>
  </div>
)

export const TreeView = ({ result }: TreeViewProps) => {
  if (result === null) {
    return (
      <p className="text-sm text-on-surface-variant">
        코드를 입력하고 분석하기를 눌러주세요.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {result.tree_view.map((item, index) => (
        <TreeCard key={index} item={item} />
      ))}
    </div>
  )
}
