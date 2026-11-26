import React, { useCallback, useEffect, useState } from 'react';
import {
  ShieldCheck,
  SquaresFour,
  ClipboardText,
  PlusCircle,
  Warning,
  FileText,
  Users,
  Gear,
  SignOut,
  CaretRight,
  Fingerprint,
  Scales,
  CheckSquareOffset,
  House,
  List,
  X,
} from '@phosphor-icons/react';
import { api, clearSession, getSavedSession, saveSession } from './api';
import type { AppView, AuthUser, WorkspaceSnapshot } from './types';
import { LandingPage } from './components/LandingPage';
import { LoginView } from './components/LoginView';
import { DashboardView } from './components/DashboardView';
import {
  AuditDetailView,
  AuditProjectsList,
  NewAuditForm,
} from './components/AuditViews';
import { FindingsView } from './components/FindingsView';
import {
  ControlsSoAView,
  RisksAndFrameworksView,
} from './components/ControlsAndRisksView';
import {
  EvidenceVaultView,
  ReportsCenterView,
  SettingsAndAuditLogView,
  UserManagementView,
} from './components/EvidenceReportsSettings';
import { LegalPage, NotFoundPage } from './components/LegalAndNotFound';

export const App: React.FC = () => {
  const initialSession = getSavedSession();
  const [token, setToken] = useState<string | null>(initialSession.token);
  const [user, setUser] = useState<AuthUser | null>(initialSession.user);
  const [view, setView] = useState<AppView>(
    initialSession.token && initialSession.user ? 'dashboard' : 'landing'
  );
  const [previousView, setPreviousView] = useState<AppView>('landing');
  const [selectedAuditId, setSelectedAuditId] = useState<string>('AUD-2026-001');
  const [includeDemo, setIncludeDemo] = useState<boolean>(true);
  const [workspace, setWorkspace] = useState<WorkspaceSnapshot | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const snap = await api.workspace(includeDemo);
      setWorkspace(snap);
    } catch (err) {
      setLoadError(
        err instanceof Error ? err.message : 'Unable to reach SecureAudit SQLite API.'
      );
    } finally {
      setLoading(false);
    }
  }, [includeDemo]);

  // Restore the workspace only for an already-authenticated session.
  // Visitors must sign in explicitly — there is no automatic demo login.
  useEffect(() => {
    if (token && user) {
      loadWorkspace();
    } else {
      setLoading(false);
    }
  }, [loadWorkspace, token, user]);

  const handleLoginSuccess = (newToken: string, newUser: AuthUser) => {
    saveSession(newToken, newUser);
    setToken(newToken);
    setUser(newUser);
    setView('dashboard');
    loadWorkspace();
  };

  const handleSignOut = () => {
    clearSession();
    setToken(null);
    setUser(null);
    setView('login');
  };

  if (view === 'landing') {
    return (
      <LandingPage
        onOpenWorkspace={() => setView(token && user ? 'dashboard' : 'login')}
        onSignInClick={() => setView('login')}
        onOpenPrivacy={() => {
          setPreviousView('landing');
          setView('legal-privacy');
        }}
        onOpenTerms={() => {
          setPreviousView('landing');
          setView('legal-terms');
        }}
      />
    );
  }

  if (view === 'legal-privacy' || view === 'legal-terms') {
    return (
      <LegalPage
        kind={view === 'legal-privacy' ? 'privacy' : 'terms'}
        onBack={() => setView(previousView)}
      />
    );
  }

  if (view === 'not-found') {
    return <NotFoundPage onGoHome={() => setView('dashboard')} />;
  }

  if (view === 'login' || !token || !user) {
    return (
      <LoginView
        onSuccess={handleLoginSuccess}
        onBackToLanding={() => setView('landing')}
      />
    );
  }

  const navItems: Array<{ id: AppView; label: string; icon: React.ReactNode }> = [
    { id: 'dashboard', label: 'Dashboard', icon: <SquaresFour size={19} /> },
    { id: 'audits', label: 'Audit Projects', icon: <ClipboardText size={19} /> },
    { id: 'new-audit', label: 'New Audit', icon: <PlusCircle size={19} /> },
    { id: 'findings', label: 'Findings & CAPA', icon: <Warning size={19} /> },
    { id: 'controls-soa', label: 'Annex A & SoA', icon: <CheckSquareOffset size={19} /> },
    { id: 'risks', label: 'Risk & Frameworks', icon: <Scales size={19} /> },
    { id: 'evidence', label: 'Evidence Vault', icon: <Fingerprint size={19} /> },
    { id: 'reports', label: 'Reports', icon: <FileText size={19} /> },
    { id: 'users', label: 'User Management', icon: <Users size={19} /> },
    { id: 'settings', label: 'Settings & Logs', icon: <Gear size={19} /> },
  ];

  const initials = user.full_name
    .split(' ')
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const pageHeaders: Record<string, { title: string; sub: string }> = {
    dashboard: {
      title: 'Security Dashboard',
      sub: 'Overview of your ISO/IEC 27001 security audit programme, controls, and findings',
    },
    audits: {
      title: 'Audit Projects',
      sub: 'Manage planned, active, and completed ISMS internal and readiness audits',
    },
    'new-audit': {
      title: 'New Security Audit',
      sub: 'Configure scope, objectives, lead auditor, and baseline Annex A checklist',
    },
    findings: {
      title: 'Findings & Vulnerabilities',
      sub: 'All security nonconformities, root causes, and linked CAPA actions across active audits',
    },
    'controls-soa': {
      title: 'ISO/IEC 27001:2022 Controls & SoA',
      sub: 'Statement of Applicability across Organizational, People, Physical, and Technological domains',
    },
    risks: {
      title: 'Risk Register & Framework Mappings',
      sub: 'Clause 6.1.2 risk treatment scoring and illustrative NIST CSF 2.0 / SOC 2 mappings',
    },
    evidence: {
      title: 'Evidence Vault (SHA 256)',
      sub: 'Cryptographic file digest verification, media validation, and controlled artefact storage',
    },
    reports: {
      title: 'Executive Audit Reports',
      sub: 'Preview and export structured PDF audit reports and 9 sheet Excel workbooks',
    },
    users: {
      title: 'User & Role Management',
      sub: 'Salted scrypt local RBAC accounts, permissions, and lockout administration',
    },
    settings: {
      title: 'Workspace Settings & Audit Trail',
      sub: 'Demo data separation, CSV/JSON portability, and tamper evident SHA 256 log verification',
    },
  };

  const selectedAudit =
    workspace?.audits.find((a) => a.audit_id === selectedAuditId) ||
    workspace?.audits[0];

  return (
    <div className="flex min-h-screen bg-[#F8FAFC] text-[#0F172A]">
      {/* Dark Left Sidebar matching Figures 1–3 (`#0F172A` / `#181818` surface) */}
      <aside
        aria-label="Workspace navigation"
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col justify-between bg-[#0F172A] p-4 text-white transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div>
          <div className="flex items-center justify-between px-2 py-2">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#2563EB] text-white">
                <ShieldCheck size={24} weight="fill" />
              </span>
              <div>
                <div className="title-3 text-white">SecureAudit</div>
                <div className="caption-4 text-[#94A3B8]">Web Tracker</div>
              </div>
            </div>
            <button
              type="button"
              aria-label="Close sidebar"
              onClick={() => setSidebarOpen(false)}
              className="rounded-lg p-1.5 text-[#94A3B8] lg:hidden"
            >
              <X size={20} />
            </button>
          </div>

          <div className="mt-6 px-2">
            <div className="caption-4 uppercase tracking-wider text-[#64748B]">Main menu</div>
            <nav className="mt-2 flex flex-col gap-1">
              {navItems.map((item) => {
                const isActive =
                  view === item.id || (view === 'audit-detail' && item.id === 'audits');
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => {
                      setView(item.id);
                      setSidebarOpen(false);
                    }}
                    className={`flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left transition-colors duration-300 ${
                      isActive
                        ? 'bg-[#2563EB] text-white'
                        : 'text-[#CBD5E1] hover:bg-[#1E293B] hover:text-white'
                    }`}
                  >
                    <span className="flex items-center gap-3 body-5">
                      {item.icon}
                      {item.label}
                    </span>
                    {isActive && <CaretRight size={14} weight="bold" />}
                  </button>
                );
              })}

              <button
                type="button"
                onClick={() => {
                  setView('landing');
                  setSidebarOpen(false);
                }}
                className="mt-2 flex w-full items-center gap-3 rounded-xl border border-[#1E293B] px-3 py-2 text-left caption-1 text-[#93C5FD] hover:bg-[#1E293B]"
              >
                <House size={18} />
                Product Overview Page
              </button>
            </nav>
          </div>
        </div>

        {/* User Profile Card & Sign Out matching Figures 1–3 */}
        <div className="mt-6 border-t border-[#1E293B] pt-4">
          <div className="rounded-xl bg-[#1E293B] p-3">
            <div className="flex items-center gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#6D28D9] caption-3 text-white">
                {initials}
              </span>
              <div className="min-w-0">
                <div className="title-4 truncate text-white">{user.full_name}</div>
                <div className="caption-4 truncate text-[#94A3B8]">{user.email}</div>
              </div>
            </div>
            <div className="mt-2">
              <span className="caption-4 inline-block rounded-md bg-[#4C1D95] px-2 py-0.5 text-[#DDD6FE]">
                {user.role === 'Admin' ? 'Administrator' : user.role}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSignOut}
            className="mt-3 flex w-full items-center gap-2 rounded-lg px-3 py-2 caption-1 text-[#94A3B8] hover:bg-[#1E293B] hover:text-white"
          >
            <SignOut size={18} />
            Sign Out / Switch Role
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Mobile Header */}
        <div className="flex items-center justify-between border-b border-[#E2E8F0] bg-white px-4 py-3 lg:hidden">
          <button
            type="button"
            aria-label="Open navigation menu"
            onClick={() => setSidebarOpen(true)}
            className="rounded-lg border border-[#CBD5E1] p-2 text-[#0F172A]"
          >
            <List size={20} />
          </button>
          <span className="title-3 text-[#0F172A]">SecureAudit</span>
          <span className="caption-3 rounded bg-[#EFF6FF] px-2 py-0.5 text-[#2563EB]">
            {user.role}
          </span>
        </div>

        <main id="main-content" className="mx-auto w-full max-w-7xl flex-1 p-4 sm:p-8">
          {/* Illustrative Demo Data Banner (per Annexure B) */}
          {includeDemo && workspace?.audits.some((a) => a.record_type === 'DEMO') && (
            <div className="mb-6 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[#FDE68A] bg-[#FFFBEB] px-4 py-2.5 caption-1 text-[#92400E]">
              <span>
                <strong>DEMO DATA INCLUDED</strong> · Illustrative sample records appear in this
                view and do not represent real audit evidence or ISO certification.
              </span>
              <button
                type="button"
                onClick={() => setIncludeDemo(false)}
                className="caption-3 underline hover:text-[#78350F]"
              >
                Hide demo records
              </button>
            </div>
          )}

          {!includeDemo && (
            <div className="mb-6 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[#A7F3D0] bg-[#ECFDF5] px-4 py-2.5 caption-1 text-[#065F46]">
              <span>
                <strong>USER WORKSPACE ONLY</strong> · Showing only records created or imported by
                users. Demo records are hidden.
              </span>
              <button
                type="button"
                onClick={() => setIncludeDemo(true)}
                className="caption-3 underline hover:text-[#064E3B]"
              >
                Show demo records
              </button>
            </div>
          )}

          {view !== 'audit-detail' && pageHeaders[view] && (
            <header className="mb-6">
              <h1 className="heading-4 text-[#0F172A]">{pageHeaders[view].title}</h1>
              <p className="body-5 mt-1 text-[#64748B]">{pageHeaders[view].sub}</p>
            </header>
          )}

          {/* B9: Skeleton loading & specific inline error states */}
          {loading && !workspace && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
              {[1, 2, 3, 4].map((n) => (
                <div
                  key={n}
                  className="h-28 animate-pulse rounded-2xl border border-[#E2E8F0] bg-white p-6"
                >
                  <div className="h-4 w-24 rounded bg-[#E2E8F0]" />
                  <div className="mt-4 h-7 w-16 rounded bg-[#E2E8F0]" />
                </div>
              ))}
            </div>
          )}

          {loadError && (
            <div
              role="alert"
              className="rounded-2xl border border-[#FECACA] bg-[#FEF2F2] p-6 text-[#991B1B]"
            >
              <div className="title-3">Workspace sync failed</div>
              <p className="body-5 mt-1">{loadError}</p>
              <button
                type="button"
                onClick={loadWorkspace}
                className="btn-main button-sm mt-4 rounded-lg bg-[#991B1B] text-white"
              >
                Retry connection
              </button>
            </div>
          )}

          {workspace && !loadError && (
            <>
              {view === 'dashboard' && (
                <DashboardView
                  data={workspace}
                  onSelectAudit={(aid) => {
                    setSelectedAuditId(aid);
                    setView('audit-detail');
                  }}
                  onViewAllAudits={() => setView('audits')}
                  onNewAudit={() => setView('new-audit')}
                />
              )}

              {view === 'audits' && (
                <AuditProjectsList
                  data={workspace}
                  user={user}
                  token={token}
                  onSelectAudit={(aid) => {
                    setSelectedAuditId(aid);
                    setView('audit-detail');
                  }}
                  onNewAudit={() => setView('new-audit')}
                  onRefresh={loadWorkspace}
                />
              )}

              {view === 'new-audit' && (
                <NewAuditForm
                  user={user}
                  token={token}
                  onCreated={(aid) => {
                    loadWorkspace().then(() => {
                      setSelectedAuditId(aid);
                      setView('audit-detail');
                    });
                  }}
                  onCancel={() => setView('audits')}
                />
              )}

              {view === 'audit-detail' && selectedAudit && (
                <AuditDetailView
                  audit={selectedAudit}
                  data={workspace}
                  user={user}
                  token={token}
                  onBack={() => setView('audits')}
                  onRefresh={loadWorkspace}
                />
              )}

              {view === 'findings' && (
                <FindingsView
                  data={workspace}
                  user={user}
                  token={token}
                  onSelectAudit={(aid) => {
                    setSelectedAuditId(aid);
                    setView('audit-detail');
                  }}
                  onRefresh={loadWorkspace}
                />
              )}

              {view === 'controls-soa' && (
                <ControlsSoAView
                  data={workspace}
                  user={user}
                  token={token}
                  onRefresh={loadWorkspace}
                />
              )}

              {view === 'risks' && (
                <RisksAndFrameworksView
                  data={workspace}
                  user={user}
                  token={token}
                  onRefresh={loadWorkspace}
                />
              )}

              {view === 'evidence' && (
                <EvidenceVaultView
                  data={workspace}
                  user={user}
                  token={token}
                  onRefresh={loadWorkspace}
                />
              )}

              {view === 'reports' && <ReportsCenterView data={workspace} />}

              {view === 'users' && (
                <UserManagementView
                  data={workspace}
                  user={user}
                  token={token}
                  onRefresh={loadWorkspace}
                />
              )}

              {view === 'settings' && (
                <SettingsAndAuditLogView
                  data={workspace}
                  user={user}
                  token={token}
                  includeDemo={includeDemo}
                  onToggleDemo={setIncludeDemo}
                  onRefresh={loadWorkspace}
                />
              )}
            </>
          )}

          {/* Footer links inside workspace */}
          <footer className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-[#E2E8F0] pt-6 caption-4 text-[#64748B]">
            <span>
              SecureAudit ISMS ISO/IEC 27001:2022 Audit Tracker · Verify conclusions through your approved governance process.
            </span>
            <div className="flex items-center gap-4">
              <button
                type="button"
                onClick={() => {
                  setPreviousView(view);
                  setView('legal-privacy');
                }}
                className="hover:text-[#0F172A]"
              >
                Privacy policy
              </button>
              <button
                type="button"
                onClick={() => {
                  setPreviousView(view);
                  setView('legal-terms');
                }}
                className="hover:text-[#0F172A]"
              >
                Terms of use
              </button>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
};

export default App;
