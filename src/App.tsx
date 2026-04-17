// 앱 루트 — AppProvider로 전체 감싸고 레이아웃 렌더링
import { AppProvider, useAppContext } from './context/AppContext'
import { useAnalyzer } from './hooks/useAnalyzer'
import type { TabType } from './types/index'
import { ForestView } from './components/views/ForestView'
import { TreeView } from './components/views/TreeView'
import { ConceptView } from './components/views/ConceptView'

// ─── 탭 설정 ──────────────────────────────────────────────────────────────────

const TABS: { id: TabType; label: string }[] = [
  { id: 'forest',   label: '🌲 숲' },
  { id: 'tree',     label: '🌿 나무' },
  { id: 'concept',  label: '🔍 돋보기' },
  { id: 'myCards',  label: '📚 도감' },
  { id: 'history',  label: '🕒 히스토리' },
]

// ─── 탭 컨텐츠 ───────────────────────────────────────────────────────────────

import type { AnalysisResult } from './types/index'

const TabContent = ({
  tab,
  result,
}: {
  tab: TabType
  result: AnalysisResult | null
}) => {
  switch (tab) {
    case 'forest':
      return <ForestView result={result} />
    case 'tree':
      return <TreeView result={result} />
    case 'concept':
      return <ConceptView result={result} />
    case 'myCards':
      return <p className="text-on-surface-variant text-sm">myCards 준비 중</p>
    case 'history':
      return <p className="text-on-surface-variant text-sm">history 준비 중</p>
  }
}

// ─── 내부 레이아웃 (Context 접근 필요) ───────────────────────────────────────

const AppLayout = () => {
  const { state, dispatch } = useAppContext()

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    dispatch({ type: 'SET_CODE', payload: e.target.value })
  }

  const { analyze } = useAnalyzer()

  const handleSwitchTab = (tab: TabType) => {
    dispatch({ type: 'SWITCH_TAB', payload: tab })
  }

  return (
    <div className="min-h-screen bg-surface font-body">
      {/* Header */}
      <header className="fixed top-0 inset-x-0 h-16 bg-primary flex items-center px-6 z-10">
        <h1 className="text-on-primary font-headline text-xl font-bold tracking-tight">
          Code Decoder
        </h1>
      </header>

      {/* Main */}
      <main className="pt-16 flex flex-col gap-4 p-4 max-w-3xl mx-auto">
        {/* 코드 입력 패널 */}
        <section className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm">
          <label
            htmlFor="code-input"
            className="block text-sm font-medium text-on-surface mb-2"
          >
            코드 입력
          </label>
          <textarea
            id="code-input"
            value={state.rawCode}
            onChange={handleCodeChange}
            placeholder="분석할 코드를 여기에 붙여넣으세요..."
            rows={10}
            className="w-full resize-y rounded-xl border border-outline-variant bg-surface p-3 text-sm text-on-surface font-mono focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            onClick={analyze}
            disabled={state.isLoading || state.rawCode.trim() === ''}
            className="mt-3 w-full rounded-xl bg-primary py-2.5 text-sm font-semibold text-on-primary transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            {state.isLoading ? '분석 중...' : '분석하기'}
          </button>
          {state.error && (
            <p className="mt-2 text-sm text-error">{state.error}</p>
          )}
        </section>

        {/* 탭 네비게이션 */}
        <div className="bg-surface-container-high rounded-full p-1.5 flex gap-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleSwitchTab(tab.id)}
              className={[
                'flex-1 rounded-full py-1.5 text-xs font-medium transition-all',
                state.activeTab === tab.id
                  ? 'bg-surface-container-lowest text-primary shadow-sm'
                  : 'text-on-surface-variant hover:bg-white/50',
              ].join(' ')}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* 탭 컨텐츠 */}
        <section className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm min-h-32">
          <TabContent tab={state.activeTab} result={state.analysisResult} />
        </section>
      </main>
    </div>
  )
}

// ─── 루트 컴포넌트 ────────────────────────────────────────────────────────────

export const App = () => (
  <AppProvider>
    <AppLayout />
  </AppProvider>
)

export default App
