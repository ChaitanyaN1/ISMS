import React, { useState } from 'react';
import {
  ArrowLeft,
  DownloadSimple,
  CheckCircle,
  XCircle,
  WarningCircle,
  PencilSimple,
  FileText,
  Plus,
  MagnifyingGlass,
  Trash,
  Stamp,
} from '@phosphor-icons/react';
import { api } from '../api';
import type {
  AuditRecord,
  AuthUser,
  ControlTestRecord,
  WorkspaceSnapshot,
} from '../types';

export const AuditProjectsList: React.FC<{
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  onSelectAudit: (auditId: string) => void;
  onNewAudit: () => void;
  onRefresh: () => void;
}> = ({ data, user, token, onSelectAudit, onNewAudit, onRefresh }) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [feedback, setFeedback] = useState<string | null>(null);

  const canManage = user.role === 'Admin' || user.role === 'Auditor';

  const filtered = data.audits.filter((a) => {
    const matchesSearch =
      !search.trim() ||
      a.title.toLowerCase().includes(search.toLowerCase()) ||
      a.audit_id.toLowerCase().includes(search.toLowerCase()) ||
      a.department.toLowerCase().includes(search.toLowerCase()) ||
      a.lead_auditor.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'All' || a.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleDelete = async (auditId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteAudit(auditId, token);
      setFeedback(`Removed audit ${auditId}.`);
      onRefresh();
    } catch (err) {
      setFeedback(err instanceof Error ? err.message : 'Delete failed.');
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div className="flex flex-1 items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlass
              size={18}
              className="pointer-events-none absolute top-2.5 left-3 text-[#64748B]"
            />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search audits by ID, title, department, or auditor"
              className="body-5 w-full rounded-lg border border-[#CBD5E1] bg-white py-2 pr-3 pl-9 text-[#0F172A]"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Filter by audit status"
            className="body-5 rounded-lg border border-[#CBD5E1] bg-white px-3 py-2 text-[#0F172A]"
          >
            <option value="All">All statuses</option>
            <option value="Planned">Planned</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Closed">Closed</option>
          </select>
        </div>

        {canManage && (
          <button
            type="button"
            onClick={onNewAudit}
            className="btn-main button-sm inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
          >
            <Plus size={16} weight="bold" />
            New audit project
          </button>
        )}
      </div>

      {feedback && (
        <div className="rounded-lg border border-[#BFDBFE] bg-[#EFF6FF] px-4 py-2 caption-1 text-[#1E40AF]">
          {feedback}
        </div>
      )}

      {filtered.length === 0 ? (
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-10 text-center caption-1 text-[#64748B]">
          No audit projects match your filter criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {filtered.map((aud) => {
            const testCount = data.tests.filter((t) => t.audit_id === aud.audit_id).length;
            const findingCount = data.findings.filter((f) => f.audit_id === aud.audit_id).length;
            return (
              <article
                key={aud.audit_id}
                onClick={() => onSelectAudit(aud.audit_id)}
                className="cursor-pointer rounded-2xl border border-[#E2E8F0] bg-white p-6 hover:border-[#60A5FA] transition-colors duration-300"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="caption-3 font-mono rounded bg-[#F1F5F9] px-2 py-0.5 text-[#334155]">
                      {aud.audit_id}
                    </span>
                    <span className="caption-3 rounded bg-[#EFF6FF] px-2 py-0.5 text-[#1E40AF]">
                      {aud.audit_type}
                    </span>
                    <span className="caption-4 rounded border border-[#E2E8F0] px-2 py-0.5 text-[#64748B]">
                      {aud.record_type}
                    </span>
                  </div>
                  <span
                    className={`caption-3 rounded-lg px-2.5 py-1 ${
                      aud.status === 'Completed'
                        ? 'bg-[#ECFDF5] text-[#065F46]'
                        : aud.status === 'In Progress'
                        ? 'bg-[#EFF6FF] text-[#1E40AF]'
                        : 'bg-[#FFFBEB] text-[#92400E]'
                    }`}
                  >
                    {aud.status}
                  </span>
                </div>

                <h3 className="title-1 mt-3 text-[#0F172A]">{aud.title}</h3>
                <p className="caption-2 mt-1 text-[#64748B]">
                  {aud.organization} · {aud.department} · Lead: {aud.lead_auditor || 'Unassigned'}
                </p>

                <p className="body-6 mt-3 line-clamp-2 text-[#475569]">
                  {aud.scope || 'Audit scope documented inside workpaper container.'}
                </p>

                <div className="mt-5 flex items-center justify-between border-t border-[#F1F5F9] pt-4">
                  <div className="flex items-center gap-4 caption-4 text-[#475569]">
                    <span>{testCount} controls</span>
                    <span>{findingCount} findings</span>
                    <span className="font-mono font-semibold text-[#0F172A]">
                      {typeof aud.compliance === 'number' ? `${Math.round(aud.compliance)}%` : 'N/A'}
                    </span>
                    <span>Sign-off: {aud.approval_status}</span>
                  </div>
                  {canManage && (
                    <button
                      type="button"
                      aria-label={`Delete ${aud.audit_id}`}
                      onClick={(e) => handleDelete(aud.audit_id, e)}
                      className="rounded-lg p-1.5 text-[#64748B] hover:bg-[#FEF2F2] hover:text-[#DC2626]"
                    >
                      <Trash size={16} />
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
};

export const NewAuditForm: React.FC<{
  user: AuthUser;
  token: string;
  onCreated: (auditId: string) => void;
  onCancel: () => void;
}> = ({ user, token, onCreated, onCancel }) => {
  const [title, setTitle] = useState('');
  const [organization, setOrganization] = useState('TechCorp International');
  const [department, setDepartment] = useState('Cloud & Platform Security');
  const [auditType, setAuditType] = useState('ISO 27001');
  const [status, setStatus] = useState('In Progress');
  const [auditDate, setAuditDate] = useState(new Date().toISOString().slice(0, 10));
  const [leadAuditor, setLeadAuditor] = useState(user.full_name);
  const [auditTeam, setAuditTeam] = useState(`${user.full_name}, Sarah Chen`);
  const [scope, setScope] = useState('');
  const [objectives, setObjectives] = useState('');
  const [seedControls, setSeedControls] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMsg('Validation failed. Enter an audit title before saving.');
      return;
    }
    setSaving(true);
    setErrorMsg(null);
    try {
      const res = (await api.saveAudit(
        {
          title: title.trim(),
          organization,
          department,
          audit_type: auditType,
          status,
          audit_date: auditDate,
          start_date: auditDate,
          end_date: auditDate,
          lead_auditor: leadAuditor,
          audit_team: auditTeam,
          scope,
          objectives,
          seed_default_controls: seedControls,
        },
        token
      )) as { audit: AuditRecord };
      onCreated(res.audit.audit_id);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Could not create audit.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl rounded-2xl border border-[#E2E8F0] bg-white p-8">
      <h2 className="heading-5 text-[#0F172A]">Create ISO 27001 audit container</h2>
      <p className="caption-1 mt-1 text-[#64748B]">
        Establish audit scope, criteria, lead auditor, and baseline Annex A control checklist.
      </p>

      {errorMsg && (
        <div className="mt-4 rounded-lg border border-[#FECACA] bg-[#FEF2F2] p-3 body-5 text-[#991B1B]">
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="title-4 block text-[#0F172A]">Audit title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="ISO 27001 Annual Surveillance Audit"
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
          </div>
          <div>
            <label className="title-4 block text-[#0F172A]">Organization</label>
            <input
              type="text"
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
          </div>
          <div>
            <label className="title-4 block text-[#0F172A]">Department</label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
          </div>
          <div>
            <label className="title-4 block text-[#0F172A]">Framework / type</label>
            <select
              value={auditType}
              onChange={(e) => setAuditType(e.target.value)}
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
            >
              <option value="ISO 27001">ISO 27001</option>
              <option value="SOC 2">SOC 2</option>
              <option value="Internal Audit">Internal Audit</option>
              <option value="Supplier Review">Supplier Review</option>
            </select>
          </div>
          <div>
            <label className="title-4 block text-[#0F172A]">Audit date</label>
            <input
              type="date"
              value={auditDate}
              onChange={(e) => setAuditDate(e.target.value)}
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
          </div>
          <div>
            <label className="title-4 block text-[#0F172A]">Lifecycle status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
            >
              <option value="Planned">Planned</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
            </select>
          </div>
          <div>
            <label className="title-4 block text-[#0F172A]">Lead auditor</label>
            <input
              type="text"
              value={leadAuditor}
              onChange={(e) => setLeadAuditor(e.target.value)}
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
          </div>
          <div>
            <label className="title-4 block text-[#0F172A]">Audit team</label>
            <input
              type="text"
              value={auditTeam}
              onChange={(e) => setAuditTeam(e.target.value)}
              className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
          </div>
        </div>

        <div>
          <label className="title-4 block text-[#0F172A]">ISMS audit scope</label>
          <textarea
            rows={3}
            value={scope}
            onChange={(e) => setScope(e.target.value)}
            placeholder="Define systems, cloud accounts, physical sites, and business units in scope..."
            className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
          />
        </div>

        <div>
          <label className="title-4 block text-[#0F172A]">Audit objectives</label>
          <textarea
            rows={3}
            value={objectives}
            onChange={(e) => setObjectives(e.target.value)}
            placeholder="Assess conformity with ISO/IEC 27001:2022 controls, verify evidence, and assign CAPA..."
            className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
          />
        </div>

        <label className="flex items-center gap-2 body-5 text-[#334155]">
          <input
            type="checkbox"
            checked={seedControls}
            onChange={(e) => setSeedControls(e.target.checked)}
            className="h-4 w-4 rounded border-[#CBD5E1]"
          />
          Preload 12 baseline Annex A control workpapers into checklist
        </label>

        <div className="mt-2 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="btn-main button-sm rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A]"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="btn-main button-sm rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
          >
            {saving ? 'Creating...' : 'Create audit & open checklist'}
          </button>
        </div>
      </form>
    </div>
  );
};

export const AuditDetailView: React.FC<{
  audit: AuditRecord;
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  onBack: () => void;
  onRefresh: () => void;
}> = ({ audit, data, user, token, onBack, onRefresh }) => {
  const [tab, setTab] = useState<'overview' | 'checklist' | 'findings' | 'evidence'>('checklist');
  const [editingTest, setEditingTest] = useState<ControlTestRecord | null>(null);
  const [addingControl, setAddingControl] = useState(false);
  const [newCtrlId, setNewCtrlId] = useState('A.5.1');
  const [newStatus, setNewStatus] = useState('Compliant');
  const [newSample, setNewSample] = useState(15);
  const [newNotes, setNewNotes] = useState('');
  const [newEvRef, setNewEvRef] = useState('');
  const [signStatus, setSignStatus] = useState(audit.approval_status || 'Draft');
  const [signVer, setSignVer] = useState(audit.report_version || '1.0');
  const [signNotes, setSignNotes] = useState(audit.approval_notes || '');
  const [banner, setBanner] = useState<{ ok: boolean; msg: string } | null>(null);

  const canEdit = user.role === 'Admin' || user.role === 'Auditor';

  const auditTests = data.tests.filter((t) => t.audit_id === audit.audit_id);
  const auditFindings = data.findings.filter((f) => f.audit_id === audit.audit_id);
  const auditEvidence = data.evidence.filter((ev) => ev.audit_id === audit.audit_id);

  const handleStatusChange = async (nextStatus: string) => {
    try {
      await api.saveAudit({ ...audit, status: nextStatus, seed_default_controls: false }, token);
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Status update failed.' });
    }
  };

  const handleSaveTestEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTest) return;
    try {
      await api.saveTest(editingTest as unknown as Record<string, unknown>, token);
      setEditingTest(null);
      setBanner({ ok: true, msg: 'Control workpaper saved and compliance score updated.' });
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Save failed.' });
    }
  };

  const handleAddControlTest = async (e: React.FormEvent) => {
    e.preventDefault();
    const ctrlMeta = data.controls.find((c) => c.control_id === newCtrlId);
    try {
      await api.saveTest(
        {
          audit_id: audit.audit_id,
          control_id: newCtrlId,
          control_title: ctrlMeta?.title || newCtrlId,
          domain: ctrlMeta?.domain || 'Organizational (5)',
          procedure: ctrlMeta?.description || '',
          sample_size: newSample,
          status: newStatus,
          auditor_notes: newNotes,
          evidence_ref: newEvRef,
        },
        token
      );
      setAddingControl(false);
      setNewNotes('');
      setNewEvRef('');
      setBanner({ ok: true, msg: `Added control ${newCtrlId} to checklist.` });
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Could not add control.' });
    }
  };

  const handleSignOff = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.approveReport(
        audit.audit_id,
        {
          approval_status: signStatus,
          report_version: signVer,
          approval_notes: signNotes,
        },
        token
      );
      setBanner({ ok: true, msg: `Report governance status updated to ${signStatus}.` });
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Sign-off rejected.' });
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header matching Figure 2 */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-[#E2E8F0] bg-white p-6 sm:flex-row sm:items-center">
        <div className="flex items-start gap-3">
          <button
            type="button"
            onClick={onBack}
            aria-label="Back to audit list"
            className="mt-1 rounded-lg border border-[#E2E8F0] p-2 text-[#475569] hover:bg-[#F8FAFC]"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="caption-3 rounded bg-[#F1F5F9] px-2.5 py-1 text-[#334155]">
                {audit.audit_type}
              </span>
              <select
                value={audit.status}
                disabled={!canEdit}
                onChange={(e) => handleStatusChange(e.target.value)}
                aria-label="Audit status"
                className="caption-3 rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1 text-[#0F172A]"
              >
                <option value="Planned">Planned</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Closed">Closed</option>
              </select>
              <span className="caption-3 rounded bg-[#ECFDF5] px-2.5 py-1 text-[#065F46]">
                Sign-off: {audit.approval_status} (v{audit.report_version})
              </span>
            </div>
            <h1 className="heading-5 mt-2 text-[#0F172A]">{audit.title}</h1>
            <p className="caption-1 mt-0.5 text-[#64748B]">
              {audit.organization} · Created by {audit.created_by} · Lead: {audit.lead_auditor}
            </p>
          </div>
        </div>

        <a
          href={`/api/reports/audit/${encodeURIComponent(audit.audit_id)}/pdf`}
          target="_blank"
          rel="noreferrer"
          className="btn-main button-sm inline-flex items-center gap-2 rounded-xl bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
        >
          <DownloadSimple size={18} weight="bold" />
          Export PDF Report
        </a>
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

      {/* Tabs matching Figure 2: Overview | Checklist (16) | Findings (5) | Evidence & Docs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-[#E2E8F0] pb-2">
        {[
          { id: 'overview', label: 'Overview', count: null },
          { id: 'checklist', label: 'Checklist', count: auditTests.length },
          { id: 'findings', label: 'Findings', count: auditFindings.length },
          { id: 'evidence', label: 'Evidence & Sign-Off', count: auditEvidence.length },
        ].map((t) => {
          const active = tab === t.id;
          return (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id as typeof tab)}
              className={`btn-main button-sm inline-flex items-center gap-2 rounded-lg ${
                active
                  ? 'bg-[#EFF6FF] text-[#2563EB]'
                  : 'text-[#475569] hover:bg-[#F1F5F9]'
              }`}
            >
              {t.label}
              {t.count !== null && (
                <span className="caption-3 rounded-full bg-white px-2 py-0.5 text-[#2563EB]">
                  {t.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* TAB: CHECKLIST (Matches Figure 2 control cards) */}
      {tab === 'checklist' && (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <span className="caption-1 text-[#64748B]">
              {auditTests.length} controls · Click Edit on any control to update status, sample size, or evidence
            </span>
            {canEdit && (
              <button
                type="button"
                onClick={() => setAddingControl((v) => !v)}
                className="btn-main button-sm inline-flex items-center gap-1.5 rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A] hover:bg-[#F8FAFC]"
              >
                <Plus size={15} weight="bold" />
                Add control test
              </button>
            )}
          </div>

          {addingControl && (
            <form
              onSubmit={handleAddControlTest}
              className="rounded-2xl border border-[#BFDBFE] bg-[#EFF6FF]/60 p-5"
            >
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
                <div>
                  <label className="caption-3 block text-[#1E3A8A]">Annex A Control</label>
                  <select
                    value={newCtrlId}
                    onChange={(e) => setNewCtrlId(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1.5"
                  >
                    {data.controls.map((c) => (
                      <option key={c.control_id} value={c.control_id}>
                        {c.control_id} · {c.title}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="caption-3 block text-[#1E3A8A]">Status</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1.5"
                  >
                    <option value="Compliant">Compliant</option>
                    <option value="Partially Compliant">Partially Compliant</option>
                    <option value="Non-Compliant">Non-Compliant</option>
                    <option value="Not Applicable">Not Applicable</option>
                  </select>
                </div>
                <div>
                  <label className="caption-3 block text-[#1E3A8A]">Sample size</label>
                  <input
                    type="number"
                    min={1}
                    value={newSample}
                    onChange={(e) => setNewSample(Number(e.target.value))}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1.5"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#1E3A8A]">Evidence ref</label>
                  <input
                    type="text"
                    value={newEvRef}
                    onChange={(e) => setNewEvRef(e.target.value)}
                    placeholder="evidence_doc.pdf"
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1.5"
                  />
                </div>
              </div>
              <input
                type="text"
                value={newNotes}
                onChange={(e) => setNewNotes(e.target.value)}
                placeholder="Auditor observation notes..."
                className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-1.5"
              />
              <div className="mt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setAddingControl(false)}
                  className="btn-main button-xsm rounded-lg border border-[#CBD5E1] bg-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-main button-xsm rounded-lg bg-[#2563EB] text-white"
                >
                  Save workpaper
                </button>
              </div>
            </form>
          )}

          {editingTest && (
            <form
              onSubmit={handleSaveTestEdit}
              className="rounded-2xl border border-[#2563EB] bg-white p-5"
            >
              <h3 className="title-3 text-[#0F172A]">
                Update workpaper: {editingTest.control_id} · {editingTest.control_title}
              </h3>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
                <div>
                  <label className="caption-3 block text-[#475569]">Assessment status</label>
                  <select
                    value={editingTest.status}
                    onChange={(e) => setEditingTest({ ...editingTest, status: e.target.value })}
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1.5"
                  >
                    <option value="Compliant">Compliant</option>
                    <option value="Partially Compliant">Partially Compliant</option>
                    <option value="Non-Compliant">Non-Compliant</option>
                    <option value="Not Applicable">Not Applicable</option>
                    <option value="Not Tested">Not Tested</option>
                  </select>
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Sample size</label>
                  <input
                    type="number"
                    min={1}
                    value={editingTest.sample_size}
                    onChange={(e) =>
                      setEditingTest({ ...editingTest, sample_size: Number(e.target.value) })
                    }
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-2.5 py-1.5"
                  />
                </div>
                <div>
                  <label className="caption-3 block text-[#475569]">Evidence filename</label>
                  <input
                    type="text"
                    value={editingTest.evidence_ref}
                    onChange={(e) =>
                      setEditingTest({ ...editingTest, evidence_ref: e.target.value })
                    }
                    className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-2.5 py-1.5"
                  />
                </div>
              </div>
              <textarea
                rows={2}
                value={editingTest.auditor_notes}
                onChange={(e) =>
                  setEditingTest({ ...editingTest, auditor_notes: e.target.value })
                }
                placeholder="Auditor test notes..."
                className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
              <div className="mt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setEditingTest(null)}
                  className="btn-main button-xsm rounded-lg border border-[#CBD5E1] bg-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-main button-xsm rounded-lg bg-[#2563EB] text-white"
                >
                  Update control status
                </button>
              </div>
            </form>
          )}

          {auditTests.map((t) => {
            const isComp = t.status === 'Compliant';
            const isNon = t.status === 'Non-Compliant';
            const isPart = t.status === 'Partially Compliant';
            return (
              <div
                key={t.test_id}
                className="rounded-2xl border border-[#E2E8F0] bg-white p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    {isComp ? (
                      <CheckCircle size={20} className="mt-0.5 shrink-0 text-[#059669]" weight="bold" />
                    ) : isNon ? (
                      <XCircle size={20} className="mt-0.5 shrink-0 text-[#DC2626]" weight="bold" />
                    ) : (
                      <WarningCircle size={20} className="mt-0.5 shrink-0 text-[#D97706]" weight="bold" />
                    )}
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="caption-3 font-mono rounded bg-[#EFF6FF] px-2 py-0.5 text-[#2563EB]">
                          {t.control_id}
                        </span>
                        <span className="title-4 text-[#475569]">{t.control_title}</span>
                        <span className="caption-4 text-[#94A3B8]">· Sample: {t.sample_size}</span>
                      </div>
                      <p className="body-5 mt-1.5 text-[#0F172A]">
                        {t.procedure || 'Verify control implementation and operating evidence.'}
                      </p>
                      <div className="mt-3 flex flex-wrap items-center gap-3">
                        <span
                          className={`caption-3 rounded-full px-2.5 py-0.5 ${
                            isComp
                              ? 'bg-[#ECFDF5] text-[#065F46]'
                              : isNon
                              ? 'bg-[#FEF2F2] text-[#991B1B]'
                              : isPart
                              ? 'bg-[#FFFBEB] text-[#92400E]'
                              : 'bg-[#F1F5F9] text-[#475569]'
                          }`}
                        >
                          {t.status}
                        </span>
                        {t.auditor_notes && (
                          <span className="caption-2 text-[#64748B]">
                            “{t.auditor_notes}”
                          </span>
                        )}
                        {t.evidence_ref && (
                          <span className="caption-3 inline-flex items-center gap-1 text-[#2563EB]">
                            <FileText size={14} />
                            {t.evidence_ref}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {canEdit && (
                    <button
                      type="button"
                      onClick={() => setEditingTest(t)}
                      className="caption-3 inline-flex shrink-0 items-center gap-1 rounded-lg px-2.5 py-1 text-[#2563EB] hover:bg-[#EFF6FF]"
                    >
                      <PencilSimple size={14} />
                      Edit
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* TAB: OVERVIEW */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
            <h3 className="title-2 text-[#0F172A]">Audit scope</h3>
            <p className="body-5 mt-2 text-[#475569]">{audit.scope || 'Not specified.'}</p>
            <h3 className="title-2 mt-6 text-[#0F172A]">Audit objectives</h3>
            <p className="body-5 mt-2 text-[#475569]">{audit.objectives || 'Not specified.'}</p>
          </div>
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
            <h3 className="title-2 text-[#0F172A]">Metadata & team</h3>
            <dl className="mt-4 grid grid-cols-2 gap-4 caption-1">
              <div>
                <dt className="text-[#64748B]">Audit ID</dt>
                <dd className="font-mono text-[#0F172A] mt-0.5">{audit.audit_id}</dd>
              </div>
              <div>
                <dt className="text-[#64748B]">Compliance score</dt>
                <dd className="font-mono text-[#0F172A] mt-0.5">
                  {typeof audit.compliance === 'number' ? `${audit.compliance}%` : 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-[#64748B]">Audit period</dt>
                <dd className="text-[#0F172A] mt-0.5">
                  {audit.start_date || audit.audit_date} → {audit.end_date || audit.audit_date}
                </dd>
              </div>
              <div>
                <dt className="text-[#64748B]">Audit team</dt>
                <dd className="text-[#0F172A] mt-0.5">{audit.audit_team || audit.lead_auditor}</dd>
              </div>
            </dl>
          </div>
        </div>
      )}

      {/* TAB: FINDINGS */}
      {tab === 'findings' && (
        <div className="flex flex-col gap-3">
          {auditFindings.length === 0 ? (
            <div className="rounded-2xl border border-[#E2E8F0] bg-white p-8 text-center caption-1 text-[#64748B]">
              No findings logged against this audit.
            </div>
          ) : (
            auditFindings.map((f) => (
              <div key={f.finding_id} className="rounded-2xl border border-[#E2E8F0] bg-white p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`caption-3 rounded-full px-2.5 py-0.5 text-white ${
                      f.severity === 'Critical'
                        ? 'bg-[#7F1D1D]'
                        : f.severity === 'High'
                        ? 'bg-[#DC2626]'
                        : 'bg-[#D97706]'
                    }`}
                  >
                    {f.severity}
                  </span>
                  <span className="caption-3 rounded bg-[#F1F5F9] px-2 py-0.5 text-[#334155]">
                    {f.status}
                  </span>
                  <span className="caption-3 font-mono text-[#2563EB]">{f.control_id}</span>
                </div>
                <h3 className="title-2 mt-2 text-[#0F172A]">{f.title}</h3>
                <p className="body-5 mt-1 text-[#475569]">{f.condition}</p>
                <p className="caption-1 mt-2 text-[#065F46]">
                  Recommendation: {f.recommendation}
                </p>
              </div>
            ))
          )}
        </div>
      )}

      {/* TAB: EVIDENCE & FORMAL REPORT SIGN-OFF */}
      {tab === 'evidence' && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
            <h3 className="title-2 text-[#0F172A]">SHA 256 verified evidence artefacts</h3>
            {auditEvidence.length === 0 ? (
              <p className="caption-1 mt-3 text-[#64748B]">
                No evidence files linked directly to this audit yet. Upload files in the Evidence Vault.
              </p>
            ) : (
              <div className="mt-4 flex flex-col gap-3">
                {auditEvidence.map((ev) => (
                  <div
                    key={ev.evidence_id}
                    className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="title-4 text-[#0F172A]">{ev.title}</span>
                      <span className="caption-3 rounded bg-[#ECFDF5] px-2 py-0.5 text-[#065F46]">
                        {ev.verified_status}
                      </span>
                    </div>
                    <div className="caption-4 mt-1 font-mono break-all text-[#64748B]">
                      SHA-256: {ev.sha256_hash}
                    </div>
                    <div className="mt-2 flex items-center justify-between caption-4 text-[#475569]">
                      <span>
                        {ev.file_name} ({ev.file_size_bytes} bytes)
                      </span>
                      <a
                        href={`/api/evidence/${encodeURIComponent(ev.evidence_id)}/download`}
                        className="text-[#2563EB] hover:underline"
                      >
                        Verified download
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <form
            onSubmit={handleSignOff}
            className="rounded-2xl border border-[#E2E8F0] bg-white p-6"
          >
            <div className="flex items-center gap-2">
              <Stamp size={22} className="text-[#2563EB]" weight="duotone" />
              <h3 className="title-2 text-[#0F172A]">Formal report approval sign off</h3>
            </div>
            <p className="caption-2 mt-1 text-[#64748B]">
              Separates workpaper preparation from management report sign off (Admin required for final Approved state).
            </p>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div>
                <label className="caption-3 block text-[#475569]">Approval state</label>
                <select
                  value={signStatus}
                  onChange={(e) => setSignStatus(e.target.value)}
                  className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
                >
                  <option value="Draft">Draft</option>
                  <option value="In Review">In Review</option>
                  <option value="Approved">Approved</option>
                  <option value="Changes Requested">Changes Requested</option>
                </select>
              </div>
              <div>
                <label className="caption-3 block text-[#475569]">Report version</label>
                <input
                  type="text"
                  value={signVer}
                  onChange={(e) => setSignVer(e.target.value)}
                  className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
                />
              </div>
            </div>
            <div className="mt-3">
              <label className="caption-3 block text-[#475569]">Sign off review notes</label>
              <textarea
                rows={2}
                value={signNotes}
                onChange={(e) => setSignNotes(e.target.value)}
                placeholder="Document review completion and sign off remarks..."
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
            {audit.approved_by && (
              <p className="caption-4 mt-2 text-[#065F46]">
                Signed off by {audit.approved_by} at {audit.approved_at}
              </p>
            )}
            <button
              type="submit"
              className="btn-main button-sm mt-4 rounded-lg bg-[#0F172A] text-white hover:bg-[#1E293B]"
            >
              Save sign off decision
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
