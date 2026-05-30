import { LeafLine } from './LeafLine';
import styles from './LeafColumn.module.css';

interface LeafColumnProps {
  codeOriginal: string;
  lineExplanations: ReadonlyArray<{ line_no: number; short: string }>;
  deepLeaves: ReadonlyArray<{ line_no: number; deep: string }>;
}

export function LeafColumn({ codeOriginal, lineExplanations, deepLeaves }: LeafColumnProps) {
  const items = deriveLeafItems(lineExplanations, deepLeaves, codeOriginal);
  return (
    <ul className={styles.column}>
      {items.map(item => (
        <LeafLine key={item.lineNo} {...item} />
      ))}
    </ul>
  );
}

// line_explanations 기준 순회로 'short ∄, deep ∃' 비정상 케이스 자동 제외.
// codeLines[lineNo-1] ?? '' 가드로 line_no 범위밖 안전망(LLM이 잘못된 번호 줘도 빈 문자열).
// LLM은 백엔드 프롬프트로 original line_no를 사용하도록 강제됨(line_mapping 불필요).
function deriveLeafItems(
  lineExplanations: ReadonlyArray<{ line_no: number; short: string }>,
  deepLeaves: ReadonlyArray<{ line_no: number; deep: string }>,
  codeOriginal: string,
) {
  const deepByLine = new Map(deepLeaves.map(dl => [dl.line_no, dl.deep]));
  const codeLines = codeOriginal.split('\n');
  return lineExplanations.map(le => {
    const deepText = deepByLine.get(le.line_no) ?? null;
    return {
      lineNo: le.line_no,
      codeLine: codeLines[le.line_no - 1] ?? '',
      shortText: le.short,
      deepText,
      tier: (deepText ? 'deep_core' : 'short') as 'deep_core' | 'short',
    };
  });
}
