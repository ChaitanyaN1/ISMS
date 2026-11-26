import React, { useEffect, useState } from 'react';
import { ShieldCheck, LockKey, ArrowLeft, WarningCircle, CheckCircle } from '@phosphor-icons/react';
import { api } from '../api';
import type { AuthUser } from '../types';

interface LoginViewProps {
  onSuccess: (token: string, user: AuthUser) => void;
  onBackToLanding: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onSuccess, onBackToLanding }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('Admin@27001!');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [demoAccounts, setDemoAccounts] = useState<
    Array<{ username: string; full_name: string; email: string; role: string; password: string }>
  >([]);

  useEffect(() => {
    api
      .demoAccounts()
      .then((res) => setDemoAccounts(res.accounts || []))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    if (!username.trim() || !password) {
      setErrorMsg('Sign in failed. Enter both username and password.');
      return;
    }
    setLoading(true);
    try {
      const res = await api.login(username.trim(), password);
      onSuccess(res.token, res.user);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#181818] px-4 py-12 text-white">
      <div className="mx-auto max-w-md">
        <button
          type="button"
          onClick={onBackToLanding}
          className="btn-main button-sm mb-6 inline-flex items-center gap-2 rounded-lg border border-[#313131] bg-[#1F1F1F] text-[#CBD5E1] hover:bg-[#272727]"
        >
          <ArrowLeft size={16} />
          Back to overview
        </button>

        <div className="rounded-2xl border border-[#313131] bg-[#1F1F1F] p-8">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#2563EB] text-white">
              <ShieldCheck size={24} weight="fill" />
            </span>
            <div>
              <h1 className="title-1 text-white">SecureAudit sign in</h1>
              <p className="caption-2 text-[#94A3B8]">
                Salted scrypt authentication · 5 attempt lockout policy
              </p>
            </div>
          </div>

          {errorMsg && (
            <div
              role="alert"
              className="mt-6 flex items-start gap-2 rounded-lg border border-[#FECACA] bg-[#FEF2F2] p-3 text-[#991B1B]"
            >
              <WarningCircle size={18} className="mt-0.5 shrink-0" weight="fill" />
              <span className="body-5">{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4" noValidate>
            <div>
              <label htmlFor="login-username" className="title-4 block text-[#E2E8F0]">
                Username or email
              </label>
              <input
                id="login-username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="body-5 mt-1.5 w-full rounded-lg border border-[#313131] bg-[#181818] px-3 py-2 text-white"
              />
            </div>

            <div>
              <label htmlFor="login-password" className="title-4 block text-[#E2E8F0]">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="body-5 mt-1.5 w-full rounded-lg border border-[#313131] bg-[#181818] px-3 py-2 text-white"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-main button-md mt-2 inline-flex items-center justify-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8] disabled:opacity-60"
            >
              <LockKey size={18} weight="bold" />
              {loading ? 'Verifying scrypt digest...' : 'Sign in to audit workspace'}
            </button>
          </form>

          {demoAccounts.length > 0 && (
            <div className="mt-8 border-t border-[#313131] pt-6">
              <p className="caption-3 uppercase tracking-wider text-[#94A3B8]">
                Local role demonstration accounts (click to autofill)
              </p>
              <div className="mt-3 grid grid-cols-2 gap-2">
                {demoAccounts.map((acc) => (
                  <button
                    key={acc.username}
                    type="button"
                    onClick={() => {
                      setUsername(acc.username);
                      setPassword(acc.password);
                      setErrorMsg(null);
                    }}
                    className="flex flex-col rounded-lg border border-[#313131] bg-[#272727] p-2.5 text-left hover:border-[#60A5FA]"
                  >
                    <div className="flex items-center justify-between">
                      <span className="caption-3 text-white">{acc.role}</span>
                      <CheckCircle size={14} className="text-[#60A5FA]" />
                    </div>
                    <span className="caption-4 mt-1 font-mono text-[#94A3B8]">{acc.username}</span>
                  </button>
                ))}
              </div>
              <p className="caption-5 mt-3 text-[#64748B]">
                Demo credentials are strictly for local prototype evaluation and must never be used with sensitive organizational records.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
