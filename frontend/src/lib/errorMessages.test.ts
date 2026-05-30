import { describe, it, expect } from 'vitest';
import { getErrorMessage } from './errorMessages';

describe('getErrorMessage', () => {
  it('INPUT_TOO_LARGE 코드는 입력 길이 안내 카피를 반환', () => {
    expect(getErrorMessage('INPUT_TOO_LARGE')).toBe('🦜 코드가 좀 길어 — 더 작게 나눠 보내줄래?');
  });

  it('DAILY_LIMIT_EXCEEDED 코드는 일일 한도 카피를 반환', () => {
    expect(getErrorMessage('DAILY_LIMIT_EXCEEDED')).toBe('🦜 오늘 분석은 다 썼어 — 내일 다시 만나자');
  });

  it('LLM_FAILURE 코드는 LLM 실패 카피를 반환', () => {
    expect(getErrorMessage('LLM_FAILURE')).toBe('🦜 잠시 길을 잃었어 — 한 번만 다시 시도해줄래?');
  });

  it('NO_SESSION 코드는 재로그인 카피를 반환', () => {
    expect(getErrorMessage('NO_SESSION')).toBe('🦜 다시 로그인이 필요해');
  });

  it('미지정 코드는 UNKNOWN fallback 카피를 반환', () => {
    expect(getErrorMessage('SOMETHING_WEIRD_THAT_DOES_NOT_EXIST')).toBe('🦜 잠시 문제가 생겼어 — 다시 시도해줄래?');
  });
});
