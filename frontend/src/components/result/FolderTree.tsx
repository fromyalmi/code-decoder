import styles from './FolderTree.module.css';

interface FolderTreeProps {
  tags: ReadonlyArray<string>;
}

export function FolderTree({ tags }: FolderTreeProps) {
  if (tags.length === 0) return null;
  return (
    <ul className={styles.chips}>
      {tags.map((tag, i) => (
        <li key={i} className={styles.chip}>{tag}</li>
      ))}
    </ul>
  );
}
