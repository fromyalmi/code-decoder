import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ApiError } from '../api/client';
import type { components } from '../api/types';
import { DashboardPage } from './DashboardPage';

// ── Mock 패턴: vi.hoisted로 mock 함수를 호이스트해서 vi.mock factory가 안전히 참조 ──
// vi.mock은 모듈 최상단으로 호이스트되므로, 일반 const는 mock factory 안에서 미정의 상태.
// vi.hoisted는 같은 시점에 호이스트되어 mock factory에서 참조 가능.
const { mockApiFetch, mockRefreshMe } = vi.hoisted(() => ({
  mockApiFetch: vi.fn(),
  mockRefreshMe: vi.fn(),
}));

vi.mock('../hooks/useApi', () => ({
  useApi: () => mockApiFetch,
}));

vi.mock('../hooks/useAppData', () => ({
  useAppData: () => ({
    refreshMe: mockRefreshMe,
    dailyUsed: 0,
    dailyLimit: 10,
    leafCounter: 0,
    reward: null,
    titleInfo: null,
  }),
}));

type AnalysisCreateResponse = components['schemas']['AnalysisCreateResponse'];

const fakeResponse: AnalysisCreateResponse = {
  id: 'a1',
  user_id: 'u1',
  code_original: 'def hi():\n    print("hello")',
  code_processed: 'def hi():\n    print("hello")',
  code_sha256: 'abc',
  language: 'python',
  line_count_original: 2,
  line_count_processed: 2,
  line_mapping: { '1': 1, '2': 2 },
  forest: '인사 출력',
  tree: '단일 호출',
  line_explanations: [
    { line_no: 1, short: '함수 선언' },
    { line_no: 2, short: '문자열 출력' },
  ],
  deep_leaves: [
    { line_no: 1, deep: 'def 키워드로 함수 정의...' },
  ],
  tags: ['python', 'function'],
  key_concepts: [
    { name: '함수', definition: '코드 묶음에 이름을 붙여 재사용하는 도구', is_new: true },
  ],
  created_at: '2026-05-30T00:00:00Z',
  daily_used: 1,
  leaf_counter: 0,
  is_favorite: false,
  memo: null,
  cache_hit: false,
};

beforeEach(() => {
  mockApiFetch.mockReset();
  mockRefreshMe.mockReset();
});

describe('DashboardPage', () => {
  it('초기 phase는 idle — CodeInput textarea가 보이고 스켈레톤은 없다', () => {
    render(<DashboardPage />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('분석 성공: POST body 검증 + idle→analyzing→showing + refreshMe 1회', async () => {
    let resolveFetch!: (v: AnalysisCreateResponse) => void;
    mockApiFetch.mockReturnValueOnce(
      new Promise<AnalysisCreateResponse>((resolve) => {
        resolveFetch = resolve;
      })
    );

    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.type(screen.getByRole('textbox'), 'print("hi")');
    await user.click(screen.getByRole('button', { name: '분석' }));

    // analyzing 단계: LoadingSkeleton(role=status) 표시, CodeInput 언마운트
    await waitFor(() => {
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();

    // POST body 검증
    expect(mockApiFetch).toHaveBeenCalledTimes(1);
    expect(mockApiFetch).toHaveBeenCalledWith('POST', '/analyses', {
      body: { code: 'print("hi")', language: 'python' },
    });

    // 응답 해결 → showing
    resolveFetch(fakeResponse);
    // ResultView 도입(3-B-1): forest 텍스트가 ForestPanel에 렌더된 직접 증거
    await waitFor(() => {
      expect(screen.getByText('인사 출력')).toBeInTheDocument();
    });
    // key_concepts 카드가 TreePanel에 렌더되는지 추가 검증
    expect(screen.getByText('함수')).toBeInTheDocument();
    expect(screen.getByText('코드 묶음에 이름을 붙여 재사용하는 도구')).toBeInTheDocument();

    // LeafColumn(3-B-2): 라인 1 (tier='deep_core' — short + deep 모두 표시)
    expect(screen.getByText('def hi():')).toBeInTheDocument();
    expect(screen.getByText('함수 선언')).toBeInTheDocument();
    expect(screen.getByText('def 키워드로 함수 정의...')).toBeInTheDocument();
    // LeafColumn(3-B-2): 라인 2 (tier='short' — short만)
    expect(screen.getByText('print("hello")')).toBeInTheDocument();
    expect(screen.getByText('문자열 출력')).toBeInTheDocument();
    // FolderTree(3-B-2): 태그 칩
    expect(screen.getByText('python')).toBeInTheDocument();
    expect(screen.getByText('function')).toBeInTheDocument();

    // refreshMe 1회
    expect(mockRefreshMe).toHaveBeenCalledTimes(1);
  });

  it('DAILY_LIMIT_EXCEEDED: idle 복귀 + 한도 카피 인라인 표시 + refreshMe 호출 X', async () => {
    mockApiFetch.mockRejectedValueOnce(
      new ApiError('DAILY_LIMIT_EXCEEDED', '서버 메시지 무시', 429)
    );
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.type(screen.getByRole('textbox'), 'print("hi")');
    await user.click(screen.getByRole('button', { name: '분석' }));

    await waitFor(() => {
      expect(
        screen.getByText('🦜 오늘 분석은 다 썼어 — 내일 다시 만나자')
      ).toBeInTheDocument();
    });

    // idle 복귀
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();

    // refreshMe 호출 안 됨
    expect(mockRefreshMe).not.toHaveBeenCalled();
  });

  it('알 수 없는 코드(ApiError): UNKNOWN fallback 카피 표시', async () => {
    mockApiFetch.mockRejectedValueOnce(
      new ApiError('SOMETHING_WEIRD', 'msg', 500)
    );
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.type(screen.getByRole('textbox'), 'print("hi")');
    await user.click(screen.getByRole('button', { name: '분석' }));

    await waitFor(() => {
      expect(
        screen.getByText('🦜 잠시 문제가 생겼어 — 다시 시도해줄래?')
      ).toBeInTheDocument();
    });
  });
});
