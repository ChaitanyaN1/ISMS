import React, { useState } from 'react';
import {
  Warning,
  MagnifyingGlass,
  Plus,
  User,
  CalendarBlank,
  PushPin,
  CheckCircle,
} from '@phosphor-icons/react';
import { api } from '../api';
import type { AuthUser, WorkspaceSnapshot } from '../types';

export const FindingsView: React.FC<{
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  onSelectAudit: (auditId: string) => void;
  onRefresh: () => void;
}> = ({ data, user, token, onSelectAudit, onRefresh }) => {
  const [search, setSearch] = useState('');
  const [sevFilter, setSevFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [tab, setTab] = useState<'findings' | 'capa'>('findings');
  const [showAddFinding, setShowAddFinding] = useState(false);
  const [showAddCapa, setShowAddCapa] = useState(false);
  const [banner, setBanner] = useState<{ ok: boolean; msg: string } | null>(null);

  // Finding form state
  const [fAuditId, setFAuditId] = useState(data.audits[0]?.audit_id || 'AUD-2026-001');
  const [fCtrlId, setFCtrlId] = useState('A.8.5');
  const [fTitle, setFTitle] = useState('');
  const [fSev, setFSev] = useState('High');
  const [fStatus, setFStatus] = useState('Open');
  const [fAsset, setFAsset] = useState('');
  const [fCondition, setFCondition] = useState('');
  const [fRecommendation, setFRecommendation] = useState('');
  const [fOwner, setFOwner] = useState(user.full_name);
  const [fDue, setFDue] = useState('2026-12-15');

  // CAPA form state
  const [cFindingId, setCFindingId] = useState(data.findings[0]?.finding_id || 'FND-2026-001');
  const [cTitle, setCTitle] = useState('');
  const [cType, setCType] = useState('Corrective');
  const [cOwner, setCOwner] = useState(user.full_name);
  const [cDue, setCDue] = useState('2026-12-15');
  const [cStatus, setCStatus] = useState('Open');
  const [cPlan, setCPlan] = useState('');

  const canFinding = user.role === 'Admin' || user.role === 'Auditor';
  const canCapa = user.role === 'Admin' || user.role === 'Auditor' || user.role === 'Risk Owner';

  const total = data.findings.length;
  const critical = data.findings.filter((f) => f.severity === 'Critical').length;
  const high = data.findings.filter((f) => f.severity === 'High').length;
  const open = data.findings.filter(
    (f) => f.status !== 'Resolved' && f.status !== 'Closed'
  ).length;
  const resolved = total - open;

  const filteredFindings = data.findings.filter((f) => {
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      f.title.toLowerCase().includes(q) ||
      f.finding_id.toLowerCase().includes(q) ||
      f.affected_asset.toLowerCase().includes(q) ||
      f.owner.toLowerCase().includes(q);
    const matchSev = sevFilter === 'All' || f.severity === sevFilter;
    const matchSt = statusFilter === 'All' || f.status === statusFilter;
    return matchSearch && matchSev && matchSt;
  });

  const handleSaveFinding = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fTitle.trim()) {
      setBanner({ ok: false, msg: 'Enter a finding title before saving.' });
      return;
    }
    try {
      await api.saveFinding(
        {
          audit_id: fAuditId,
          control_id: fCtrlId,
          title: fTitle.trim(),
          severity: fSev,
          status: fStatus,
          affected_asset: fAsset,
          condition: fCondition,
          recommendation: fRecommendation,
          owner: fOwner,
          due_date: fDue,
        },
        token
      );
      setShowAddFinding(false);
      setFTitle('');
      setFCondition('');
      setFRecommendation('');
      setBanner({ ok: true, msg: 'Finding logged to SQLite register.' });
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Save failed.' });
    }
  };

  const handleSaveCapa = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cTitle.trim()) {
      setBanner({ ok: false, msg: 'Enter a CAPA action title before saving.' });
      return;
    }
    try {
      await api.saveAction(
        {
          finding_id: cFindingId,
          title: cTitle.trim(),
          action_type: cType,
          owner: cOwner,
          due_date: cDue,
          status: cStatus,
          corrective_action: cPlan,
        },
        token
      );
      setShowAddCapa(false);
      setCTitle('');
      setCPlan('');
      setBanner({ ok: true, msg: 'Corrective / preventive action saved.' });
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Save failed.' });
    }
  };

  const handleFindingQuickStatus = async (findingId: string, nextStatus: string) => {
    const existing = data.findings.find((f) => f.finding_id === findingId);
    if (!existing) return;
    try {
      await api.saveFinding({ ...existing, status: nextStatus }, token);
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Update failed.' });
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* 5 Colored Summary Cards matching Figure 3 */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        <div className="rounded-2xl bg-[#181818] p-5 text-center text-white">
          <div className="heading-4 font-mono">{total}</div>
          <div className="caption-2 mt-1 text-[#CBD5E1]">Total</div>
        </div>
        <div className="rounded-2xl bg-[#7F1D1D] p-5 text-center text-white">
          <div className="heading-4 font-mono">{critical}</div>
          <div className="caption-2 mt-1 text-[#FECACA]">Critical</div>
        </div>
        <div className="rounded-2xl bg-[#DC2626] p-5 text-center text-white">
          <div className="heading-4 font-mono">{high}</div>
          <div className="caption-2 mt-1 text-[#FEE2E2]">High</div>
        </div>
        <div className="rounded-2xl bg-[#D97706] p-5 text-center text-white">
          <div className="heading-4 font-mono">{open}</div>
          <div className="caption-2 mt-1 text-[#FEF3C7]">Open</div>
        </div>
        <div className="rounded-2xl bg-[#059669] p-5 text-center text-white">
          <div className="heading-4 font-mono">{resolved}</div>
          <div className="caption-2 mt-1 text-[#D1FAE5]">Resolved</div>
        </div>
      </div>

      {banner && (
        <div
          className={`rounded-xl border px-4 py-3 body-5 ${
            banner.ok
              ? 'border-[#A7F3D0] bg-[#ECFDF5] text-[#065F46]'
              : 'border-[#FECACA] bg-[#FEF2F2] text-[#991B1B]'
          }`}
        >
          {banner.msg}
        </div>
      )}

      {/* Mode Switcher: Findings vs CAPA */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setTab('findings')}
            className={`btn-main button-sm rounded-lg ${
              tab === 'findings'
                ? 'bg-[#0F172A] text-white'
                : 'border border-[#CBD5E1] bg-white text-[#475569]'
            }`}
          >
            Findings & Vulnerabilities ({data.findings.length})
          </button>
          <button
            type="button"
            onClick={() => setTab('capa')}
            className={`btn-main button-sm rounded-lg ${
              tab === 'capa'
                ? 'bg-[#0F172A] text-white'
                : 'border border-[#CBD5E1] bg-white text-[#475569]'
            }`}
          >
            CAPA Remediation Tracker ({data.actions.length})
          </button>
        </div>

        <div className="flex items-center gap-2">
          {canFinding && tab === 'findings' && (
            <button
              type="button"
              onClick={() => setShowAddFinding((v) => !v)}
              className="btn-main button-sm inline-flex items-center gap-1.5 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
            >
              <Plus size={16} weight="bold" />
              Log finding
            </button>
          )}
          {canCapa && tab === 'capa' && (
            <button
              type="button"
              onClick={() => setShowAddCapa((v) => !v)}
              className="btn-main button-sm inline-flex items-center gap-1.5 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
            >
              <Plus size={16} weight="bold" />
              Create CAPA action
            </button>
          )}
        </div>
      </div>

      {tab === 'findings' && (
        <>
          {/* Search & filter bar matching Figure 3 */}
          <div className="flex flex-col gap-3 rounded-2xl border border-[#E2E8F0] bg-white p-4 sm:flex-row">
            <div className="relative flex-1">
              <MagnifyingGlass
                size={18}
                className="pointer-events-none absolute top-2.5 left-3 text-[#64748B]"
              />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search findings by title, asset, owner, or ID"
                className="body-5 w-full rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] py-2 pr-3 pl-9"
              />
            </div>
            <select
              value={sevFilter}
              onChange={(e) => setSevFilter(e.target.value)}
              aria-label="Filter by severity"
              className="body-5 rounded-lg border border-[#E2E8F0] bg-white px-3 py-2"
            >
              <option value="All">All severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              aria-label="Filter by finding status"
              className="body-5 rounded-lg border border-[#E2E8F0] bg-white px-3 py-2"
            >
              <option value="All">All statuses</option>
              <option value="Open">Open</option>
              <option value="In Remediation">In Remediation</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>
          </div>

          {showAddFinding && (
            <form
              onSubmit={handleSaveFinding}
              className="rounded-2xl border border-[#BFDBFE] bg-white p-6"
            >
              <h3 className="title-2 text-[#0F172A]">Log audit nonconformity / finding</h3>
              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                <div>
                  <label className="caption-3 block text-[#475569]">Linked audit</label>
                  <select
                    value={fAuditId}
                    onChange={(e) => setFAuditId(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
                  >
                    {data.audits.map((a) => (
                      <option key={a.audit_id} value={a.audit_id}>
                        {a.audit_id} · {a.title}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Control ID</label>
                  <input
                    type="text"
                    value={fCtrlId}
                    onChange={(e) => setFCtrlId(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Severity</label>
                  <select
                    value={fSev}
                    onChange={(e) => setFSev(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
                  >
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <label className="caption-3 block text-[#475569]">Finding title</label>
                  <input
                    type="text"
                    value={fTitle}
                    onChange={(e) => setFTitle(e.target.value)}
                    placeholder="Missing MFA on Emergency Admin Accounts"
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Affected asset</label>
                  <input
                    type="text"
                    value={fAsset}
                    onChange={(e) => setFAsset(e.target.value)}
                    placeholder="Cloud Console"
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Assigned owner</label>
                  <input
                    type="text"
                    value={fOwner}
                    onChange={(e) => setFOwner(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Target due date</label>
                  <input
                    type="date"
                    value={fDue}
                    onChange={(e) => setFDue(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Status</label>
                  <select
                    value={fStatus}
                    onChange={(e) => setFStatus(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
                  >
                    <option value="Open">Open</option>
                    <option value="In Remediation">In Remediation</option>
                    <option value="Resolved">Resolved</option>
                  </select>
                </div>
              </div>
              <textarea
                rows={2}
                value={fCondition}
                onChange={(e) => setFCondition(e.target.value)}
                placeholder="Observed condition against criteria..."
                className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
              <textarea
                rows={2}
                value={fRecommendation}
                onChange={(e) => setFRecommendation(e.target.value)}
                placeholder="Remediation recommendation..."
                className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
              <div className="mt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddFinding(false)}
                  className="btn-main button-xsm rounded-lg border border-[#CBD5E1]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-main button-xsm rounded-lg bg-[#2563EB] text-white"
                >
                  Save finding
                </button>
              </div>
            </form>
          )}

          {/* Finding Cards matching Figure 3 */}
          <div className="flex flex-col gap-4">
            {filteredFindings.map((f) => {
              const linkedAudit = data.audits.find((a) => a.audit_id === f.audit_id);
              const isCrit = f.severity === 'Critical';
              const isHigh = f.severity === 'High';
              return (
                <article
                  key={f.finding_id}
                  className="rounded-2xl border border-[#E2E8F0] bg-white p-6"
                >
                  <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
                    <div className="flex items-start gap-4">
                      <div
                        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${
                          isCrit
                            ? 'bg-[#7F1D1D] text-white'
                            : isHigh
                            ? 'bg-[#FEF2F2] text-[#DC2626]'
                            : 'bg-[#FFFBEB] text-[#D97706]'
                        }`}
                      >
                        <Warning size={20} weight="bold" />
                      </div>
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className={`caption-3 rounded-full px-2.5 py-0.5 text-white ${
                              isCrit
                                ? 'bg-[#7F1D1D]'
                                : isHigh
                                ? 'bg-[#DC2626]'
                                : 'bg-[#D97706]'
                            }`}
                          >
                            {f.severity}
                          </span>
                          <span
                            className={`caption-3 rounded-full px-2.5 py-0.5 ${
                              f.status === 'Open'
                                ? 'bg-[#FEF2F2] text-[#991B1B]'
                                : f.status === 'In Remediation'
                                ? 'bg-[#FFFBEB] text-[#92400E]'
                                : 'bg-[#ECFDF5] text-[#065F46]'
                            }`}
                          >
                            {f.status}
                          </span>
                          {f.control_id && (
                            <span className="caption-3 font-mono rounded bg-[#F1F5F9] px-2 py-0.5 text-[#334155]">
                              {f.control_id}
                            </span>
                          )}
                          <button
                            type="button"
                            onClick={() => onSelectAudit(f.audit_id)}
                            className="caption-3 text-[#2563EB] hover:underline"
                          >
                            {linkedAudit?.title || f.audit_id}
                          </button>
                        </div>

                        <h3 className="title-2 mt-2 text-[#0F172A]">{f.title}</h3>
                        <p className="body-5 mt-1 text-[#475569]">{f.condition}</p>
                        {f.recommendation && (
                          <p className="body-5 mt-2 text-[#065F46]">
                            → {f.recommendation}
                          </p>
                        )}

                        <div className="mt-3 flex flex-wrap items-center gap-4 caption-4 text-[#64748B]">
                          {f.affected_asset && (
                            <span className="inline-flex items-center gap-1">
                              <PushPin size={13} className="text-[#DC2626]" weight="fill" />
                              {f.affected_asset}
                            </span>
                          )}
                          <span className="inline-flex items-center gap-1">
                            <User size={13} />
                            {f.owner || 'Unassigned'}
                          </span>
                          {f.due_date && (
                            <span className="inline-flex items-center gap-1">
                              <CalendarBlank size={13} />
                              Due: {f.due_date}
                            </span>
                          )}
                          {f.found_date && <span>Found: {f.found_date}</span>}
                        </div>
                      </div>
                    </div>

                    {canFinding && (
                      <select
                        value={f.status}
                        aria-label={`Update status for ${f.finding_id}`}
                        onChange={(e) => handleFindingQuickStatus(f.finding_id, e.target.value)}
                        className="caption-3 rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1.5 text-[#0F172A]"
                      >
                        <option value="Open">Open</option>
                        <option value="In Remediation">In Remediation</option>
                        <option value="Resolved">Resolved</option>
                        <option value="Closed">Closed</option>
                      </select>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        </>
      )}

      {tab === 'capa' && (
        <div className="flex flex-col gap-4">
          {showAddCapa && (
            <form
              onSubmit={handleSaveCapa}
              className="rounded-2xl border border-[#BFDBFE] bg-white p-6"
            >
              <h3 className="title-2 text-[#0F172A]">Assign corrective / preventive action</h3>
              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                <div>
                  <label className="caption-3 block text-[#475569]">Linked finding</label>
                  <select
                    value={cFindingId}
                    onChange={(e) => setCFindingId(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
                  >
                    {data.findings.map((f) => (
                      <option key={f.finding_id} value={f.finding_id}>
                        {f.finding_id} · {f.title}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Action type</label>
                  <select
                    value={cType}
                    onChange={(e) => setCType(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
                  >
                    <option value="Corrective">Corrective</option>
                    <option value="Preventive">Preventive</option>
                  </select>
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Status</label>
                  <select
                    value={cStatus}
                    onChange={(e) => setCStatus(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
                  >
                    <option value="Open">Open</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Verified">Verified</option>
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <label className="caption-3 block text-[#475569]">CAPA title</label>
                  <input
                    type="text"
                    value={cTitle}
                    onChange={(e) => setCTitle(e.target.value)}
                    placeholder="Enforce hardware FIDO2 keys on break glass accounts"
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Due date</label>
                  <input
                    type="date"
                    value={cDue}
                    onChange={(e) => setCDue(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                  />
                </div>
              </div>
              <input
                type="text"
                value={cOwner}
                onChange={(e) => setCOwner(e.target.value)}
                placeholder="Action owner"
                className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
              <textarea
                rows={2}
                value={cPlan}
                onChange={(e) => setCPlan(e.target.value)}
                placeholder="Detailed remediation plan and verification criteria..."
                className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
              <div className="mt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddCapa(false)}
                  className="btn-main button-xsm rounded-lg border border-[#CBD5E1]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-main button-xsm rounded-lg bg-[#2563EB] text-white"
                >
                  Save CAPA
                </button>
              </div>
            </form>
          )}

          {data.actions.map((act) => {
            const today = new Date().toISOString().slice(0, 10);
            const isDone = act.status === 'Completed' || act.status === 'Verified';
            const isOverdue = !isDone && act.due_date && act.due_date < today;
            return (
              <div
                key={act.action_id}
                className="rounded-2xl border border-[#E2E8F0] bg-white p-5"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="caption-3 font-mono rounded bg-[#F1F5F9] px-2 py-0.5 text-[#0F172A]">
                      {act.action_id}
                    </span>
                    <span className="caption-3 rounded bg-[#EFF6FF] px-2 py-0.5 text-[#1E40AF]">
                      {act.action_type} · {act.finding_id}
                    </span>
                    {isOverdue && (
                      <span className="caption-3 rounded bg-[#FEF2F2] px-2 py-0.5 text-[#991B1B]">
                        Overdue
                      </span>
                    )}
                  </div>
                  <span
                    className={`caption-3 inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 ${
                      isDone
                        ? 'bg-[#ECFDF5] text-[#065F46]'
                        : 'bg-[#FFFBEB] text-[#92400E]'
                    }`}
                  >
                    {isDone && <CheckCircle size={13} weight="fill" />}
                    {act.status}
                  </span>
                </div>
                <h3 className="title-2 mt-2 text-[#0F172A]">{act.title}</h3>
                <p className="body-5 mt-1 text-[#475569]">{act.corrective_action}</p>
                {act.preventive_action && (
                  <p className="caption-1 mt-1 text-[#64748B]">
                    Preventive control: {act.preventive_action}
                  </p>
                )}
                <div className="mt-3 flex flex-wrap items-center gap-4 caption-4 text-[#64748B]">
                  <span>Owner: {act.owner}</span>
                  <span>Target date: {act.due_date}</span>
                  {act.verification_notes && <span>Notes: {act.verification_notes}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
