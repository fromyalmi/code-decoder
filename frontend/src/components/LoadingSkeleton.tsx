import styles from './LoadingSkeleton.module.css';

export function LoadingSkeleton() {
  return (
    <div className={styles.skeleton} role="status" aria-label="분석 중">
      <div className={styles.box} />
      <div className={styles.box} />
      <div className={styles.box} />
    </div>
  );
}
