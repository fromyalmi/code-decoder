import styles from './LeafLine.module.css';

interface LeafLineProps {
  lineNo: number;
  codeLine: string;
  tier: 'short' | 'deep_core';
  shortText: string;
  deepText: string | null;
}

export function LeafLine({ lineNo, codeLine, tier, shortText, deepText }: LeafLineProps) {
  return (
    <li className={styles.line}>
      <div className={styles.codeRow}>
        <span className={styles.lineNo}>{lineNo}</span>
        <code className={styles.code}>{codeLine}</code>
      </div>
      <p className={styles.short}>{shortText}</p>
      {tier === 'deep_core' && deepText && (
        <p className={styles.deep}>{deepText}</p>
      )}
    </li>
  );
}
