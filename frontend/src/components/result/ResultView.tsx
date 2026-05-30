import { DashboardLayout } from '../DashboardLayout';
import { FolderTree } from './FolderTree';
import { ForestPanel } from './ForestPanel';
import { LeafColumn } from './LeafColumn';
import { TreePanel } from './TreePanel';

// Create·Detail 응답 양쪽 만족하는 최소 표면. 3-B-2에서
// code_original/line_explanations/deep_leaves/tags 추가(LeafColumn·FolderTree용).
export interface ResultViewAnalysis {
  forest: string;
  tree: string;
  key_concepts: ReadonlyArray<{
    name: string;
    definition: string;
    is_new?: boolean;
  }>;
  code_original: string;
  line_explanations: ReadonlyArray<{ line_no: number; short: string }>;
  deep_leaves: ReadonlyArray<{ line_no: number; deep: string }>;
  tags: ReadonlyArray<string>;
}

interface ResultViewProps {
  analysis: ResultViewAnalysis;
}

export function ResultView({ analysis }: ResultViewProps) {
  return (
    <DashboardLayout
      pillar1={
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <ForestPanel forest={analysis.forest} />
          <FolderTree tags={analysis.tags} />
        </div>
      }
      pillar4={<TreePanel tree={analysis.tree} keyConcepts={analysis.key_concepts} />}
      pillar12={
        <LeafColumn
          codeOriginal={analysis.code_original}
          lineExplanations={analysis.line_explanations}
          deepLeaves={analysis.deep_leaves}
        />
      }
    />
  );
}
