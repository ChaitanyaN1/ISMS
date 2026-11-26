"""Build the project report in both DOCX and PDF from one content source.

Content modules call a small renderer API (chapter/section/subsection/body/para/
bullets/numbered/table/figure/rich). Two renderers implement it:
  * docx_base.Report     -> .docx (Word-native, live TOC field, editable)
  * pdf_report.PDFReport -> .pdf  (geometric compliance with every Format.pdf rule)

The PDF build runs twice: the first pass records the page each chapter, section,
figure and table lands on, the second pass prints the contents pages with those
numbers in place.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
os.chdir(ROOT)

import docx_base
import pdf_report
import content_front
from content_front import build_front_block, FIGURES, TABLES
from content_ch1_3 import ch1, ch2, ch3
from content_ch4_5 import ch4, ch5
from content_ch6_8 import ch6, ch7, ch8
from content_back import back_matter

FIG_ARCH   = "docs/report/figures/figure-4-1-architecture.png"
FIG_PHASES = "docs/report/figures/figure-3-1-phases.png"
FIG_ER     = "docs/report/figures/figure-4-2-er-model.png"
FIG_FLOW   = "docs/report/figures/figure-4-3-workflow.png"
FIG_DASH   = "docs/report/figures/figure-5-1-dashboard.png"
FIG_AUDIT  = "docs/report/figures/figure-5-2-audit-detail.png"
FIG_FIND   = "docs/report/figures/figure-5-3-findings.png"
FIG_SOA    = "docs/report/figures/figure-5-4-soa.png"
FIG_EVID   = "docs/report/figures/figure-5-5-evidence.png"
FIG_REP    = "docs/report/figures/figure-5-6-reports.png"

# content modules reference figures by their original (stale) file names
FIGMAP = {
    "docs/report/figures/figure-3-2-phases.png":       FIG_PHASES,
    "docs/report/figures/figure-3-1-architecture.png": FIG_ARCH,
    "docs/report/figures/figure-4-1-workflow.png":     FIG_FLOW,
    "figure-3-2-phases.png":       FIG_PHASES,
    "figure-3-1-architecture.png": FIG_ARCH,
    "figure-4-1-workflow.png":     FIG_FLOW,
}

FIGNUMS = {os.path.basename(FIGMAP.get(src, src)): num for num, _cap, src in FIGURES}


def _patch_figures():
    """Resolve the stale figure file names used inside the content modules."""
    for mod in (docx_base.Report, pdf_report.PDFReport):
        orig = mod.figure

        def figure(self, path, caption, *a, _orig=orig, **kw):
            path = FIGMAP.get(path, FIGMAP.get(os.path.basename(path), path))
            return _orig(self, path, caption, *a, **kw)

        mod.figure = figure


_patch_figures()


def build_docx(path):
    r = docx_base.Report()
    r.fignums = dict(FIGNUMS)
    build_front_block(r, docx=True)
    ch1(r); ch2(r); ch3(r); ch4(r); ch5(r); ch6(r); ch7(r); ch8(r); back_matter(r)
    r.save(path)
    return r


def build_pdf(path, pagemap=None):
    p = pdf_report.PDFReport()
    p.figmap = dict(FIGMAP)
    p.fignums = dict(FIGNUMS)
    p.pagemap = dict(pagemap or {})
    build_front_block(p, docx=False)
    p.start_body()                          # Chapter 1 -> Arabic page 1
    ch1(p); ch2(p); ch3(p); ch4(p); ch5(p); ch6(p); ch7(p); ch8(p); back_matter(p)
    p.save(path)
    return p


def make_pdf(path, passes=3):
    pagemap, p = {}, None
    for _ in range(passes):
        p = build_pdf(path, pagemap)
        if p.pagemap == pagemap:
            break
        pagemap = dict(p.pagemap)
    return p


if __name__ == "__main__":
    out_docx = "docs/report/Project_Report_ISMS_ISO27001_Audit_Tracker.docx"
    out_pdf  = "docs/report/Project_Report_ISMS_ISO27001_Audit_Tracker.pdf"
    args = sys.argv[1:] or ["docx", "pdf"]
    if "docx" in args:
        build_docx(out_docx)
        print("DOCX:", out_docx)
    if "pdf" in args:
        p = make_pdf(out_pdf)
        print("PDF:", out_pdf, "pages:", p.page_no())
