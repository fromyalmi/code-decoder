import type { ReactNode } from 'react';
import styles from './DashboardLayout.module.css';

interface DashboardLayoutProps {
  pillar1: ReactNode;
  pillar4: ReactNode;
  pillar12: ReactNode;
}

export function DashboardLayout({ pillar1, pillar4, pillar12 }: DashboardLayoutProps) {
  return (
    <div className={styles.grid}>
      <section className={styles.pillar}>
        <header className={styles.header}>1×</header>
        {pillar1}
      </section>
      <section className={styles.pillar}>
        <header className={styles.header}>4×</header>
        {pillar4}
      </section>
      <section className={styles.pillar}>
        <header className={styles.header}>12×</header>
        {pillar12}
      </section>
    </div>
  );
}
