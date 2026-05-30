import styles from './ForestPanel.module.css';

interface ForestPanelProps {
  forest: string;
}

export function ForestPanel({ forest }: ForestPanelProps) {
  return <div className={styles.panel}>{forest}</div>;
}
