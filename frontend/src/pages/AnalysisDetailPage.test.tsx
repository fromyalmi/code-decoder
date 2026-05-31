import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ApiError } from '../api/client';
import type { components } from '../api/types';
import { AnalysisDetailPage } from './AnalysisDetailPage';

// ── Mock 패턴 (기존 본 유지: vi.hoisted + vi.mock) ─────────────────────
const { mockApiFetch } = vi.hoisted(() => ({ mockApiFetch: vi.fn() }));

vi.mock('../hooks/useApi', () => ({
  useApi: () => mockApiFetch,
}));

vi.mock('../hooks/useAppData', () => ({
  useAppData: () => ({
    refreshMe: vi.fn(),
    dailyUsed: 0,
    dailyLimit: 10,
    leafCounter: 0,
    reward: null,
    titleInfo: null,
  }),
}));

type AnalysisDetailResponse = components['schemas']['AnalysisDetailResponse'];

// ── fakeDetailResponse: DashboardPage 케이스 2와 동일 값(출처 무지 실증용) ──
// Create 응답 vs Detail 응답이라도 ResultView가 같은 표면(ResultViewAnalysis)으로
// 흡수 → 동일 단언 통과 = 출처 무지 원칙 실증
const fakeDetailResponse: AnalysisDetailResponse = {
  id: 'a1',
  user_id: 'u1',
  created_at: '2026-05-30T00:00:00Z',
  language: 'python',
  code_original: 'def hi():\n    print("hello")',
  code_processed: 'def hi():\n    print("hello")',
  forest: '인사 출력',
  tree: '단일 호출',
  tags: ['python', 'function'],
  memo: null,
  is_favorite: false,
  line_explanations: [
    { line_no: 1, short: '함수 선언' },
    { line_no: 2, short: '문자열 출력' },
  ],
  deep_leaves: [
    { line_no: 1, deep: 'def 키워드로 함수 정의...' },
  ],
  key_concepts: [
    // ★ KeyConceptDetailItem은 is_new 없음 — Detail 응답 정확 표현
    { name: '함수', definition: '코드 묶음에 이름을 붙여 재사용하는 도구' },
  ],
};

// ── 라우팅 테스트 셋업 (★ 이 프로젝트 첫 라우팅 테스트 — 이후 페이지 라우팅 본) ──
// useParams 직접 mock 대신 MemoryRouter + Routes로 실제 라우팅.
// 라우터가 :uuid를 실제로 넘기는지까지 검증됨.
function renderAtRoute(uuid: string) {
  return render(
    <MemoryRouter initialEntries={[`/analysis/${uuid}`]}>
      <Routes>
        <Route path="/analysis/:uuid" element={<AnalysisDetailPage />} />
      </Routes>
    </MemoryRouter>
  );
}

beforeEach(() => {
  mockApiFetch.mockReset();
});

describe('AnalysisDetailPage', () => {
  it('마운트 시 GET /analyses/:uuid 1회 호출 — uuid가 URL에서 정확히 추출', async () => {
    mockApiFetch.mockResolvedValueOnce(fakeDetailResponse);
    renderAtRoute('abc-123');
    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith('GET', '/analyses/abc-123');
    });
    expect(mockApiFetch).toHaveBeenCalledTimes(1);
  });

  it('로딩→성공: LoadingSkeleton 표시 후 ResultView로 전환', async () => {
    let resolveFetch!: (v: AnalysisDetailResponse) => void;
    mockApiFetch.mockReturnValueOnce(
      new Promise<AnalysisDetailResponse>((resolve) => {
        resolveFetch = resolve;
      })
    );
    renderAtRoute('abc-123');

    // 마운트 직후 로딩
    await waitFor(() => {
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    // 응답 해결 → ResultView 전환
    resolveFetch(fakeDetailResponse);
    await waitFor(() => {
      expect(screen.getByText('인사 출력')).toBeInTheDocument();
    });
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('출처 무지 실증: DashboardPage 케이스 2와 동일 11단언이 Detail에서도 통과', async () => {
    mockApiFetch.mockResolvedValueOnce(fakeDetailResponse);
    renderAtRoute('abc-123');

    await waitFor(() => {
      expect(screen.getByText('인사 출력')).toBeInTheDocument();
    });
    // ForestPanel
    expect(screen.getByText('인사 출력')).toBeInTheDocument();
    // TreePanel 카드
    expect(screen.getByText('함수')).toBeInTheDocument();
    expect(screen.getByText('코드 묶음에 이름을 붙여 재사용하는 도구')).toBeInTheDocument();
    // LeafColumn + CodeBlock (정규식 length 2 — substring 매칭)
    expect(screen.getAllByText(/def hi\(\):/)).toHaveLength(2);
    expect(screen.getAllByText(/print\("hello"\)/)).toHaveLength(2);
    // LeafLine deep_core (라인 1)
    expect(screen.getByText('함수 선언')).toBeInTheDocument();
    expect(screen.getByText('def 키워드로 함수 정의...')).toBeInTheDocument();
    // LeafLine short (라인 2)
    expect(screen.getByText('문자열 출력')).toBeInTheDocument();
    // FolderTree
    expect(screen.getByText('python')).toBeInTheDocument();
    expect(screen.getByText('function')).toBeInTheDocument();
  });

  it('NOT_FOUND 에러: 신규 카피 인라인 표시 + 로딩 사라짐', async () => {
    mockApiFetch.mockRejectedValueOnce(
      new ApiError('NOT_FOUND', '서버 메시지 무시', 404)
    );
    renderAtRoute('not-exist-uuid');

    await waitFor(() => {
      expect(
        screen.getByText('🦜 이 분석을 찾을 수 없어 — 삭제됐거나 주소가 잘못됐을 수 있어')
      ).toBeInTheDocument();
    });
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });
});
