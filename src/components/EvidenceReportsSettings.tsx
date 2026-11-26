import React, { useState } from 'react';
import {
  Fingerprint,
  UploadSimple,
  DownloadSimple,
  FilePdf,
  FileXls,
  CheckCircle,
  LockOpen,
  UserPlus,
  Database,
  ShieldCheck,
} from '@phosphor-icons/react';
import { api } from '../api';
import type { AuthUser, WorkspaceSnapshot } from '../types';

export const EvidenceVaultView: React.FC<{
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  onRefresh: () => void;
}> = ({ data, user, token, onRefresh }) => {
  const [title, setTitle] = useState('');
  const [entityType, setEntityType] = useState('Audit');
  const [auditId, setAuditId] = useState(data.audits[0]?.audit_id || 'AUD-2026-001');
  const [controlId, setControlId] = useState('A.8.5');
  const [notes, setNotes] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [feedback, setFeedback] = useState<{ ok: boolean; msg: string } | null>(null);

  const canUpload =
    user.role === 'Admin' || user.role === 'Auditor' || user.role === 'Risk Owner';

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setFeedback({ ok: false, msg: 'Select an evidence file under 20 MB before uploading.' });
      return;
    }
    setUploading(true);
    setFeedback(null);
    try {
      const fd = new FormData();
      fd.append('title', title.trim() || file.name);
      fd.append('entity_type', entityType);
      fd.append('entity_id', entityType === 'Control' ? controlId : auditId);
      fd.append('audit_id', auditId);
      fd.append('control_id', controlId);
      fd.append('notes', notes);
      fd.append('file', file);
      await api.uploadEvidence(fd, token);
      setTitle('');
      setNotes('');
      setFile(null);
      setFeedback({
        ok: true,
        msg: 'Evidence uploaded and SHA 256 digest stored in SQLite.',
      });
      onRefresh();
    } catch (err) {
      setFeedback({
        ok: false,
        msg: err instanceof Error ? err.message : 'Upload failed.',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleVerifyHash = async (evidenceId: string) => {
    try {
      const res = await api.verifyEvidence(evidenceId, token);
      setFeedback({
        ok: res.matches,
        msg: res.matches
          ? `Integrity verified for ${evidenceId}. Disk SHA 256 matches ${res.actual_sha256.slice(0, 20)}...`
          : `Hash mismatch detected for ${evidenceId} (${res.status}).`,
      });
      onRefresh();
    } catch (err) {
      setFeedback({ ok: false, msg: err instanceof Error ? err.message : 'Verification failed.' });
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {feedback && (
        <div
          className={`rounded-xl border px-4 py-3 body-5 ${
            feedback.ok
              ? 'border-[#A7F3D0] bg-[#ECFDF5] text-[#065F46]'
              : 'border-[#FECACA] bg-[#FEF2F2] text-[#991B1B]'
          }`}
        >
          {feedback.msg}
        </div>
      )}

      {canUpload && (
        <form
          onSubmit={handleUpload}
          className="rounded-2xl border border-[#E2E8F0] bg-white p-6"
        >
          <div className="flex items-center gap-2">
            <UploadSimple size={20} className="text-[#2563EB]" weight="bold" />
            <h2 className="title-2 text-[#0F172A]">
              Upload audit evidence artefact (automatic SHA 256 & 20 MB cap)
            </h2>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-4">
            <div className="sm:col-span-2">
              <label className="caption-3 block text-[#475569]">Evidence title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="FIDO2 Enrollment Verification Log"
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Audit ID</label>
              <select
                value={auditId}
                onChange={(e) => setAuditId(e.target.value)}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
              >
                {data.audits.map((a) => (
                  <option key={a.audit_id} value={a.audit_id}>
                    {a.audit_id}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Annex A control</label>
              <input
                type="text"
                value={controlId}
                onChange={(e) => setControlId(e.target.value)}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <label className="caption-3 block text-[#475569]">Entity category</label>
              <select
                value={entityType}
                onChange={(e) => setEntityType(e.target.value)}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
              >
                <option value="Audit">Audit</option>
                <option value="Control">Control</option>
                <option value="Finding">Finding</option>
                <option value="CAPA">CAPA</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="caption-3 block text-[#475569]">
                Select file (PDF, TXT, CSV, JSON, PNG, JPG, XLSX, DOCX)
              </label>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-[#F8FAFC] px-3 py-1.5"
              />
            </div>
          </div>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Chain of custody or sampling notes..."
            className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
          />
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              disabled={uploading}
              className="btn-main button-sm inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
            >
              <Fingerprint size={18} />
              {uploading ? 'Hashing & storing...' : 'Compute SHA 256 & store evidence'}
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 gap-4">
        {data.evidence.map((ev) => (
          <div key={ev.evidence_id} className="rounded-2xl border border-[#E2E8F0] bg-white p-5">
            <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="caption-3 font-mono rounded bg-[#EFF6FF] px-2 py-0.5 text-[#2563EB]">
                    {ev.evidence_id}
                  </span>
                  <span className="caption-3 rounded bg-[#F1F5F9] px-2 py-0.5 text-[#334155]">
                    {ev.entity_type}: {ev.entity_id}
                  </span>
                  {ev.control_id && (
                    <span className="caption-3 font-mono text-[#475569]">{ev.control_id}</span>
                  )}
                  <span
                    className={`caption-3 rounded-full px-2.5 py-0.5 ${
                      ev.verified_status === 'Verified'
                        ? 'bg-[#ECFDF5] text-[#065F46]'
                        : 'bg-[#FEF2F2] text-[#991B1B]'
                    }`}
                  >
                    {ev.verified_status}
                  </span>
                </div>
                <h3 className="title-2 mt-2 text-[#0F172A]">{ev.title}</h3>
                <p className="caption-4 mt-1 font-mono break-all text-[#64748B]">
                  SHA-256: {ev.sha256_hash}
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-4 caption-4 text-[#475569]">
                  <span>File: {ev.file_name}</span>
                  <span>Size: {ev.file_size_bytes.toLocaleString()} bytes</span>
                  <span>MIME: {ev.mime_type}</span>
                  <span>Uploaded by: {ev.uploaded_by}</span>
                </div>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleVerifyHash(ev.evidence_id)}
                  className="btn-main button-xsm inline-flex items-center gap-1 rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A] hover:bg-[#F8FAFC]"
                >
                  <Fingerprint size={15} />
                  Re-verify hash
                </button>
                <a
                  href={`/api/evidence/${encodeURIComponent(ev.evidence_id)}/download`}
                  className="btn-main button-xsm inline-flex items-center gap-1 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
                >
                  <DownloadSimple size={15} />
                  Download
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const ReportsCenterView: React.FC<{
  data: WorkspaceSnapshot;
}> = ({ data }) => {
  const [selectedAuditId, setSelectedAuditId] = useState(
    data.audits[0]?.audit_id || 'AUD-2026-001'
  );

  const selectedAudit =
    data.audits.find((a) => a.audit_id === selectedAuditId) || data.audits[0];
  const auditTests = data.tests.filter((t) => t.audit_id === selectedAudit?.audit_id);
  const auditFindings = data.findings.filter((f) => f.audit_id === selectedAudit?.audit_id);
  const critFindings = auditFindings.filter((f) => f.severity === 'Critical').length;

  return (
    <div className="flex flex-col gap-6">
      {/* Top Export Controls */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-[#E2E8F0] bg-white p-6 sm:flex-row sm:items-center">
        <div className="flex flex-wrap items-center gap-3">
          <label htmlFor="report-audit-select" className="title-4 text-[#0F172A]">
            Select audit report:
          </label>
          <select
            id="report-audit-select"
            value={selectedAudit?.audit_id || ''}
            onChange={(e) => setSelectedAuditId(e.target.value)}
            className="body-5 rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
          >
            {data.audits.map((a) => (
              <option key={a.audit_id} value={a.audit_id}>
                {a.audit_id} · {a.title}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {selectedAudit && (
            <a
              href={`/api/reports/audit/${encodeURIComponent(selectedAudit.audit_id)}/pdf`}
              target="_blank"
              rel="noreferrer"
              className="btn-main button-sm inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
            >
              <FilePdf size={18} weight="fill" />
              Download PDF Report
            </a>
          )}
          <a
            href="/api/reports/workbook.xlsx"
            className="btn-main button-sm inline-flex items-center gap-2 rounded-lg bg-[#059669] text-white hover:bg-[#047857]"
          >
            <FileXls size={18} weight="fill" />
            Export 9-Sheet Excel Workbook
          </a>
        </div>
      </div>

      {/* Live Report Preview matching Figure 4 */}
      {selectedAudit && (
        <div className="mx-auto w-full max-w-4xl overflow-hidden rounded-2xl border border-[#CBD5E1] bg-white">
          <div className="flex items-center justify-between border-b-4 border-[#2563EB] bg-[#0F172A] px-8 py-4 text-white">
            <div className="flex items-center gap-2">
              <ShieldCheck size={22} className="text-[#60A5FA]" weight="fill" />
              <span className="title-4">Professional Security Audit Report</span>
            </div>
            <span className="caption-3 font-mono text-[#93C5FD]">
              {selectedAudit.record_type === 'DEMO' ? 'ILLUSTRATIVE DEMO' : 'CONFIDENTIAL'}
            </span>
          </div>

          <div className="p-8">
            <div className="flex items-center gap-3">
              <span className="h-6 w-1.5 rounded bg-[#2563EB]" />
              <h2 className="heading-6 text-[#0F172A]">1. Executive Summary</h2>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-6 sm:grid-cols-2">
              <div>
                <div className="caption-3 uppercase text-[#64748B]">Audit title</div>
                <div className="title-3 mt-0.5 text-[#0F172A]">{selectedAudit.title}</div>
                <div className="caption-3 mt-4 uppercase text-[#64748B]">Organization</div>
                <div className="body-5 mt-0.5 text-[#334155]">{selectedAudit.organization}</div>
                <div className="caption-3 mt-4 uppercase text-[#64748B]">Approval status</div>
                <div className="body-5 mt-0.5 text-[#065F46]">
                  {selectedAudit.approval_status} (v{selectedAudit.report_version})
                  {selectedAudit.approved_by ? ` · Signed by ${selectedAudit.approved_by}` : ''}
                </div>
              </div>
              <div>
                <div className="caption-3 uppercase text-[#64748B]">Audit type</div>
                <div className="title-3 mt-0.5 text-[#0F172A]">{selectedAudit.audit_type}</div>
                <div className="caption-3 mt-4 uppercase text-[#64748B]">Lead auditor</div>
                <div className="body-5 mt-0.5 text-[#334155]">{selectedAudit.lead_auditor}</div>
                <div className="caption-3 mt-4 uppercase text-[#64748B]">Created by</div>
                <div className="body-5 mt-0.5 text-[#334155]">{selectedAudit.created_by}</div>
              </div>
            </div>

            {/* 4 Colored Metric Boxes matching Figure 4 */}
            <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-xl bg-[#2563EB] p-5 text-center text-white">
                <div className="heading-4 font-mono">{auditTests.length}</div>
                <div className="caption-4 mt-1 text-[#DBEAFE]">Total Controls</div>
              </div>
              <div className="rounded-xl bg-[#DC2626] p-5 text-center text-white">
                <div className="heading-4 font-mono">{auditFindings.length}</div>
                <div className="caption-4 mt-1 text-[#FEE2E2]">Total Findings</div>
              </div>
              <div className="rounded-xl bg-[#7F1D1D] p-5 text-center text-white">
                <div className="heading-4 font-mono">{critFindings}</div>
                <div className="caption-4 mt-1 text-[#FECACA]">Critical Findings</div>
              </div>
              <div className="rounded-xl bg-[#D97706] p-5 text-center text-white">
                <div className="heading-4 font-mono">
                  {typeof selectedAudit.compliance === 'number'
                    ? `${Math.round(selectedAudit.compliance)}%`
                    : 'N/A'}
                </div>
                <div className="caption-4 mt-1 text-[#FEF3C7]">Compliance Score</div>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-4 rounded-xl bg-[#F8FAFC] p-4 sm:grid-cols-2">
              <div>
                <div className="caption-3 uppercase text-[#64748B]">Audit period</div>
                <div className="body-5 mt-0.5 font-mono text-[#0F172A]">
                  {selectedAudit.start_date || selectedAudit.audit_date} →{' '}
                  {selectedAudit.end_date || selectedAudit.audit_date}
                </div>
              </div>
              <div>
                <div className="caption-3 uppercase text-[#64748B]">Audit team</div>
                <div className="body-5 mt-0.5 text-[#0F172A]">
                  {selectedAudit.audit_team || selectedAudit.lead_auditor}
                </div>
              </div>
            </div>

            <div className="mt-8 flex items-center gap-3">
              <span className="h-6 w-1.5 rounded bg-[#2563EB]" />
              <h2 className="heading-6 text-[#0F172A]">2. Scope & Objectives</h2>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-[#BFDBFE] bg-[#F8FAFC] p-5">
                <div className="caption-3 uppercase text-[#2563EB]">Scope</div>
                <p className="body-6 mt-2 text-[#334155]">{selectedAudit.scope}</p>
              </div>
              <div className="rounded-xl border border-[#BFDBFE] bg-[#F8FAFC] p-5">
                <div className="caption-3 uppercase text-[#2563EB]">Objectives</div>
                <p className="body-6 mt-2 text-[#334155]">{selectedAudit.objectives}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const UserManagementView: React.FC<{
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  onRefresh: () => void;
}> = ({ data, user, token, onRefresh }) => {
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('Auditor');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const isAdmin = user.role === 'Admin';

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createUser(
        { username, full_name: fullName, email, role, password },
        token
      );
      setUsername('');
      setFullName('');
      setEmail('');
      setPassword('');
      setMsg({ ok: true, text: 'Provisioned salted scrypt user account.' });
      onRefresh();
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : 'Creation failed.' });
    }
  };

  const handleUnlock = async (uname: string) => {
    try {
      await api.unlockUser(uname, token);
      setMsg({ ok: true, text: `Cleared lockout state for ${uname}.` });
      onRefresh();
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : 'Unlock failed.' });
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {msg && (
        <div
          className={`rounded-xl border px-4 py-3 body-5 ${
            msg.ok
              ? 'border-[#A7F3D0] bg-[#ECFDF5] text-[#065F46]'
              : 'border-[#FECACA] bg-[#FEF2F2] text-[#991B1B]'
          }`}
        >
          {msg.text}
        </div>
      )}

      {isAdmin && (
        <form
          onSubmit={handleCreate}
          className="rounded-2xl border border-[#E2E8F0] bg-white p-6"
        >
          <div className="flex items-center gap-2">
            <UserPlus size={20} className="text-[#2563EB]" weight="bold" />
            <h2 className="title-2 text-[#0F172A]">
              Provision role account (scrypt N=16384 salted KDF)
            </h2>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-5">
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              className="body-5 rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Full name"
              className="body-5 rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="body-5 rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="body-5 rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
            >
              <option value="Auditor">Auditor</option>
              <option value="Risk Owner">Risk Owner</option>
              <option value="Viewer">Viewer</option>
              <option value="Admin">Admin</option>
            </select>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min 10 chars + U/l/digit"
              className="body-5 rounded-lg border border-[#CBD5E1] px-3 py-2"
            />
          </div>
          <div className="mt-3 flex justify-end">
            <button
              type="submit"
              className="btn-main button-sm rounded-lg bg-[#2563EB] text-white"
            >
              Create account
            </button>
          </div>
        </form>
      )}

      <div className="overflow-x-auto rounded-2xl border border-[#E2E8F0] bg-white">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC] caption-3 text-[#475569]">
              <th className="p-4">User</th>
              <th className="p-4">Role</th>
              <th className="p-4">Failed Attempts</th>
              <th className="p-4">Lockout Window</th>
              <th className="p-4">Last Login</th>
              {isAdmin && <th className="p-4">Security Action</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F1F5F9] body-5">
            {data.users.map((u) => (
              <tr key={u.user_id}>
                <td className="p-4">
                  <div className="title-4 text-[#0F172A]">{u.full_name}</div>
                  <div className="caption-4 font-mono text-[#64748B]">
                    {u.username} · {u.email}
                  </div>
                </td>
                <td className="p-4">
                  <span className="caption-3 rounded-full bg-[#EFF6FF] px-2.5 py-0.5 text-[#1E40AF]">
                    {u.role}
                  </span>
                </td>
                <td className="p-4 font-mono">{u.failed_attempts} / 5</td>
                <td className="p-4 caption-4 font-mono text-[#991B1B]">
                  {u.locked_until || 'Unlocked'}
                </td>
                <td className="p-4 caption-4 font-mono text-[#64748B]">
                  {u.last_login || 'Never'}
                </td>
                {isAdmin && (
                  <td className="p-4">
                    <button
                      type="button"
                      onClick={() => handleUnlock(u.username)}
                      className="btn-main button-xsm inline-flex items-center gap-1 rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A]"
                    >
                      <LockOpen size={14} />
                      Reset lockout
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const SettingsAndAuditLogView: React.FC<{
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  includeDemo: boolean;
  onToggleDemo: (val: boolean) => void;
  onRefresh: () => void;
}> = ({ data, user, token, includeDemo, onToggleDemo, onRefresh }) => {
  const [statusMsg, setStatusMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const isAdmin = user.role === 'Admin';

  const handleCsvImport = async (file: File | null) => {
    if (!file) return;
    try {
      const res = await api.importAuditsCsv(file, token);
      setStatusMsg({
        ok: true,
        text: `Imported ${res.imported} audit(s); skipped ${res.skipped} existing IDs.`,
      });
      onRefresh();
    } catch (err) {
      setStatusMsg({ ok: false, text: err instanceof Error ? err.message : 'Import failed.' });
    }
  };

  const handleBackupCheck = async (file: File | null) => {
    if (!file) return;
    try {
      const res = await api.verifyBackupJson(file);
      setStatusMsg({
        ok: res.valid,
        text: res.valid
          ? `Backup manifest verified! SHA-256 matches ${res.actual_sha256.slice(0, 24)}...`
          : 'Manifest SHA-256 verification failed.',
      });
    } catch (err) {
      setStatusMsg({ ok: false, text: err instanceof Error ? err.message : 'Invalid backup.' });
    }
  };

  const handleDemoAction = async (mode: 'restore' | 'remove') => {
    try {
      if (mode === 'restore') {
        const res = await api.restoreDemo(token);
        setStatusMsg({ ok: true, text: `Restored ${res.restored} missing DEMO record(s).` });
      } else {
        const res = await api.removeDemo(token);
        setStatusMsg({
          ok: true,
          text: `Removed ${res.removed} DEMO record(s). USER records preserved.`,
        });
      }
      onRefresh();
    } catch (err) {
      setStatusMsg({ ok: false, text: err instanceof Error ? err.message : 'Action failed.' });
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {statusMsg && (
        <div
          className={`rounded-xl border px-4 py-3 body-5 ${
            statusMsg.ok
              ? 'border-[#A7F3D0] bg-[#ECFDF5] text-[#065F46]'
              : 'border-[#FECACA] bg-[#FEF2F2] text-[#991B1B]'
          }`}
        >
          {statusMsg.text}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
          <div className="flex items-center gap-2">
            <Database size={20} className="text-[#2563EB]" weight="duotone" />
            <h2 className="title-2 text-[#0F172A]">Workspace & demo data separation</h2>
          </div>
          <p className="caption-2 mt-1 text-[#64748B]">
            Toggle illustrative DEMO records out of views or safely restore/purge them without touching USER records.
          </p>
          <label className="mt-4 flex items-center gap-3 body-5 text-[#0F172A]">
            <input
              type="checkbox"
              checked={includeDemo}
              onChange={(e) => onToggleDemo(e.target.checked)}
              className="h-4 w-4 rounded border-[#CBD5E1]"
            />
            Include illustrative DEMO records in workspace metrics
          </label>

          {isAdmin && (
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => handleDemoAction('restore')}
                className="btn-main button-xsm rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A] hover:bg-[#F8FAFC]"
              >
                Restore missing DEMO records
              </button>
              <button
                type="button"
                onClick={() => handleDemoAction('remove')}
                className="btn-main button-xsm rounded-lg border border-[#FECACA] bg-[#FEF2F2] text-[#991B1B]"
              >
                Remove DEMO records (keep USER)
              </button>
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
          <h2 className="title-2 text-[#0F172A]">
            Append-only CSV import & verified JSON backup
          </h2>
          <div className="mt-4 flex flex-col gap-3">
            <div>
              <span className="caption-3 block text-[#475569]">
                Import Audit CSV (audit_id, title, department, status, audit_date)
              </span>
              <input
                type="file"
                accept=".csv"
                disabled={!isAdmin}
                onChange={(e) => handleCsvImport(e.target.files?.[0] || null)}
                className="body-6 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-1.5"
              />
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[#F1F5F9] pt-3">
              <a
                href="/api/backup/json"
                className="btn-main button-xsm inline-flex items-center gap-1.5 rounded-lg bg-[#0F172A] text-white"
              >
                <DownloadSimple size={15} />
                Download Verified JSON Backup
              </a>
              <label className="caption-3 cursor-pointer rounded-lg border border-[#CBD5E1] px-3 py-1.5 text-[#0F172A] hover:bg-[#F8FAFC]">
                Dry-run verify backup JSON
                <input
                  type="file"
                  accept=".json"
                  className="hidden"
                  onChange={(e) => handleBackupCheck(e.target.files?.[0] || null)}
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Tamper-Evident Hash-Chained Audit Trail */}
      <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 className="title-2 text-[#0F172A]">
              Tamper evident SHA 256 hash chained audit trail
            </h2>
            <p className="caption-2 text-[#64748B]">
              Every authentication, workpaper update, evidence hash, and report sign off is cryptographically chained.
            </p>
          </div>
          <span
            className={`caption-3 inline-flex items-center gap-1.5 rounded-full px-3 py-1 ${
              data.log_chain.valid
                ? 'bg-[#ECFDF5] text-[#065F46]'
                : 'bg-[#FEF2F2] text-[#991B1B]'
            }`}
          >
            <CheckCircle size={15} weight="fill" />
            {data.log_chain.valid
              ? `Chain intact (${data.log_chain.checked_entries} links)`
              : 'Chain broken'}
          </span>
        </div>

        <div className="mt-4 max-h-96 overflow-y-auto rounded-xl border border-[#E2E8F0]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC] caption-3 text-[#475569]">
                <th className="p-3">#</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Actor & Role</th>
                <th className="p-3">Action</th>
                <th className="p-3">Target</th>
                <th className="p-3">Entry Hash (SHA-256)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9] caption-4">
              {data.audit_logs.map((log) => (
                <tr key={log.log_id}>
                  <td className="p-3 font-mono text-[#64748B]">{log.log_id}</td>
                  <td className="p-3 font-mono text-[#475569]">{log.timestamp}</td>
                  <td className="p-3">
                    <span className="font-semibold text-[#0F172A]">{log.actor}</span>{' '}
                    <span className="text-[#64748B]">({log.role})</span>
                  </td>
                  <td className="p-3 font-mono text-[#2563EB]">{log.action}</td>
                  <td className="p-3">
                    {log.entity_type}:{log.entity_id} — {log.details}
                  </td>
                  <td className="p-3 font-mono text-[#64748B]">
                    {log.entry_hash.slice(0, 16)}...
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
