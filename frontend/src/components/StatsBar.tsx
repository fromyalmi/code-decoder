import { useAppData } from '../hooks/useAppData';
import styles from './StatsBar.module.css';

export function StatsBar() {
  const { dailyUsed, dailyLimit, leafCounter, reward, titleInfo } = useAppData();
  return (
    <div className={styles.bar}>
      <Cell label="오늘 분석" value={`${dailyUsed}/${dailyLimit}`} />
      <Cell label="잎" value={leafCounter} />
      <Cell label="🐛" value={reward?.caterpillar_balance ?? 0} />
      <Cell label={titleInfo?.emoji ?? ''} value={titleInfo?.label ?? ''} />
    </div>
  );
}

function Cell({ label, value }: { label: string; value: string | number }) {
  return (
    <div className={styles.cell}>
      <span className={styles.label}>{label}</span>
      <span className={styles.value}>{value}</span>
    </div>
  );
}
