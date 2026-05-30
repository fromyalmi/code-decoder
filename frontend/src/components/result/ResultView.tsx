import { DashboardLayout } from '../DashboardLayout';
import { ForestPanel } from './ForestPanel';
import { TreePanel } from './TreePanel';

// 3-B-1 표면: 양쪽 응답 객체(Create/Detail) 모두 만족하는 최소 인터페이스.
// 3-B-2에서 line_explanations/deep_leaves 추가 예정, 3-B-2에서 tags 추가 예정.
export interface ResultViewAnalysis {
  forest: string;
  tree: string;
  key_concepts: ReadonlyArray<{
    name: string;
    definition: string;
    is_new?: boolean;
  }>;
}

interface ResultViewProps {
  analysis: ResultViewAnalysis;
}

export function ResultView({ analysis }: ResultViewProps) {
  return (
    <DashboardLayout
      pillar1={<ForestPanel forest={analysis.forest} />}
      pillar4={<TreePanel tree={analysis.tree} keyConcepts={analysis.key_concepts} />}
      pillar12={<EmptyPlaceholder label="12× 영역(3-B-2)" />}
    />
  );
}

function EmptyPlaceholder({ label }: { label: string }) {
  return <div style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-ui)' }}>{label}</div>;
}
