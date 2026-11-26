import React, { useEffect, useRef, useState } from 'react';
import {
  ShieldCheck,
  CheckCircle,
  FilePdf,
  LockKey,
  TreeStructure,
  ClipboardText,
  ArrowRight,
  CaretDown,
  List,
  X,
  Fingerprint,
  Scales,
  ChartBar,
} from '@phosphor-icons/react';

interface LandingPageProps {
  onOpenWorkspace: () => void;
  onSignInClick: () => void;
  onOpenPrivacy: () => void;
  onOpenTerms: () => void;
}

const TAGLINE_WORDS = [
  'Every',
  'ISO',
  '27001',
  'control',
  'test,',
  'SHA',
  '256',
  'evidence',
  'digest,',
  'nonconformity,',
  'and',
  'corrective',
  'action',
  'connected',
  'in',
  'one',
  'verifiable',
  'audit',
  'trail',
  'before',
  'management',
  'review.',
];

const FAQS = [
  {
    q: 'Does SecureAudit run locally without external cloud accounts?',
    a: 'Yes. All records, uploaded evidence files, salted scrypt credentials, and hash chained audit logs stay inside your local SQLite workspace with zero external cloud dependencies.',
  },
  {
    q: 'Which ISO 27001 controls and clauses are included in the reference catalogue?',
    a: 'The workspace includes Clauses 4 through 10 summaries, the 2024 climate action amendment notes, and 40 Annex A controls spanning Organizational, People, Physical, and Technological domains.',
  },
  {
    q: 'How does evidence file integrity verification work?',
    a: 'Every uploaded evidence file under 20 MB is validated by media type and hashed with SHA 256 at upload. Reviewers can verify the stored digest on demand and before every download.',
  },
  {
    q: 'How are user roles and login security enforced?',
    a: 'Four role scopes (Admin, Auditor, Risk Owner, Viewer) gate editing and sign off actions. Passwords use salted scrypt hashing and accounts lock for 15 minutes after 5 failed attempts.',
  },
  {
    q: 'Can we separate demonstration data from real audit records?',
    a: 'Yes. Seeded illustrative records carry a clear DEMO badge and can be hidden from dashboard metrics, removed cleanly, or restored without overwriting any USER record.',
  },
  {
    q: 'What report formats can auditors export for governance review?',
    a: 'You can generate structured multi section PDF audit reports, multi sheet Excel workbooks covering nine ISMS registers, append only CSV files, and SHA 256 verified JSON backups.',
  },
  {
    q: 'Does using this tracker certify an organization under ISO 27001?',
    a: 'No. SecureAudit organizes audit workpapers, evidence references, and remediation workflows. Formal conformity requires qualified auditors and accredited certification body review.',
  },
];

