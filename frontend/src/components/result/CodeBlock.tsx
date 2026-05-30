import styles from './CodeBlock.module.css';

interface CodeBlockProps {
  code: string;
}

export function CodeBlock({ code }: CodeBlockProps) {
  if (!code.trim()) return null;
  return <pre className={styles.block}><code>{code}</code></pre>;
}
