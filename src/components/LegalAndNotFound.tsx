import React from 'react';
import { ArrowLeft, ShieldCheck, WarningOctagon } from '@phosphor-icons/react';

export const LegalPage: React.FC<{
  kind: 'privacy' | 'terms';
  onBack: () => void;
}> = ({ kind, onBack }) => {
  return (
    <div className="min-h-screen bg-[#F8FAFC] px-4 py-12 text-[#0F172A]">
      <article className="mx-auto max-w-3xl rounded-2xl border border-[#E2E8F0] bg-white p-8">
        <button
          type="button"
          onClick={onBack}
          className="btn-main button-sm mb-6 inline-flex items-center gap-2 rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A] hover:bg-[#F1F5F9]"
        >
          <ArrowLeft size={16} />
          Return to previous view
        </button>

        <div className="flex items-center gap-2">
          <ShieldCheck size={24} className="text-[#2563EB]" weight="fill" />
          <h1 className="heading-4 text-[#0F172A]">
            {kind === 'privacy' ? 'Privacy & local data handling policy' : 'Terms of educational & governance use'}
          </h1>
        </div>

        {kind === 'privacy' ? (
          <div className="mt-6 flex flex-col gap-4 body-3 text-[#334155]">
            <p>
              SecureAudit ISMS Audit Tracker operates as a local SQLite workspace. Audit plans,
              control tests, findings, CAPA items, uploaded evidence artefacts, and salted scrypt
              credentials remain inside the local runtime directory unless exported by an authorized user.
            </p>
            <p>
              Uploaded evidence files are restricted to approved document and image formats under 20 MB
              and are hashed with SHA 256 to detect accidental modification. Do not upload sensitive
              personal data or production secrets into an unhardened demonstration host.
            </p>
            <p>
              Session tokens are stored in browser local storage solely to authenticate local API
              requests and can be cleared immediately via the Sign Out control.
            </p>
          </div>
        ) : (
          <div className="mt-6 flex flex-col gap-4 body-3 text-[#334155]">
            <p>
              This platform is an educational and operational coordination prototype developed for
              ISO/IEC 27001:2022 audit workflow management. Seeded records marked DEMO are fictional
              examples and do not represent real organizational conformity or audit conclusions.
            </p>
            <p>
              Cross framework references to ISO/IEC 27001:2022, Amendment 1:2024, ISO 19011:2026,
              NIST CSF 2.0, and SOC 2 are navigation aids only. Always consult licensed standards and
              qualified legal or certification professionals before making compliance determinations.
            </p>
          </div>
        )}
      </article>
    </div>
  );
};

export const NotFoundPage: React.FC<{ onGoHome: () => void }> = ({ onGoHome }) => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] px-4">
      <div className="max-w-md rounded-2xl border border-[#E2E8F0] bg-white p-8 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-[#FEF2F2] text-[#DC2626]">
          <WarningOctagon size={28} weight="fill" />
        </div>
        <h1 className="heading-5 mt-4 text-[#0F172A]">Page not found (404)</h1>
        <p className="body-5 mt-2 text-[#475569]">
          The requested audit view or route does not exist in this workspace.
        </p>
        <button
          type="button"
          onClick={onGoHome}
          className="btn-main button-md mt-6 inline-flex items-center gap-2 rounded-lg bg-[#2563EB] text-white hover:bg-[#1D4ED8]"
        >
          <ArrowLeft size={18} />
          Return to SecureAudit dashboard
        </button>
      </div>
    </div>
  );
};
