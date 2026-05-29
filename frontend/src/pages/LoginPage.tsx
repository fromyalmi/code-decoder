import { useState, useContext } from 'react';
import type { CSSProperties, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { AppDataContext } from '../context/AppDataContext';
import { ApiError } from '../api/client';
import type { components } from '../api/types';

type LoginRequest = components['schemas']['LoginRequest'];
type SignupRequest = components['schemas']['SignupRequest'];
type Tab = 'login' | 'signup';

// ── Styles ──────────────────────────────────────────────────────────────

const inputBase: CSSProperties = {
  padding: '10px 12px',
  backgroundColor: 'var(--n10)',
  border: '2px solid var(--n40)',
  color: 'var(--text-primary)',
  fontFamily: 'var(--font-ui)',
  fontSize: '14px',
  outline: 'none',
  width: '100%',
  boxSizing: 'border-box',
};

const hint: CSSProperties = {
  margin: '4px 0 0',
  fontSize: '12px',
  color: 'var(--text-label)',
};

/* TODO: 에러색 #E85555 토큰화 — §12.10, 별도 세션 */
const errorText: CSSProperties = {
  margin: 0,
  fontSize: '13px',
  color: 'var(--color-orange)',
};

const cbLabel: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  fontSize: '13px',
  color: 'var(--text-label)',
  cursor: 'pointer',
};

const submitBtn = (enabled: boolean): CSSProperties => ({
  padding: '12px',
  width: '100%',
  backgroundColor: enabled ? 'var(--color-yellow)' : 'var(--n40)',
  color: enabled ? 'var(--n10)' : 'var(--text-dim)',
  border: 'none',
  fontFamily: 'var(--font-ui)',
  fontSize: '14px',
  fontWeight: 600,
  cursor: enabled ? 'pointer' : 'not-allowed',
});

// ── PasswordInput ───────────────────────────────────────────────────────

function PasswordInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  const [show, setShow] = useState(false);
  return (
    <div style={{ display: 'flex' }}>
      <input
        type={show ? 'text' : 'password'}
        value={value}
        placeholder="비밀번호"
        onChange={e => onChange(e.target.value)}
        style={{ ...inputBase, flex: 1, width: 'auto', borderRight: 'none' }}
      />
      <button
        type="button"
        onClick={() => setShow(s => !s)}
        style={{
          padding: '10px 12px',
          backgroundColor: 'var(--n10)',
          border: '2px solid var(--n40)',
          color: 'var(--text-label)',
          fontFamily: 'var(--font-ui)',
          fontSize: '12px',
          cursor: 'pointer',
          whiteSpace: 'nowrap',
        }}
      >
        {show ? '🙈 가리기' : '👁 보기'}
      </button>
    </div>
  );
}

// ── LoginForm ───────────────────────────────────────────────────────────

function LoginForm({ onInteract }: { onInteract: () => void }) {
  const apiFetch = useApi();
  const { refreshMe } = useContext(AppDataContext)!;
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = email.trim() !== '' && password.trim() !== '' && !loading;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    try {
      const body: LoginRequest = { email, password };
      await apiFetch<unknown>('POST', '/auth/login', { body });
      await refreshMe();
      navigate('/');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '잠시 문제가 생겼어 — 다시 시도해줄래?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '24px' }}
    >
      <input
        type="email"
        value={email}
        placeholder="이메일"
        onChange={e => { setEmail(e.target.value); onInteract(); }}
        style={inputBase}
      />
      <PasswordInput value={password} onChange={v => { setPassword(v); onInteract(); }} />
      {error && <p style={errorText}>{error}</p>}
      <button type="submit" disabled={!canSubmit} style={submitBtn(canSubmit)}>
        {loading ? '로그인 중…' : '로그인'}
      </button>
    </form>
  );
}

// ── SignupForm ──────────────────────────────────────────────────────────

