export class ApiError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

let _onUnauthorized: (() => void) | null = null;

export function registerUnauthorizedHandler(fn: () => void): void {
  _onUnauthorized = fn;
}

export function handleUnauthorized(): void {
  _onUnauthorized?.();
  if (window.location.pathname !== '/login') {
    window.location.assign('/login');
  }
}
