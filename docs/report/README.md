# Minor Project Report

Submission-ready report for **ISMS ISO 27001 Audit Tracker**, produced from a single
content source in two formats:

| File | Purpose |
| --- | --- |
| `Project_Report_ISMS_ISO27001_Audit_Tracker.pdf` | Typeset submission copy (Times, 64 pages) |
| `Project_Report_ISMS_ISO27001_Audit_Tracker.docx` | Editable copy for the guide / viva |

## Rebuilding

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install fpdf2 pyphen pymupdf pillow python-docx
python docs/report/build/build_all.py          # both formats
python docs/report/build/build_all.py pdf      # PDF only
python docs/report/build/check_format.py       # audit the PDF against Format.pdf
```

## How it is organised

```
build/
  content_front.py   title page, declaration, certificate, abstract, contents, abbreviations
  content_ch1_3.py   Chapter 1 Introduction, 2 Literature Review, 3 Research Methodology
  content_ch4_5.py   Chapter 4 System Analysis and Implementation, 5 Results and Analysis
  content_ch6_8.py   Chapter 6 Discussion, 7 Conclusion, 8 Limitations
  content_back.py    Chapter 9 Bibliography, 10 Annexures
  pdf_report.py      PDF renderer (fpdf2) -- enforces the Format.pdf rules geometrically
  docx_base.py       DOCX renderer (python-docx) -- Word-native fields, editable
  build_all.py       driver; runs the PDF twice so contents page numbers are correct
  check_format.py    automated audit of every numbered Format.pdf rule
  figs.py, figs2.py, plates.py   figure and interface-plate generators
figures/             10 generated figures referenced by the report
```

The contents pages are generated from the renderer's own recorded outline, so all three
levels (chapter, section, subsection) appear with dot leaders and their real page numbers.
The PDF is built twice: pass one records the page each heading, figure and table lands on,
pass two typesets the front matter with those numbers.

`check_format.py` verifies paper size, the three margins, 1.5 spacing, the Roman/Arabic
page-number sequences, the new page and 55 mm drop of every chapter, heading and body
font sizes, the absence of stretched justification gaps, the Times family, and the
figure and table caption numbering. It exits non-zero if any rule fails.

## Screen captures

The interface figures in Section 5.1.3 are real captures of the running application,
not illustrations. To regenerate them:

```bash
# 1. start the API and the client
.venv/bin/python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 &
npm run dev &                      # vite on :5173, proxies /api to :8000

# 2. drive a headless browser through every view
node docs/report/build/capture_screens.js        # landing, sign-in, nine domain views
node docs/report/build/capture_screens_extra.js  # audit detail, checklist, log, users

# 3. crop, scale and copy the results into figures/
```

The capture scripts expect Puppeteer with a Chromium binary, and they sign in through
the ordinary form with the seeded `admin` identity rather than injecting a session, so
the authentication path itself is exercised.