function SignupForm({ onSuccess }: { onSuccess: () => void }) {
  const apiFetch = useApi();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nickname, setNickname] = useState('');
  const [terms, setTerms] = useState(false);
  const [privacy, setPrivacy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit =
    email.trim() !== '' && password.trim() !== '' && nickname.trim() !== '' &&
    terms && privacy && !loading;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    try {
      const body: SignupRequest = {
        email, password, nickname, agreed_terms: terms, agreed_privacy: privacy,
      };
      await apiFetch<unknown>('POST', '/auth/signup', { body });
      onSuccess();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '잠시 문제가 생겼어 — 다시 시도해줄래?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '24px' }}
    >
      <div>
        <input
          type="email" value={email} placeholder="이메일"
          onChange={e => setEmail(e.target.value)} style={inputBase}
        />
        <p style={hint}>로그인할 때 쓸 이메일이야 📧</p>
      </div>
      <div>
        <PasswordInput value={password} onChange={setPassword} />
        <p style={hint}>8자 이상이면 충분해 🔑 (숫자·특수기호는 안 넣어도 돼)</p>
      </div>
      <div>
        <input
          type="text" value={nickname} placeholder="닉네임"
          onChange={e => setNickname(e.target.value)} style={inputBase}
        />
        <p style={hint}>2~12자로 정해줘 · 나중에 바꿀 수 있어 🦜</p>
      </div>
      <label style={cbLabel}>
        <input type="checkbox" checked={terms} onChange={e => setTerms(e.target.checked)} />
        이용약관 동의 (필수)
      </label>
      <label style={cbLabel}>
        <input type="checkbox" checked={privacy} onChange={e => setPrivacy(e.target.checked)} />
        개인정보 처리방침 동의 (필수)
      </label>
      {error && <p style={errorText}>{error}</p>}
      <button type="submit" disabled={!canSubmit} style={submitBtn(canSubmit)}>
        {loading ? '가입 중…' : '가입하기'}
      </button>
    </form>
  );
}

// ── LoginPage ───────────────────────────────────────────────────────────

export function LoginPage() {
  const [tab, setTab] = useState<Tab>('login');
  const [signupSuccess, setSignupSuccess] = useState(false);

  return (
    <div
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        minHeight: '100vh', backgroundColor: 'var(--n10)', fontFamily: 'var(--font-ui)',
      }}
    >
      <div style={{ width: '360px', border: '2px solid var(--n40)', backgroundColor: 'var(--n20)' }}>

        {/* Tab bar */}
        <div style={{ display: 'flex', borderBottom: '2px solid var(--n40)' }}>
          {(['login', 'signup'] as Tab[]).map(t => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              style={{
                flex: 1, padding: '14px 8px',
                backgroundColor: tab === t ? 'var(--n20)' : 'var(--n10)',
                color: tab === t ? 'var(--text-primary)' : 'var(--text-dim)',
                border: 'none',
                borderTop: tab === t ? '2px solid var(--color-yellow)' : '2px solid transparent',
                fontFamily: 'var(--font-ui)', fontSize: '14px', cursor: 'pointer',
              }}
            >
              {t === 'login' ? '🪶 이미 코뉴야' : '🥚 처음 와 봤어'}
            </button>
          ))}
        </div>

        {/* Signup success banner */}
        {signupSuccess && tab === 'login' && (
          <div
            style={{
              padding: '10px 24px', backgroundColor: 'var(--n30)',
              borderBottom: '2px solid var(--n40)', fontSize: '13px', color: 'var(--text-primary)',
            }}
          >
            가입 완료! 로그인해줘 🦜
          </div>
        )}

        {/* Active form */}
        {tab === 'login' ? (
          <LoginForm onInteract={() => setSignupSuccess(false)} />
        ) : (
          <SignupForm onSuccess={() => { setTab('login'); setSignupSuccess(true); }} />
        )}

      </div>
    </div>
  );
}
