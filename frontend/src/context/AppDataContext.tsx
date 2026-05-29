import {
  createContext,
  useCallback,
  useEffect,
  useReducer,
  type ReactNode,
} from 'react';
import { ApiError, registerUnauthorizedHandler } from '../api/client';
import type { MeResponse, RewardPublic, TitleInfo, UserPublic } from '../api/manual-types';
import { useApi } from '../hooks/useApi';

// ── State ──────────────────────────────────────────────────────────────
interface AppDataState {
  user: UserPublic | null;
  reward: RewardPublic | null;
  titleInfo: TitleInfo | null;
  dailyUsed: number;
  dailyLimit: number;
  leafCounter: number;
  isBootstrapping: boolean;
  bootstrapError: ApiError | null;
}

// ── Actions ────────────────────────────────────────────────────────────
type AppAction =
  | { type: 'BOOTSTRAP_START' }
  | { type: 'BOOTSTRAP_SUCCESS'; payload: MeResponse }
  | { type: 'BOOTSTRAP_ERROR'; error: ApiError }
  | { type: 'RECORD_ANALYSIS_COMPLETED'; reward: RewardPublic; cacheHit: boolean }
  | { type: 'RECORD_LEAF_CHARGED' }
  | { type: 'RECORD_LEAF_INCREMENTED' }
  | { type: 'CLEAR_USER' };

const initialState: AppDataState = {
  user: null,
  reward: null,
  titleInfo: null,
  dailyUsed: 0,
  dailyLimit: 10,
  leafCounter: 0,
  isBootstrapping: true,
  bootstrapError: null,
};

function appDataReducer(state: AppDataState, action: AppAction): AppDataState {
  switch (action.type) {
    case 'BOOTSTRAP_START':
      return { ...state, isBootstrapping: true, bootstrapError: null };

    case 'BOOTSTRAP_SUCCESS': {
      const me = action.payload;
      const { daily_used, daily_limit, leaf_counter, reward, title, ...userFields } = me;
      return {
        ...state,
        user: userFields,
        reward,
        titleInfo: title,
        dailyUsed: daily_used,
        dailyLimit: daily_limit,
        leafCounter: leaf_counter,
        isBootstrapping: false,
        bootstrapError: null,
      };
    }

    case 'BOOTSTRAP_ERROR':
      return { ...state, isBootstrapping: false, bootstrapError: action.error };

    case 'RECORD_ANALYSIS_COMPLETED':
      return {
        ...state,
        dailyUsed: state.dailyUsed + 1,
        reward: action.reward,
      };

    case 'RECORD_LEAF_CHARGED':
      return {
        ...state,
        dailyUsed: state.dailyUsed + 1,
        leafCounter: 0,
      };

    case 'RECORD_LEAF_INCREMENTED':
      return { ...state, leafCounter: state.leafCounter + 1 };

    case 'CLEAR_USER':
      return { ...initialState, isBootstrapping: false };

    default:
      return state;
  }
}

// ── Context ────────────────────────────────────────────────────────────
interface AppDataActions {
  refreshMe: () => Promise<void>;
  recordAnalysisCompleted: (reward: RewardPublic, cacheHit: boolean) => void;
  recordLeafCharged: () => void;
  recordLeafIncremented: () => void;
  clearUser: () => void;
}

type AppDataContextValue = AppDataState & AppDataActions;

export const AppDataContext = createContext<AppDataContextValue | null>(null);

// ── Provider ───────────────────────────────────────────────────────────
export function AppDataProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appDataReducer, initialState);
  const apiFetch = useApi();

  const clearUser = useCallback(() => {
    dispatch({ type: 'CLEAR_USER' });
  }, []);

  const refreshMe = useCallback(async () => {
    dispatch({ type: 'BOOTSTRAP_START' });
    try {
      const me = await apiFetch<MeResponse>('GET', '/me');
      dispatch({ type: 'BOOTSTRAP_SUCCESS', payload: me });
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        dispatch({ type: 'CLEAR_USER' });
      } else {
        dispatch({ type: 'BOOTSTRAP_ERROR', error: e instanceof ApiError ? e : new ApiError('UNKNOWN', '부트스트랩 실패', 0) });
      }
    }
  }, [apiFetch]);

  useEffect(() => {
    registerUnauthorizedHandler(clearUser);
    refreshMe();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const recordAnalysisCompleted = useCallback((reward: RewardPublic, cacheHit: boolean) => {
    dispatch({ type: 'RECORD_ANALYSIS_COMPLETED', reward, cacheHit });
  }, []);

  const recordLeafCharged = useCallback(() => {
    dispatch({ type: 'RECORD_LEAF_CHARGED' });
  }, []);

  const recordLeafIncremented = useCallback(() => {
    dispatch({ type: 'RECORD_LEAF_INCREMENTED' });
  }, []);

  const value: AppDataContextValue = {
    ...state,
    refreshMe,
    recordAnalysisCompleted,
    recordLeafCharged,
    recordLeafIncremented,
    clearUser,
  };

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}
