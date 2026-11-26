import React, { useState } from 'react';
import {
  CheckCircle,
  PencilSimple,
  ShieldWarning,
  Plus,
  BookOpen,
} from '@phosphor-icons/react';
import { api } from '../api';
import type { AuthUser, ControlSoARecord, WorkspaceSnapshot } from '../types';

export const ControlsSoAView: React.FC<{
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  onRefresh: () => void;
}> = ({ data, user, token, onRefresh }) => {
  const [domainFilter, setDomainFilter] = useState('All');
  const [subTab, setSubTab] = useState<'soa' | 'clauses'>('soa');
  const [editingCtrl, setEditingCtrl] = useState<ControlSoARecord | null>(null);
  const [banner, setBanner] = useState<{ ok: boolean; msg: string } | null>(null);

  const canEdit = user.role === 'Admin' || user.role === 'Auditor';
  const domains = ['All', ...Array.from(new Set(data.controls.map((c) => c.domain)))];

  const filtered = data.controls.filter(
    (c) => domainFilter === 'All' || c.domain === domainFilter
  );

  const applicableCount = data.controls.filter((c) => c.applicability === 'Applicable').length;
  const implementedCount = data.controls.filter(
    (c) => c.applicability === 'Applicable' && c.implementation_status === 'Implemented'
  ).length;

  const handleSaveCtrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingCtrl) return;
    try {
      await api.updateControl(
        editingCtrl.control_id,
        {
          applicability: editingCtrl.applicability,
          implementation_status: editingCtrl.implementation_status,
          justification: editingCtrl.justification,
          owner: editingCtrl.owner,
        },
        token
      );
      setEditingCtrl(null);
      setBanner({ ok: true, msg: `Updated SoA record for ${editingCtrl.control_id}.` });
      onRefresh();
    } catch (err) {
      setBanner({ ok: false, msg: err instanceof Error ? err.message : 'Update failed.' });
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5">
          <div className="caption-1 text-[#64748B]">Annex A controls</div>
          <div className="heading-5 mt-1 font-mono text-[#0F172A]">{data.controls.length}</div>
          <div className="caption-4 mt-1 text-[#64748B]">4 domains (ISO/IEC 27001:2022)</div>
        </div>
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5">
          <div className="caption-1 text-[#64748B]">Applicable in SoA</div>
          <div className="heading-5 mt-1 font-mono text-[#2563EB]">{applicableCount}</div>
          <div className="caption-4 mt-1 text-[#64748B]">
            {data.controls.length - applicableCount} excluded with justification
          </div>
        </div>
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5">
          <div className="caption-1 text-[#64748B]">Implemented coverage</div>
          <div className="heading-5 mt-1 font-mono text-[#059669]">
            {applicableCount ? Math.round((implementedCount / applicableCount) * 100) : 0}%
          </div>
          <div className="caption-4 mt-1 text-[#64748B]">
            {implementedCount} of {applicableCount} applicable controls
          </div>
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

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setSubTab('soa')}
            className={`btn-main button-sm rounded-lg ${
              subTab === 'soa'
                ? 'bg-[#0F172A] text-white'
                : 'border border-[#CBD5E1] bg-white text-[#475569]'
            }`}
          >
            Statement of Applicability (Annex A)
          </button>
          <button
            type="button"
            onClick={() => setSubTab('clauses')}
            className={`btn-main button-sm inline-flex items-center gap-1.5 rounded-lg ${
              subTab === 'clauses'
                ? 'bg-[#0F172A] text-white'
                : 'border border-[#CBD5E1] bg-white text-[#475569]'
            }`}
          >
            <BookOpen size={16} />
            Clauses 4 to 10 & 2024 Amendment
          </button>
        </div>

        {subTab === 'soa' && (
          <select
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
            aria-label="Filter by Annex A domain"
            className="body-5 rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
          >
            {domains.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        )}
      </div>

      {editingCtrl && (
        <form
          onSubmit={handleSaveCtrl}
          className="rounded-2xl border border-[#2563EB] bg-white p-6"
        >
          <h3 className="title-2 text-[#0F172A]">
            Update SoA control: {editingCtrl.control_id} · {editingCtrl.title}
          </h3>
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <label className="caption-3 block text-[#475569]">Applicability</label>
              <select
                value={editingCtrl.applicability}
                onChange={(e) =>
                  setEditingCtrl({ ...editingCtrl, applicability: e.target.value })
                }
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
              >
                <option value="Applicable">Applicable</option>
                <option value="Not Applicable">Not Applicable</option>
              </select>
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Implementation status</label>
              <select
                value={editingCtrl.implementation_status}
                onChange={(e) =>
                  setEditingCtrl({ ...editingCtrl, implementation_status: e.target.value })
                }
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
              >
                <option value="Implemented">Implemented</option>
                <option value="Partially Implemented">Partially Implemented</option>
                <option value="Not Implemented">Not Implemented</option>
                <option value="Not Applicable">Not Applicable</option>
              </select>
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Control owner</label>
              <input
                type="text"
                value={editingCtrl.owner}
                onChange={(e) => setEditingCtrl({ ...editingCtrl, owner: e.target.value })}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
          </div>
          <textarea
            rows={2}
            value={editingCtrl.justification}
            onChange={(e) => setEditingCtrl({ ...editingCtrl, justification: e.target.value })}
            placeholder="Justification for inclusion or exclusion..."
            className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
          />
          <div className="mt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setEditingCtrl(null)}
              className="btn-main button-xsm rounded-lg border border-[#CBD5E1]"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-main button-xsm rounded-lg bg-[#2563EB] text-white"
            >
              Save SoA update
            </button>
          </div>
        </form>
      )}

      {subTab === 'soa' ? (
        <div className="overflow-x-auto rounded-2xl border border-[#E2E8F0] bg-white">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC] caption-3 text-[#475569]">
                <th className="p-4">Control</th>
                <th className="p-4">Domain & Title</th>
                <th className="p-4">Applicability</th>
                <th className="p-4">Implementation</th>
                <th className="p-4">NIST / SOC 2</th>
                <th className="p-4">Owner & Justification</th>
                {canEdit && <th className="p-4">Action</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9] body-5">
              {filtered.map((c) => (
                <tr key={c.control_id} className="hover:bg-[#F8FAFC]">
                  <td className="p-4 font-mono font-semibold text-[#2563EB]">{c.control_id}</td>
                  <td className="p-4">
                    <div className="title-4 text-[#0F172A]">{c.title}</div>
                    <div className="caption-4 text-[#64748B]">{c.domain}</div>
                  </td>
                  <td className="p-4">
                    <span
                      className={`caption-3 rounded-full px-2.5 py-0.5 ${
                        c.applicability === 'Applicable'
                          ? 'bg-[#EFF6FF] text-[#1E40AF]'
                          : 'bg-[#F1F5F9] text-[#64748B]'
                      }`}
                    >
                      {c.applicability}
                    </span>
                  </td>
                  <td className="p-4">
                    <span
                      className={`caption-3 rounded-full px-2.5 py-0.5 ${
                        c.implementation_status === 'Implemented'
                          ? 'bg-[#ECFDF5] text-[#065F46]'
                          : c.implementation_status === 'Partially Implemented'
                          ? 'bg-[#FFFBEB] text-[#92400E]'
                          : c.implementation_status === 'Not Implemented'
                          ? 'bg-[#FEF2F2] text-[#991B1B]'
                          : 'bg-[#F1F5F9] text-[#64748B]'
                      }`}
                    >
                      {c.implementation_status}
                    </span>
                  </td>
                  <td className="p-4 font-mono caption-4 text-[#475569]">
                    {c.nist_csf} · {c.soc2}
                  </td>
                  <td className="p-4 max-w-xs">
                    <div className="caption-3 text-[#334155]">{c.owner}</div>
                    <div className="caption-4 text-[#64748B] line-clamp-2">{c.justification}</div>
                  </td>
                  {canEdit && (
                    <td className="p-4">
                      <button
                        type="button"
                        onClick={() => setEditingCtrl(c)}
                        className="caption-3 inline-flex items-center gap-1 text-[#2563EB] hover:underline"
                      >
                        <PencilSimple size={14} />
                        Edit
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {data.clauses.map((cl) => (
            <div key={cl.clause_id} className="rounded-2xl border border-[#E2E8F0] bg-white p-5">
              <div className="flex items-center justify-between">
                <span className="caption-3 font-mono rounded bg-[#EFF6FF] px-2.5 py-0.5 text-[#2563EB]">
                  Clause {cl.clause_id}
                </span>
                <span className="caption-4 text-[#64748B]">{cl.section}</span>
              </div>
              <h3 className="title-3 mt-2 text-[#0F172A]">{cl.title}</h3>
              <p className="body-6 mt-1.5 text-[#475569]">{cl.summary}</p>
              {cl.amendment_2024 && (
                <div className="mt-3 rounded-lg border border-[#A7F3D0] bg-[#ECFDF5] p-2.5 caption-4 text-[#065F46]">
                  {cl.amendment_2024}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const RisksAndFrameworksView: React.FC<{
  data: WorkspaceSnapshot;
  user: AuthUser;
  token: string;
  onRefresh: () => void;
}> = ({ data, user, token, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [title, setTitle] = useState('');
  const [asset, setAsset] = useState('');
  const [threat, setThreat] = useState('');
  const [likelihood, setLikelihood] = useState(3);
  const [impact, setImpact] = useState(4);
  const [treatment, setTreatment] = useState('Mitigate');
  const [controls, setControls] = useState('A.8.5, A.8.8');
  const [residual, setResidual] = useState(6);
  const [banner, setBanner] = useState<string | null>(null);

  const canManage = user.role === 'Admin' || user.role === 'Risk Owner';

  const handleSaveRisk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await api.saveRisk(
        {
          title: title.trim(),
          asset,
          threat,
          likelihood,
          impact,
          treatment,
          linked_controls: controls,
          residual_score: residual,
          owner: user.full_name,
          status: 'Treatment In Progress',
        },
        token
      );
      setShowAdd(false);
      setTitle('');
      setBanner('Risk scenario recorded.');
      onRefresh();
    } catch (err) {
      setBanner(err instanceof Error ? err.message : 'Could not save risk.');
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="title-1 text-[#0F172A]">Clause 6.1.2 Risk Register</h2>
          <p className="caption-1 text-[#64748B]">
            5x5 inherent risk scoring, treatment decisions, and residual risk tracking
          </p>
        </div>
        {canManage && (
          <button
            type="button"
            onClick={() => setShowAdd((v) => !v)}
            className="btn-main button-sm inline-flex items-center gap-1.5 rounded-lg bg-[#2563EB] text-white"
          >
            <Plus size={16} weight="bold" />
            Add risk scenario
          </button>
        )}
      </div>

      {banner && (
        <div className="rounded-xl border border-[#BFDBFE] bg-[#EFF6FF] px-4 py-2.5 caption-1 text-[#1E40AF]">
          {banner}
        </div>
      )}

      {showAdd && (
        <form
          onSubmit={handleSaveRisk}
          className="rounded-2xl border border-[#BFDBFE] bg-white p-6"
        >
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="sm:col-span-2">
              <label className="caption-3 block text-[#475569]">Risk title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Unauthorized Production API Key Exposure"
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Information asset</label>
              <input
                type="text"
                value={asset}
                onChange={(e) => setAsset(e.target.value)}
                placeholder="CI/CD Secrets Vault"
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Likelihood (1-5)</label>
              <input
                type="number"
                min={1}
                max={5}
                value={likelihood}
                onChange={(e) => setLikelihood(Number(e.target.value))}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Impact (1-5)</label>
              <input
                type="number"
                min={1}
                max={5}
                value={impact}
                onChange={(e) => setImpact(Number(e.target.value))}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Residual score (1-25)</label>
              <input
                type="number"
                min={1}
                max={25}
                value={residual}
                onChange={(e) => setResidual(Number(e.target.value))}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
            <div>
              <label className="caption-3 block text-[#475569]">Treatment</label>
              <select
                value={treatment}
                onChange={(e) => setTreatment(e.target.value)}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 py-2"
              >
                <option value="Mitigate">Mitigate</option>
                <option value="Accept">Accept</option>
                <option value="Transfer">Transfer</option>
                <option value="Avoid">Avoid</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="caption-3 block text-[#475569]">Linked Annex A controls</label>
              <input
                type="text"
                value={controls}
                onChange={(e) => setControls(e.target.value)}
                className="body-5 mt-1 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
              />
            </div>
          </div>
          <input
            type="text"
            value={threat}
            onChange={(e) => setThreat(e.target.value)}
            placeholder="Threat vector description..."
            className="body-5 mt-3 w-full rounded-lg border border-[#CBD5E1] px-3 py-2"
          />
          <div className="mt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAdd(false)}
              className="btn-main button-xsm rounded-lg border border-[#CBD5E1]"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-main button-xsm rounded-lg bg-[#2563EB] text-white"
            >
              Save risk
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {data.risks.map((r) => (
          <div key={r.risk_id} className="rounded-2xl border border-[#E2E8F0] bg-white p-5">
            <div className="flex items-center justify-between">
              <span className="caption-3 font-mono rounded bg-[#F1F5F9] px-2 py-0.5 text-[#334155]">
                {r.risk_id} · {r.asset}
              </span>
              <span
                className={`caption-3 font-mono rounded-full px-2.5 py-0.5 text-white ${
                  r.inherent_score >= 16 ? 'bg-[#7F1D1D]' : r.inherent_score >= 10 ? 'bg-[#D97706]' : 'bg-[#2563EB]'
                }`}
              >
                Inherent: {r.inherent_score}/25 → Residual: {r.residual_score}/25
              </span>
            </div>
            <h3 className="title-2 mt-2 text-[#0F172A]">{r.title}</h3>
            <p className="body-6 mt-1 text-[#475569]">{r.threat}</p>
            <div className="mt-3 flex flex-wrap items-center justify-between caption-4 text-[#64748B]">
              <span>Controls: {r.linked_controls}</span>
              <span>
                {r.treatment} · Owner: {r.owner}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
        <div className="flex items-center gap-2">
          <ShieldWarning size={20} className="text-[#D97706]" weight="fill" />
          <h3 className="title-2 text-[#0F172A]">
            Illustrative cross framework mappings (ISO 27001 · NIST CSF 2.0 · SOC 2)
          </h3>
        </div>
        <p className="caption-2 mt-1 text-[#64748B]">
          Illustrative reference mappings only — verify against authoritative obligations before operational reliance.
        </p>
        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          {data.requirements.map((req) => (
            <div
              key={req.req_id}
              className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4"
            >
              <div className="flex items-center justify-between">
                <span className="caption-3 text-[#2563EB]">
                  {req.framework} ({req.reference})
                </span>
                <span className="caption-4 rounded bg-white px-2 py-0.5 text-[#334155]">
                  {req.status}
                </span>
              </div>
              <p className="body-6 mt-1.5 text-[#0F172A]">{req.requirement_summary}</p>
              <div className="caption-4 mt-2 font-mono text-[#64748B]">
                Mapped Annex A: {req.mapped_controls}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
