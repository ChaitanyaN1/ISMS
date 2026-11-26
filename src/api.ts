import type { AuthUser, WorkspaceSnapshot } from './types';

const TOKEN_KEY = 'secureaudit_session_token';
const USER_KEY = 'secureaudit_session_user';

export function getSavedSession(): { token: string | null; user: AuthUser | null } {
  const token = localStorage.getItem(TOKEN_KEY);
  const rawUser = localStorage.getItem(USER_KEY);
  if (!token || !rawUser) return { token: null, user: null };
  try {
    return { token, user: JSON.parse(rawUser) as AuthUser };
  } catch {
    return { token: null, user: null };
  }
}

export function saveSession(token: string, user: AuthUser): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.detail) detail = String(errJson.detail);
    } catch {
      // ignore json parse error
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export const api = {
  login: (username: string, password: string) =>
    apiRequest<{ ok: boolean; token: string; user: AuthUser }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  demoAccounts: () =>
    apiRequest<{
      notice: string;
      accounts: Array<{ username: string; full_name: string; email: string; role: string; password: string }>;
    }>('/api/auth/demo-accounts'),

  workspace: (includeDemo: boolean) =>
    apiRequest<WorkspaceSnapshot>(`/api/workspace?include_demo=${includeDemo ? 'true' : 'false'}`),

  saveAudit: (payload: Record<string, unknown>, token: string) =>
    apiRequest<{ audit: unknown }>('/api/audits', { method: 'POST', body: JSON.stringify(payload) }, token),

  deleteAudit: (auditId: string, token: string) =>
    apiRequest<{ deleted: string }>(`/api/audits/${encodeURIComponent(auditId)}`, { method: 'DELETE' }, token),

  saveTest: (payload: Record<string, unknown>, token: string) =>
    apiRequest<{ test: unknown; audit_compliance: number | null }>(
      '/api/tests',
      { method: 'POST', body: JSON.stringify(payload) },
      token
    ),

  saveFinding: (payload: Record<string, unknown>, token: string) =>
    apiRequest<{ finding: unknown }>('/api/findings', { method: 'POST', body: JSON.stringify(payload) }, token),

  saveAction: (payload: Record<string, unknown>, token: string) =>
    apiRequest<{ action: unknown }>('/api/actions', { method: 'POST', body: JSON.stringify(payload) }, token),

  updateControl: (controlId: string, payload: Record<string, unknown>, token: string) =>
    apiRequest<{ control: unknown }>(
      `/api/controls/${encodeURIComponent(controlId)}`,
      { method: 'PUT', body: JSON.stringify(payload) },
      token
    ),

  saveRisk: (payload: Record<string, unknown>, token: string) =>
    apiRequest<{ risk: unknown }>('/api/risks', { method: 'POST', body: JSON.stringify(payload) }, token),

  uploadEvidence: (formData: FormData, token: string) =>
    apiRequest<{ evidence: unknown }>('/api/evidence/upload', { method: 'POST', body: formData }, token),

  verifyEvidence: (evidenceId: string, token: string) =>
    apiRequest<{
      evidence_id: string;
      expected_sha256: string;
      actual_sha256: string;
      matches: boolean;
      status: string;
    }>(`/api/evidence/${encodeURIComponent(evidenceId)}/verify`, { method: 'POST' }, token),

  approveReport: (auditId: string, payload: Record<string, unknown>, token: string) =>
    apiRequest<{ audit: unknown }>(
      `/api/audits/${encodeURIComponent(auditId)}/approve`,
      { method: 'POST', body: JSON.stringify(payload) },
      token
    ),

  createUser: (payload: Record<string, unknown>, token: string) =>
    apiRequest<{ created_user_id: string }>('/api/users', { method: 'POST', body: JSON.stringify(payload) }, token),

  unlockUser: (username: string, token: string) =>
    apiRequest<{ unlocked: string }>(
      `/api/users/${encodeURIComponent(username)}/unlock`,
      { method: 'POST' },
      token
    ),

  importAuditsCsv: (file: File, token: string) => {
    const fd = new FormData();
    fd.append('file', file);
    return apiRequest<{ imported: number; skipped: number }>(
      '/api/import/audits-csv',
      { method: 'POST', body: fd },
      token
    );
  },

  verifyBackupJson: (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return apiRequest<{
      valid: boolean;
      expected_sha256: string;
      actual_sha256: string;
      record_counts: Record<string, number>;
    }>('/api/backup/verify', { method: 'POST', body: fd });
  },

  restoreDemo: (token: string) =>
    apiRequest<{ restored: number }>('/api/demo/restore', { method: 'POST' }, token),

  removeDemo: (token: string) =>
    apiRequest<{ removed: number }>('/api/demo/remove', { method: 'POST' }, token),
};
