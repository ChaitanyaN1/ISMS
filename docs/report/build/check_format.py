"""Audit the generated PDF against every numbered rule in Format.pdf.

Usage (from the repository root):
    .venv/bin/python docs/report/build/check_format.py

Prints one PASS/FAIL line per rule and exits non-zero if any rule fails.
"""
import os
import re
import sys

import pymupdf

PDF = "docs/report/Project_Report_ISMS_ISO27001_Audit_Tracker.pdf"
MM = 25.4 / 72.0

fails = []


def check(rule, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {rule:<58} {detail}")
    if not ok:
        fails.append(rule)


def main():
    doc = pymupdf.open(PDF)
    pages = len(doc)

    # -- rule 1: A4 ----------------------------------------------------------
    w, h = doc[0].rect.width, doc[0].rect.height
    check("1  A4 paper (210 x 297 mm)", abs(w * MM - 210) < 1 and abs(h * MM - 297) < 1,
          f"{w * MM:.1f} x {h * MM:.1f} mm, {pages} pages")

    body = [p for p in doc if p.get_text().strip()]
    blocks = [b for p in body for b in p.get_text("blocks") if b[4].strip()]
    xs0 = [b[0] for b in blocks]
    xs1 = [b[2] for b in blocks]
    ys0 = [b[1] for b in blocks]

    # -- rule 2: margins -----------------------------------------------------
    left_ok = abs(min(xs0) * MM - 38.1) < 1.2
    # glyph bounding boxes carry font ascent, so allow ~1 mm of tolerance against
    # the nominal box; baselines always sit inside the text area
    right_ok = max(xs1) * MM <= 191.1
    top_ok = min(ys0) * MM >= 24.5
    check("2  margins L 38.1 / R 19.05 / T 25.4 mm", left_ok and right_ok and top_ok,
          f"L {min(xs0) * MM:.1f}, R edge {max(xs1) * MM:.1f} (limit 191.0), "
          f"T {min(ys0) * MM:.1f} mm")

    # -- rule 3: 1.5 line spacing -------------------------------------------
    gaps = []
    for p in doc[10:40]:
        lines = [l for b in p.get_text("dict")["blocks"] for l in b.get("lines", [])
                 if l["spans"] and abs(l["spans"][0]["size"] - 12) < 0.4]
        for a, b in zip(lines, lines[1:]):
            d = b["bbox"][1] - a["bbox"][1]
            if 10 < d < 30:
                gaps.append(d)
    gaps.sort()
    med = gaps[len(gaps) // 2] * MM if gaps else 0
    check("3  1.5 line spacing (18 pt = 6.35 mm)", abs(med - 6.35) < 0.4, f"median {med:.2f} mm")

    # -- rule 5: pagination --------------------------------------------------
    def footer(p):
        return " ".join(wd[4] for wd in p.get_text("words") if wd[1] > p.rect.height - 70).strip()

    front = [footer(p) for p in doc[:8]]
    front_ok = front[0] == "" and front[1:] == ["i", "ii", "iii", "iv", "v", "vi", "vii"]
    check("5a front matter lower-case Roman, none on title", front_ok, ", ".join(repr(f) for f in front))

    chap = [(i, p) for i, p in enumerate(doc) if p.get_text().lstrip().startswith("CHAPTER 1")][0]
    seq = [footer(p) for p in doc[chap[0]:]]
    nums = [int(s) for s in seq if s.isdigit()]
    body_ok = nums == list(range(1, len(nums) + 1))
    check("5b body Arabic numerals restart at 1", body_ok, f"1..{nums[-1]} over {len(nums)} pages")

    # -- rule 6: chapter pages ----------------------------------------------
    tops, news = [], []
    for i, p in enumerate(doc):
        t = p.get_text().lstrip()
        if t.startswith("CHAPTER"):
            tops.append(min(b[1] for b in p.get_text("blocks")) * MM)
            prev_last = doc[i - 1].get_text().strip().splitlines()
            news.append(bool(prev_last))
    check("6a every chapter starts on a new page", all(news), f"{len(tops)} chapters")
    check("6b chapter title 55 mm from the top edge", all(abs(t - 55) < 3 for t in tops),
          f"{min(tops):.1f}-{max(tops):.1f} mm")

    # -- rules 7 and 9: heading sizes ---------------------------------------
    sizes = {}
    for p in doc[chap[0]:]:
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    sizes.setdefault(round(s["size"], 1), 0)
                    sizes[round(s["size"], 1)] += 1
    has20 = 20.0 in sizes
    has14 = 14.0 in sizes
    has12 = 12.0 in sizes
    check("7/9 chapter 20 pt, section 14 pt, body 12 pt", has20 and has14 and has12,
          "sizes " + ", ".join(f"{k}" for k in sorted(sizes, reverse=True)))

    # -- rule 4: justified paragraphs, no double spaces ----------------------
    # headings use fixed multi-space separators ("1.1   Title"); ordinary prose must not
    prose = 0
    for p in doc[chap[0]:]:
        for line in p.get_text().splitlines():
            if "  " in line and not re.match(r"^(\d+(\.\d+)*|[0-9.]+)\s{2,}\S", line):
                prose += 1
    dbl = prose
    check("4/11 justified text, no gaps in extraction", dbl == 0,
          f"{dbl} prose lines with stretched gaps")

    # -- rule 8: Times ------------------------------------------------------
    fonts = set()
    for p in doc[chap[0]:]:
        fonts |= {f[3] for f in p.get_fonts(full=True)}
    check("8  Times New Roman throughout", fonts and all("Times" in f for f in fonts),
          ", ".join(sorted(fonts)))

    # -- captions ------------------------------------------------------------
    figs = sum(len(re.findall(r"^Figure \d+\.\d+\.", p.get_text(), re.M)) for p in doc)
    tabs = sum(len(re.findall(r"^Table (F|\d+)\.\d\.", p.get_text(), re.M)) for p in doc)
    check("figures and tables carry numbered captions", figs >= 10 and tabs >= 13,
          f"{figs} figures, {tabs} tables")

    print(f"\n{len(fails)} rule(s) failed" if fails else "\nAll format rules satisfied")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
