import React from 'react';
import {
  ShieldCheck,
  Warning,
  TrendUp,
  CheckCircle,
  ArrowRight,
  Pulse,
} from '@phosphor-icons/react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import type { WorkspaceSnapshot } from '../types';

interface DashboardViewProps {
  data: WorkspaceSnapshot;
  onSelectAudit: (auditId: string) => void;
  onViewAllAudits: () => void;
  onNewAudit: () => void;
}

const SEVERITY_COLORS: Record<string, string> = {
  Critical: '#7F1D1D',
  High: '#DC2626',
  Medium: '#D97706',
  Low: '#2563EB',
};

export const DashboardView: React.FC<DashboardViewProps> = ({
  data,
  onSelectAudit,
  onViewAllAudits,
  onNewAudit,
}) => {
  const totalAudits = data.audits.length;
  const activeAudits = data.audits.filter((a) => a.status === 'In Progress').length;
  const completedAudits = data.audits.filter(
    (a) => a.status === 'Completed' || a.status === 'Closed'
  ).length;
  const planningAudits = data.audits.filter((a) => a.status === 'Planned').length;

  const totalFindings = data.findings.length;
  const openFindings = data.findings.filter(
    (f) => f.status !== 'Resolved' && f.status !== 'Closed'
  ).length;

  const scoredAudits = data.audits.filter((a) => typeof a.compliance === 'number');
  const avgCompliance =
    scoredAudits.length > 0
      ? Math.round(
          scoredAudits.reduce((acc, a) => acc + (a.compliance || 0), 0) / scoredAudits.length
        )
      : 0;

  const compliantTests = data.tests.filter((t) => t.status === 'Compliant').length;
  const nonCompliantTests = data.tests.filter((t) => t.status === 'Non-Compliant').length;
  const partialTests = data.tests.filter((t) => t.status === 'Partially Compliant').length;
  const naTests = data.tests.filter((t) => t.status === 'Not Applicable').length;
  const totalTests = Math.max(1, data.tests.length);

  if (totalAudits === 0) {
    return (
      <div className="rounded-2xl border border-[#E2E8F0] bg-white p-10 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-[#EFF6FF] text-[#2563EB]">
          <ShieldCheck size={28} weight="fill" />
        </div>
        <h2 className="heading-5 mt-4 text-[#0F172A]">Your audit workspace is empty</h2>
        <p className="body-5 mx-auto mt-2 max-w-md text-[#475569]">
          Create your first ISO 27001 audit container, import a CSV register in Settings, or turn on
          illustrative demo records to explore preloaded controls and reports.
        </p>
        <button
          type="button"
          onClick={onNewAudit}
          className="btn-main button-md mt-6 inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
        >
          Create first audit
          <ArrowRight size={18} />
        </button>
      </div>
    );
  }

  const barData = data.audits.map((a) => ({
    name: a.title.length > 22 ? `${a.title.slice(0, 22)}...` : a.title,
    score: Math.round(a.compliance ?? 0),
    fill:
      (a.compliance ?? 0) >= 75
        ? '#059669'
        : (a.compliance ?? 0) >= 60
        ? '#D97706'
        : '#DC2626',
  }));

  const sevCounts = ['Critical', 'High', 'Medium', 'Low']
    .map((sev) => ({
      name: sev,
      value: data.findings.filter((f) => f.severity === sev).length,
      color: SEVERITY_COLORS[sev],
    }))
    .filter((item) => item.value > 0);

  return (
    <div className="flex flex-col gap-6">
      {/* KPI Cards matching Figure 1 */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
          <div className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#EFF6FF] text-[#2563EB]">
              <ShieldCheck size={22} weight="duotone" />
            </div>
            <div>
              <div className="caption-1 text-[#64748B]">Total audits</div>
              <div className="heading-5 mt-1 font-mono text-[#0F172A]">{totalAudits}</div>
              <div className="caption-4 mt-1 text-[#64748B]">{activeAudits} active</div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
          <div className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#FEF2F2] text-[#DC2626]">
              <Warning size={22} weight="duotone" />
            </div>
            <div>
              <div className="caption-1 text-[#64748B]">Total findings</div>
              <div className="heading-5 mt-1 font-mono text-[#0F172A]">{totalFindings}</div>
              <div className="caption-4 mt-1 text-[#64748B]">{openFindings} open</div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
          <div className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#ECFDF5] text-[#059669]">
              <TrendUp size={22} weight="duotone" />
            </div>
            <div>
              <div className="caption-1 text-[#64748B]">Avg compliance</div>
              <div className="heading-5 mt-1 font-mono text-[#0F172A]">{avgCompliance}%</div>
              <div className="caption-4 mt-1 text-[#64748B]">
                {compliantTests}/{data.tests.length} control tests
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
          <div className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#F5F3FF] text-[#6D28D9]">
              <CheckCircle size={22} weight="duotone" />
            </div>
            <div>
              <div className="caption-1 text-[#64748B]">Completed audits</div>
              <div className="heading-5 mt-1 font-mono text-[#0F172A]">{completedAudits}</div>
              <div className="caption-4 mt-1 text-[#64748B]">{planningAudits} in planning</div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row: Compliance by Audit & Risk Distribution */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="rounded-2xl border border-[#E2E8F0] bg-white p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="title-2 text-[#0F172A]">Compliance by audit</h2>
            <span className="caption-3 rounded-lg bg-[#F1F5F9] px-2.5 py-1 text-[#475569]">
              Score %
            </span>
          </div>
          <div className="mt-4 h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 16, left: 0, bottom: 8 }}>
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748B' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#64748B' }} />
                <Tooltip
                  formatter={(val: number) => [`${val}%`, 'Compliance']}
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #E2E8F0',
                    fontSize: '13px',
                  }}
                />
                <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                  {barData.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
          <h2 className="title-2 text-[#0F172A]">Finding severity distribution</h2>
          <div className="mt-4 h-52 w-full">
            {sevCounts.length === 0 ? (
              <div className="flex h-full items-center justify-center caption-1 text-[#64748B]">
                No findings logged
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sevCounts}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={52}
                    outerRadius={78}
                    paddingAngle={3}
                  >
                    {sevCounts.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="mt-2 flex flex-wrap justify-center gap-3">
            {sevCounts.map((s) => (
              <div key={s.name} className="flex items-center gap-1.5">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: s.color }}
                />
                <span className="caption-4 text-[#475569]">
                  {s.name} ({s.value})
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Bottom Row: Control Status Overview & Recent Audits */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <section className="rounded-2xl border border-[#E2E8F0] bg-white p-6 lg:col-span-2">
          <h2 className="title-2 text-[#0F172A]">Control status overview</h2>
          <div className="mt-5 flex flex-col gap-4">
            {[
              { label: 'Compliant', count: compliantTests, color: 'bg-[#059669]' },
              { label: 'Non-Compliant', count: nonCompliantTests, color: 'bg-[#DC2626]' },
              { label: 'Partially Compliant', count: partialTests, color: 'bg-[#D97706]' },
              { label: 'Not Applicable', count: naTests, color: 'bg-[#64748B]' },
            ].map((row) => (
              <div key={row.label}>
                <div className="flex items-center justify-between">
                  <span className="caption-1 text-[#334155]">{row.label}</span>
                  <span className="caption-3 font-mono text-[#0F172A]">{row.count}</span>
                </div>
                <div className="mt-1.5 h-2 w-full rounded-full bg-[#F1F5F9]">
                  <div
                    className={`h-2 rounded-full ${row.color}`}
                    style={{ width: `${Math.min(100, Math.round((row.count / totalTests) * 100))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-[#E2E8F0] bg-white p-6 lg:col-span-3">
          <div className="flex items-center justify-between">
            <h2 className="title-2 text-[#0F172A]">Recent audits</h2>
            <button
              type="button"
              onClick={onViewAllAudits}
              className="caption-3 inline-flex items-center gap-1 text-[#2563EB] hover:text-[#1D4ED8]"
            >
              View all
              <ArrowRight size={14} />
            </button>
          </div>
          <div className="mt-4 flex flex-col gap-3">
            {data.audits.slice(0, 4).map((aud) => (
              <button
                key={aud.audit_id}
                type="button"
                onClick={() => onSelectAudit(aud.audit_id)}
                className="flex w-full items-center justify-between rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4 text-left hover:border-[#93C5FD] transition-colors duration-300"
              >
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#EFF6FF] text-[#2563EB]">
                    <Pulse size={20} weight="bold" />
                  </span>
                  <div>
                    <div className="title-4 text-[#0F172A]">{aud.title}</div>
                    <div className="caption-4 mt-0.5 text-[#64748B]">
                      {aud.audit_type} · {aud.lead_auditor || aud.department}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {typeof aud.compliance === 'number' && (
                    <span className="caption-3 font-mono text-[#0F172A]">
                      {Math.round(aud.compliance)}%
                    </span>
                  )}
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
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};
