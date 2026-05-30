import styles from './CodeInput.module.css';

interface CodeInputProps {
  value: string;
  onChange: (next: string) => void;
  onSubmit: () => void;
  errorMessage: string | null;
}

export function CodeInput({ value, onChange, onSubmit, errorMessage }: CodeInputProps) {
  const lineCount = Math.max(1, value.split('\n').length);
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1).join('\n');

  return (
    <div className={styles.wrapper}>
      <div className={styles.editor}>
        <pre className={styles.lineNumbers} aria-hidden="true">{lineNumbers}</pre>
        <textarea
          className={styles.textarea}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck={false}
        />
      </div>
      {errorMessage && <div className={styles.error}>{errorMessage}</div>}
      <button className={styles.submit} type="button" onClick={onSubmit}>분석</button>
    </div>
  );
}