export const LandingPage: React.FC<LandingPageProps> = ({
  onOpenWorkspace,
  onSignInClick,
  onOpenPrivacy,
  onOpenTerms,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const [activeWords, setActiveWords] = useState<number>(0);
  const [readinessEmail, setReadinessEmail] = useState('');
  const [emailStatus, setEmailStatus] = useState<{ ok: boolean; msg: string } | null>(null);

  const taglineRef = useRef<HTMLDivElement | null>(null);
  const pageRef = useRef<HTMLDivElement | null>(null);

  // B7: IntersectionObserver reveal once for sections
  useEffect(() => {
    const root = pageRef.current;
    if (!root) return;
    const targets = root.querySelectorAll('.reveal-section');
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.14 }
    );
    targets.forEach((el) => obs.observe(el));
    return () => obs.disconnect();
  }, []);

  // B11: Tagline word-by-word reveal throttled via requestAnimationFrame
  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      setActiveWords(TAGLINE_WORDS.length);
      return;
    }
    let ticking = false;
    const updateWords = () => {
      ticking = false;
      const el = taglineRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const vh = window.innerHeight || 800;
      const start = vh * 0.85;
      const end = vh * 0.25;
      const progress = Math.min(1, Math.max(0, (start - rect.top) / (start - end)));
      const count = Math.round(progress * TAGLINE_WORDS.length);
      setActiveWords((prev) => Math.max(prev, count));
    };

    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(updateWords);
      }
    };

    updateWords();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleChecklistRequest = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = readinessEmail.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      setEmailStatus({
        ok: false,
        msg: 'Check failed. Enter a valid work or university email address.',
      });
      return;
    }
    setEmailStatus({
      ok: true,
      msg: `Readiness workspace unlocked for ${trimmed}. Opening audit platform.`,
    });
    setTimeout(() => onOpenWorkspace(), 500);
  };

  return (
    <div ref={pageRef} className="min-h-screen bg-[#F8FAFC] text-[#0F172A]">
      {/* B7: Floating compact centered translucent navigation bar */}
      <header className="sticky top-4 z-40 px-4">
        <nav
          aria-label="Primary navigation"
          className="mx-auto flex max-w-5xl items-center justify-between rounded-2xl border border-[#E2E8F0] bg-white/85 px-4 py-2 backdrop-blur-md"
        >
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#2563EB] text-white">
              <ShieldCheck size={20} weight="fill" />
            </span>
            <span className="title-3 text-[#0F172A]">SecureAudit</span>
          </div>

          <div className="hidden items-center gap-6 md:flex">
            <a href="#overview" className="title-4 text-[#0F172A] underline decoration-[#2563EB] decoration-2 underline-offset-8">
              Overview
            </a>
            <a href="#benefits" className="title-4 text-[#475569] hover:text-[#0F172A] transition-colors duration-300">
              Capabilities
            </a>
            <a href="#workflow" className="title-4 text-[#475569] hover:text-[#0F172A] transition-colors duration-300">
              How it works
            </a>
            <a href="#architecture" className="title-4 text-[#475569] hover:text-[#0F172A] transition-colors duration-300">
              Assurance
            </a>
            <a href="#faq" className="title-4 text-[#475569] hover:text-[#0F172A] transition-colors duration-300">
              FAQ
            </a>
          </div>

          <div className="hidden items-center gap-2 md:flex">
            <button
              type="button"
              onClick={onSignInClick}
              className="btn-main button-sm rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A] hover:bg-[#F1F5F9]"
            >
              Sign in
            </button>
            <button
              type="button"
              onClick={onOpenWorkspace}
              className="btn-main button-sm inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
            >
              Open audit workspace
              <ArrowRight size={16} weight="bold" />
            </button>
          </div>

          {/* Mobile toggle */}
          <button
            type="button"
            aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-[#E2E8F0] bg-white text-[#0F172A] md:hidden"
          >
            <span
              className="transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
              style={{ transform: mobileMenuOpen ? 'rotate(90deg)' : 'rotate(0deg)' }}
            >
              {mobileMenuOpen ? <X size={20} /> : <List size={20} />}
            </span>
          </button>
        </nav>

        {/* B7: Full height mobile menu with staggered link entrance */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 flex flex-col bg-[#F8FAFC]/95 p-6 backdrop-blur-xl md:hidden">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#2563EB] text-white">
                  <ShieldCheck size={20} weight="fill" />
                </span>
                <span className="title-3 text-[#0F172A]">SecureAudit</span>
              </div>
              <button
                type="button"
                aria-label="Close menu"
                onClick={() => setMobileMenuOpen(false)}
                className="flex h-10 w-10 items-center justify-center rounded-lg border border-[#CBD5E1] bg-white"
              >
                <X size={20} />
              </button>
            </div>
            <div className="mt-10 flex flex-col gap-6">
              {[
                { href: '#overview', label: 'Overview' },
                { href: '#benefits', label: 'Capabilities' },
                { href: '#workflow', label: 'How it works' },
                { href: '#architecture', label: 'Assurance' },
                { href: '#faq', label: 'FAQ' },
              ].map((item, idx) => (
                <a
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  style={{ transitionDelay: `${Math.min(idx * 60, 300)}ms` }}
                  className="heading-5 text-[#0F172A] transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
                >
                  {item.label}
                </a>
              ))}
              <button
                type="button"
                onClick={() => {
                  setMobileMenuOpen(false);
                  onOpenWorkspace();
                }}
                className="btn-main button-md mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-[#2563EB] text-white"
              >
                Open audit workspace
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        )}
      </header>

      <main id="main-content">
        {/* 1. HERO SECTION (A2 & B5: Single primary CTA above the fold, max-w 680px, gradient heading text only) */}
        <section id="overview" className="mx-auto max-w-6xl px-4 pt-16 pb-20 sm:px-6">
          <div className="flex flex-col items-center text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#BFDBFE] bg-[#EFF6FF] px-3 py-1">
              <ShieldCheck size={16} className="text-[#2563EB]" weight="fill" />
              <span className="caption-3 text-[#1E40AF]">
                ISO 27001:2022 · Amd 1:2024 · SQLite Local Assurance
              </span>
            </div>

            <h1 className="heading-1 hero-heading-light max-w-[680px]">
              Run verifiable ISO 27001 internal audits
              <br />
              without scattered spreadsheets
            </h1>

            <p className="body-2 mt-6 max-w-[680px] text-[#475569]">
              Connect audit scope, 40 Annex A control workpapers, SHA 256 verified evidence files,
              CAPA owners, and signed PDF reports inside one local SQLite workspace.
            </p>

            {/* Single Primary CTA above the fold (A4) */}
            <div className="mt-8 flex flex-col items-center gap-3">
              <button
                type="button"
                onClick={onOpenWorkspace}
                className="btn-main button-md inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
              >
                Open live audit workspace
                <ArrowRight size={18} weight="bold" />
              </button>
              <p className="caption-2 text-[#64748B]">
                100% local SQLite storage · Zero cloud account required · Safe DEMO and USER separation
              </p>
            </div>

            {/* Proof signal directly beneath CTA */}
            <div className="mt-10 grid w-full max-w-4xl grid-cols-2 gap-3 rounded-2xl border border-[#E2E8F0] bg-white p-2 sm:grid-cols-4">
              {[
                { metric: '40 controls', detail: 'Annex A 2022 reference set' },
                { metric: 'SHA 256', detail: 'Evidence & log chain digests' },
                { metric: '4 RBAC roles', detail: 'Scrypt salted auth & lockout' },
                { metric: 'PDF & XLSX', detail: 'One click signed audit exports' },
              ].map((item) => (
                <div key={item.metric} className="rounded-lg bg-[#F8FAFC] p-3 text-left">
                  <div className="title-2 font-mono text-[#0F172A]">{item.metric}</div>
                  <div className="caption-2 mt-1 text-[#64748B]">{item.detail}</div>
                </div>
              ))}
            </div>

            {/* Hero Visual: Live Preview Frame matching SecureAudit Interface */}
            <div className="mt-12 w-full rounded-2xl border border-[#CBD5E1] bg-[#181818] p-3 text-left">
              <div className="flex items-center justify-between border-b border-[#272727] px-3 pb-3">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-[#DC2626]" />
                  <span className="h-3 w-3 rounded-full bg-[#D97706]" />
                  <span className="h-3 w-3 rounded-full bg-[#059669]" />
                  <span className="caption-4 ml-2 font-mono text-[#94A3B8]">
                    SecureAudit Web Tracker · ISO 27001 Annual Security Audit
                  </span>
                </div>
                <span className="caption-3 rounded bg-[#272727] px-2 py-1 text-[#93C5FD]">
                  Illustrative Preview
                </span>
              </div>
              <div className="mt-3 grid gap-3 rounded-xl bg-[#F8FAFC] p-4 sm:grid-cols-4">
                <div className="rounded-lg border border-[#E2E8F0] bg-white p-4">
                  <div className="caption-2 text-[#64748B]">Audits in scope</div>
                  <div className="heading-5 mt-1 font-mono text-[#0F172A]">4</div>
                  <div className="caption-4 mt-1 text-[#059669]">2 signed off</div>
                </div>
                <div className="rounded-lg border border-[#E2E8F0] bg-white p-4">
                  <div className="caption-2 text-[#64748B]">Tracked findings</div>
                  <div className="heading-5 mt-1 font-mono text-[#DC2626]">8</div>
                  <div className="caption-4 mt-1 text-[#991B1B]">3 critical open</div>
                </div>
                <div className="rounded-lg border border-[#E2E8F0] bg-white p-4">
                  <div className="caption-2 text-[#64748B]">Mean compliance</div>
                  <div className="heading-5 mt-1 font-mono text-[#0F172A]">69.8%</div>
                  <div className="caption-4 mt-1 text-[#475569]">20 workpapers</div>
                </div>
                <div className="rounded-lg border border-[#E2E8F0] bg-white p-4">
                  <div className="caption-2 text-[#64748B]">Log chain status</div>
                  <div className="heading-5 mt-1 font-mono text-[#065F46]">VERIFIED</div>
                  <div className="caption-4 mt-1 text-[#059669]">SHA 256 linked</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* B11: MANDATORY TAGLINE REVEAL SECTION (Word-by-word opacity transition on scroll) */}
        <section
          aria-label="Core traceability statement"
          className="border-y border-[#E2E8F0] bg-[#181818] py-24 px-4 sm:px-6"
        >
          <div ref={taglineRef} className="mx-auto max-w-[680px]">
            <p className="caption-3 mb-4 uppercase tracking-wider text-[#60A5FA]">
              Audit lifecycle continuity
            </p>
            <h2 className="heading-3 text-white">
              {TAGLINE_WORDS.map((word, idx) => (
                <React.Fragment key={`${word}-${idx}`}>
                  <span className={`tagline-word ${idx < activeWords ? 'is-active' : ''}`}>
                    {word}
                  </span>{' '}
                </React.Fragment>
              ))}
            </h2>
          </div>
        </section>

        {/* 2. PROBLEM TO SOLUTION & OUTCOME BENEFITS (A2 & A5) */}
        <section id="benefits" className="reveal-section mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <div className="max-w-[680px]">
            <p className="caption-3 uppercase tracking-wider text-[#2563EB]">
              Built for ISMS governance teams
            </p>
            <h2 className="heading-3 mt-2 text-[#0F172A]">
              Replace disconnected checklists with end to end audit traceability
            </h2>
            <p className="body-3 mt-4 text-[#475569]">
              When control matrices, sample notes, evidence files, and CAPA due dates live in separate
              folders, reviewers lose visibility into what was tested and whether remediation closed.
            </p>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: <ClipboardText size={24} className="text-[#2563EB]" weight="duotone" />,
                title: 'Connected workpapers',
                body: 'Link every audit scope directly to Annex A test procedures, sample sizes, auditor observations, and live compliance scoring.',
              },
              {
                icon: <Fingerprint size={24} className="text-[#059669]" weight="duotone" />,
                title: 'SHA 256 evidence integrity',
                body: 'Compute cryptographic file digests and byte counts on upload, enforce a 20 MB media allowlist, and verify hashes before download.',
              },
              {
                icon: <LockKey size={24} className="text-[#D97706]" weight="duotone" />,
                title: 'Salted scrypt RBAC',
                body: 'Separate Admin, Auditor, Risk Owner, and Viewer permissions with RFC 7914 scrypt hashing and 15 minute failed login lockout.',
              },
              {
                icon: <FilePdf size={24} className="text-[#DC2626]" weight="duotone" />,
                title: 'Signed executive reports',
                body: 'Record formal report version approval and export structured PDF reports, 9 sheet Excel workbooks, and verified JSON backups.',
              },
            ].map((card) => (
              <article
                key={card.title}
                className="rounded-2xl border border-[#E2E8F0] bg-white p-6"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                  {card.icon}
                </div>
                <h3 className="title-2 mt-4 text-[#0F172A]">{card.title}</h3>
                <p className="body-6 mt-2 text-[#475569]">{card.body}</p>
              </article>
            ))}
          </div>
        </section>

        {/* 3. HOW IT WORKS IN THREE STEPS (A2) */}
        <section id="workflow" className="reveal-section border-y border-[#E2E8F0] bg-white py-20 px-4 sm:px-6">
          <div className="mx-auto max-w-6xl">
            <div className="max-w-[680px]">
              <p className="caption-3 uppercase tracking-wider text-[#2563EB]">
                Three step workflow
              </p>
              <h2 className="heading-3 mt-2 text-[#0F172A]">
                From Clause 9.2 audit plan to signed management report
              </h2>
            </div>

            <div className="mt-12 grid gap-6 md:grid-cols-3">
              {[
                {
                  step: '01',
                  title: 'Define scope and Statement of Applicability',
                  desc: 'Create an audit container, assign lead auditors, and select applicable ISO 27001:2022 Annex A controls with documented justifications.',
                },
                {
                  step: '02',
                  title: 'Execute control tests and hash evidence',
                  desc: 'Record test sample sizes and outcomes, attach SHA 256 verified artefacts, and log structured findings with root cause and CAPA owners.',
                },
                {
                  step: '03',
                  title: 'Approve report and export audit package',
                  desc: 'Complete Admin report sign off, verify the tamper evident audit trail, and download executive PDF and Excel deliverables.',
                },
              ].map((st) => (
                <div key={st.step} className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-6">
                  <span className="font-mono title-1 text-[#2563EB]">{st.step}</span>
                  <h3 className="title-2 mt-3 text-[#0F172A]">{st.title}</h3>
                  <p className="body-6 mt-2 text-[#475569]">{st.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 4. ACADEMIC & TECHNICAL ASSURANCE PROOF (A2 & B8 — Zero invented customer quotes; factual NFSU project context) */}
        <section id="architecture" className="reveal-section mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <div className="grid gap-8 rounded-2xl border border-[#E2E8F0] bg-white p-8 lg:grid-cols-2">
            <div>
              <p className="caption-3 uppercase tracking-wider text-[#2563EB]">
                Verified architecture & standards alignment
              </p>
              <h2 className="heading-4 mt-2 text-[#0F172A]">
                Engineered for transparent cybersecurity governance review
              </h2>
              <p className="body-3 mt-4 text-[#475569]">
                Developed as an applied MBA Cyber Security Management software artefact at National
                Forensic Sciences University, Gandhinagar. Every security control claimed in the
                documentation is backed by automated pytest verification.
              </p>
              <div className="mt-6 flex flex-col gap-3">
                {[
                  'ISO/IEC 27001:2022 Clauses 4 to 10 plus Amd 1:2024 climate context notes',
                  'ISO 19011:2026 management system audit programme traceability model',
                  'Illustrative cross framework mappings to NIST CSF 2.0 and SOC 2 criteria',
                  'Dual runtime support: React + FastAPI web app and 8 page Streamlit suite',
                ].map((line) => (
                  <div key={line} className="flex items-start gap-2">
                    <CheckCircle size={20} className="mt-0.5 shrink-0 text-[#059669]" weight="fill" />
                    <span className="body-5 text-[#334155]">{line}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex flex-col justify-between rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-6">
              <div>
                <div className="flex items-center gap-2">
                  <Scales size={20} className="text-[#2563EB]" />
                  <span className="title-3 text-[#0F172A]">Interactive readiness access</span>
                </div>
                <p className="body-6 mt-2 text-[#475569]">
                  Enter your institutional or work email to validate client side access and open the
                  live audit workspace immediately, or jump straight into the demo account view.
                </p>
                <form onSubmit={handleChecklistRequest} className="mt-4 flex flex-col gap-3 sm:flex-row" noValidate>
                  <label htmlFor="readiness-email" className="sr-only">
                    Work or institutional email
                  </label>
                  <input
                    id="readiness-email"
                    type="email"
                    value={readinessEmail}
                    onChange={(e) => setReadinessEmail(e.target.value)}
                    placeholder="auditor@organization.org"
                    className="body-5 flex-1 rounded-lg border border-[#CBD5E1] bg-white px-3 py-2 text-[#0F172A]"
                  />
                  <button
                    type="submit"
                    className="btn-main button-sm rounded-lg bg-[#0F172A] text-white hover:bg-[#1E293B]"
                  >
                    Launch with email
                  </button>
                </form>
                {emailStatus && (
                  <p
                    role="status"
                    className={`caption-1 mt-2 ${
                      emailStatus.ok ? 'text-[#065F46]' : 'text-[#991B1B]'
                    }`}
                  >
                    {emailStatus.msg}
                  </p>
                )}
              </div>

              <div className="mt-6 grid grid-cols-3 gap-3 border-t border-[#E2E8F0] pt-4">
                <div>
                  <div className="caption-4 text-[#64748B]">Password KDF</div>
                  <div className="body-4 font-mono text-[#0F172A]">scrypt 16384</div>
                </div>
                <div>
                  <div className="caption-4 text-[#64748B]">Lockout window</div>
                  <div className="body-4 font-mono text-[#0F172A]">5 tries / 15m</div>
                </div>
                <div>
                  <div className="caption-4 text-[#64748B]">Upload cap</div>
                  <div className="body-4 font-mono text-[#0F172A]">20 MB SHA256</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 5. FAQ SECTION (A2 & A7 — Plain Q&A objection handling) */}
        <section id="faq" className="reveal-section border-t border-[#E2E8F0] bg-white py-20 px-4 sm:px-6">
          <div className="mx-auto max-w-4xl">
            <p className="caption-3 uppercase tracking-wider text-[#2563EB]">
              Frequently asked questions
            </p>
            <h2 className="heading-3 mt-2 text-[#0F172A]">
              Governance, data privacy, and deployment details
            </h2>

            <div className="mt-10 flex flex-col gap-3">
              {FAQS.map((item, index) => {
                const isOpen = openFaq === index;
                return (
                  <div
                    key={item.q}
                    className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4"
                  >
                    <button
                      type="button"
                      aria-expanded={isOpen}
                      onClick={() => setOpenFaq(isOpen ? null : index)}
                      className="flex w-full items-center justify-between gap-4 text-left"
                    >
                      <span className="title-3 text-[#0F172A]">{item.q}</span>
                      <CaretDown
                        size={18}
                        className="shrink-0 text-[#475569] transition-transform duration-300 ease-[cubic-bezier(0.22,1,0.36,1)]"
                        style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}
                      />
                    </button>
                    {isOpen && (
                      <p className="body-5 mt-3 text-[#475569]">{item.a}</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* 6. RISK REVERSAL & FINAL CTA (A2 — Identical promise to hero) */}
        <section className="reveal-section border-t border-[#E2E8F0] bg-[#181818] py-20 px-4 text-center sm:px-6">
          <div className="mx-auto max-w-[680px]">
            <h2 className="heading-3 hero-heading-dark">
              Start tracking your ISO 27001 audit programme right now
            </h2>
            <p className="body-2 mt-4 text-[#CBD5E1]">
              Explore four preloaded illustrative audits or switch to a clean user workspace in one
              click. No external database setup, no subscription, and full JSON export anytime.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <button
                type="button"
                onClick={onOpenWorkspace}
                className="btn-main button-md inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
              >
                Open live audit workspace
                <ArrowRight size={18} weight="bold" />
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* B10: Footer with Privacy Policy, Terms, Governance Disclaimer & Way Back */}
      <footer className="border-t border-[#E2E8F0] bg-white py-10 px-4 sm:px-6">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck size={20} className="text-[#2563EB]" weight="fill" />
              <span className="title-4 text-[#0F172A]">
                SecureAudit · ISMS ISO/IEC 27001 Audit Tracker
              </span>
            </div>
            <p className="caption-2 mt-1 text-[#64748B]">
              Educational ISMS governance prototype · National Forensic Sciences University Minor Project
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-6">
            <button
              type="button"
              onClick={onOpenPrivacy}
              className="caption-1 text-[#475569] hover:text-[#0F172A]"
            >
              Privacy policy
            </button>
            <button
              type="button"
              onClick={onOpenTerms}
              className="caption-1 text-[#475569] hover:text-[#0F172A]"
            >
              Terms of use
            </button>
            <button
              type="button"
              onClick={onSignInClick}
              className="caption-1 text-[#2563EB] hover:text-[#1D4ED8]"
            >
              Role sign in
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
