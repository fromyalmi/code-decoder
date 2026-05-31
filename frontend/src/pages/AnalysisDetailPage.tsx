import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ApiError } from '../api/client';
import type { components } from '../api/types';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { ResultView } from '../components/result/ResultView';
import { StatsBar } from '../components/StatsBar';
import { useApi } from '../hooks/useApi';
import { getErrorMessage } from '../lib/errorMessages';

type AnalysisDetailResponse = components['schemas']['AnalysisDetailResponse'];

export function AnalysisDetailPage() {
  const apiFetch = useApi();
  const { uuid } = useParams<{ uuid: string }>();
  const [analysis, setAnalysis] = useState<AnalysisDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!uuid) return;
    setIsLoading(true);
    setErrorMessage(null);
    apiFetch<AnalysisDetailResponse>('GET', `/analyses/${uuid}`)
      .then(res => {
        setAnalysis(res);
        setIsLoading(false);
      })
      .catch(e => {
        const code = e instanceof ApiError ? e.code : 'UNKNOWN';
        setErrorMessage(getErrorMessage(code));
        setIsLoading(false);
      });
  }, [uuid, apiFetch]);

  return (
    <div style={{ padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <StatsBar />
      {isLoading ? (
        <LoadingSkeleton />
      ) : errorMessage ? (
        <div style={{ color: 'var(--color-orange)', fontFamily: 'var(--font-ui)' }}>{errorMessage}</div>
      ) : analysis ? (
        <ResultView analysis={analysis} />
      ) : null}
    </div>
  );
}
