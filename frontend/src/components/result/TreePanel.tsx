import styles from './TreePanel.module.css';

interface KeyConceptItem {
  name: string;
  definition: string;
  is_new?: boolean;
}

interface TreePanelProps {
  tree: string;
  keyConcepts: ReadonlyArray<KeyConceptItem>;
}

export function TreePanel({ tree, keyConcepts }: TreePanelProps) {
  return (
    <div className={styles.panel}>
      <div className={styles.treeText}>{tree}</div>
      <ul className={styles.cards}>
        {keyConcepts.map((kc, i) => (
          <li key={i} className={styles.card}>
            <header className={styles.cardHeader}>
              <span className={styles.cardName}>{kc.name}</span>
              {kc.is_new && <span className={styles.newBadge}>NEW</span>}
            </header>
            <p className={styles.cardBody}>{kc.definition}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
