export const ERROR_MESSAGES: Record<string, string> = {
  INPUT_TOO_LARGE:      '🦜 코드가 좀 길어 — 더 작게 나눠 보내줄래?',
  DAILY_LIMIT_EXCEEDED: '🦜 오늘 분석은 다 썼어 — 내일 다시 만나자',
  LLM_FAILURE:          '🦜 잠시 길을 잃었어 — 한 번만 다시 시도해줄래?',
  NO_SESSION:           '🦜 다시 로그인이 필요해',
  NOT_FOUND:            '🦜 이 분석을 찾을 수 없어 — 삭제됐거나 주소가 잘못됐을 수 있어',
  UNKNOWN:              '🦜 잠시 문제가 생겼어 — 다시 시도해줄래?',
};

export function getErrorMessage(code: string): string {
  return ERROR_MESSAGES[code] ?? ERROR_MESSAGES.UNKNOWN;
}
