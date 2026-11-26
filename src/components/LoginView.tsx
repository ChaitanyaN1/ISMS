import React, { useState } from 'react';
import { ShieldCheck, LockKey, ArrowLeft, WarningCircle } from '@phosphor-icons/react';
import { api } from '../api';
import type { AuthUser } from '../types';

interface LoginViewProps {
  onSuccess: (token: string, user: AuthUser) => void;
  onBackToLanding: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onSuccess, onBackToLanding }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

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
                name="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck={false}
                placeholder="Enter your username"
                required
                className="body-5 mt-1.5 w-full rounded-lg border border-[#313131] bg-[#181818] px-3 py-2 text-white placeholder:text-[#64748B]"
              />
            </div>

            <div>
              <label htmlFor="login-password" className="title-4 block text-[#E2E8F0]">
                Password
              </label>
              <input
                id="login-password"
                name="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                placeholder="Enter your password"
                required
                className="body-5 mt-1.5 w-full rounded-lg border border-[#313131] bg-[#181818] px-3 py-2 text-white placeholder:text-[#64748B]"
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

          <p className="caption-5 mt-6 border-t border-[#313131] pt-6 text-[#64748B]">
            Accounts are provisioned by an administrator. Contact your ISMS lead if you need access
            or have forgotten your password.
          </p>
        </div>
      </div>
    </div>
  );
};
