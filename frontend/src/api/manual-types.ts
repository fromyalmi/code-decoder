// Hand-written response types — backend does not yet expose response_model in OpenAPI.
// These must stay in sync with backend/app/routers/users.py _user_response
// and backend/app/services/analysis_service.py.

export interface TitleInfo {
  stage: number;
  emoji: string;
  label: string;
  next_threshold: number | null;
}

export interface RewardPublic {
  caterpillar_balance: number;
  caterpillar_total_earned: number;
  caterpillar_total_spent: number;
  shield_count: number;
  shield_used_total: number;
  streak_current: number;
  streak_max: number;
  streak_last_date: string | null;
  analysis_count_total: number;
}

export interface UserPublic {
  id: string;
  email: string;
  nickname: string;
  level: number;
  level_auto: boolean;
  first_login_completed_at: string | null;
  sound_enabled: boolean;
}

// Flat response from GET /api/v1/me (backend returns a single dict, not nested)
export interface MeResponse extends UserPublic {
  daily_used: number;
  daily_limit: number;
  daily_remaining: number;
  leaf_counter: number;
  reward: RewardPublic;
  title: TitleInfo;
}
