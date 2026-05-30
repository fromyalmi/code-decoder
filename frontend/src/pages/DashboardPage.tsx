import { useState } from 'react';
import { ApiError } from '../api/client';
import type { components } from '../api/types';
import { CodeInput } from '../components/CodeInput';
import { DashboardLayout } from '../components/DashboardLayout';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { StatsBar } from '../components/StatsBar';
import { useApi } from '../hooks/useApi';
import { useAppData } from '../hooks/useAppData';
import { getErrorMessage } from '../lib/errorMessages';

type Phase = 'idle' | 'analyzing' | 'showing';
type AnalysisCreateResponse = components['schemas']['AnalysisCreateResponse'];

export function DashboardPage() {
  const apiFetch = useApi();
  const { refreshMe } = useAppData();
  const [phase, setPhase] = useState<Phase>('idle');
  const [inputCode, setInputCode] = useState('');
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisCreateResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit() {
    if (!inputCode.trim() || phase === 'analyzing') return;
    setErrorMessage(null);
    setPhase('analyzing');
    try {
      const res = await apiFetch<AnalysisCreateResponse>(
        'POST',
        '/analyses',
        // 3-A: python 고정(백엔드 Literal["python"]뿐). 언어 선택 UI는 후속 세션.
        { body: { code: inputCode, language: 'python' } }
      );
      setCurrentAnalysis(res);
      setPhase('showing');
      void refreshMe();
    } catch (e) {
      const code = e instanceof ApiError ? e.code : 'UNKNOWN';
      setErrorMessage(getErrorMessage(code));
      setPhase('idle');
    }
  }

  // 같은 자리(pillar1) 진화: idle→analyzing→showing
  // 3-A 임시: 결과 전체를 pillar1에 JSON 덤프.
  // 3-B에서 Forest/Tree/Leaf 세 기둥으로 분산 예정(ResultView 도입).
  const pillar1Content =
    phase === 'analyzing' ? <LoadingSkeleton /> :
    phase === 'showing' && currentAnalysis ? (
      <pre style={{ fontFamily: 'var(--font-code)', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
        {JSON.stringify(currentAnalysis, null, 2)}
      </pre>
    ) : (
      <CodeInput
        value={inputCode}
        onChange={setInputCode}
        onSubmit={handleSubmit}
        errorMessage={errorMessage}
      />
    );

  return (
    <div style={{ padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <StatsBar />
      <DashboardLayout
        pillar1={pillar1Content}
        pillar4={<EmptyPlaceholder label="4× 영역(3-B)" />}
        pillar12={<EmptyPlaceholder label="12× 영역(3-C)" />}
      />
    </div>
  );
}

// EmptyPlaceholder: DashboardPage 내부 인라인 소형 컴포넌트(별도 파일 X — 한 입 크기 유지)
function EmptyPlaceholder({ label }: { label: string }) {
  return <div style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-ui)' }}>{label}</div>;
}
