import { useCallback } from 'react';
import { ApiError, handleUnauthorized } from '../api/client';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

type ApiFetchFn = <TResponse>(
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
  path: string,
  options?: {
    body?: unknown;
    query?: Record<string, string | number | boolean>;
    signal?: AbortSignal;
  }
) => Promise<TResponse>;

export function useApi(): ApiFetchFn {
  return useCallback(async <TResponse>(
    method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
    path: string,
    options?: {
      body?: unknown;
      query?: Record<string, string | number | boolean>;
      signal?: AbortSignal;
    }
  ): Promise<TResponse> => {
    let url = `${BASE_URL}/api/v1${path}`;

    if (options?.query) {
      const params = new URLSearchParams();
      for (const [k, v] of Object.entries(options.query)) {
        params.set(k, String(v));
      }
      url = `${url}?${params.toString()}`;
    }

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: options?.body !== undefined ? JSON.stringify(options.body) : undefined,
      signal: options?.signal,
    });

    if (response.status === 401) {
      handleUnauthorized();
      throw new ApiError('NO_SESSION', '🦜 다시 로그인이 필요해', 401);
    }

    const text = await response.text();

    if (response.ok) {
      return (text ? JSON.parse(text) : null) as TResponse;
    }

    try {
      const envelope = JSON.parse(text) as { error: { code: string; message: string } };
      throw new ApiError(envelope.error.code, envelope.error.message, response.status);
    } catch (e) {
      if (e instanceof ApiError) throw e;
      throw new ApiError('UNKNOWN', '🦜 잠시 문제가 생겼어 — 다시 시도해줄래?', response.status);
    }
  }, []);
}
