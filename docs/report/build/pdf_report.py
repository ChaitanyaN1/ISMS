"""PDF renderer for the minor project report.

Every rule in Format.pdf is enforced geometrically:

 1  Paper size A4 (210 x 297 mm)
 2  Margins: left 1.5 in = 38.1 mm, right 0.75 in = 19.05 mm, top and bottom 1.0 in = 25.4 mm
 3  1.5 line spacing (12 pt body -> 18 pt leading = 6.35 mm)
 4  12 pt vertical space between a heading and its first paragraph; no first-line
    indentation; single column; fully justified
 5  Page numbers bottom-centre. Lower-case Roman numerals from the title page to the
    page before Chapter 1 (no number on the title page); Arabic numerals restarting
    at 1 on the first page of Chapter 1
 6  Each chapter begins on a new page, 20 pt bold title with an additional 30 mm of
    top margin (55 mm total)
 7  36 pt before the chapter's first section heading, 24 pt before every later
    section or subsection heading; sections 14 pt, subsections 12 pt, bold
 8  Times New Roman
 9  Body 12 pt, subtitles 14 pt, titles 16-20 pt
10  Bold and italic used only for specific purposes
11  Page justified
"""
from __future__ import annotations

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos, Align

# ---------------------------------------------------------------- geometry ---
PAGE_W, PAGE_H = 210.0, 297.0
ML, MR, MT, MB = 38.1, 19.05, 25.4, 25.4
TEXT_W = PAGE_W - ML - MR                    # 152.85 mm
BODY = 12
LEAD = 6.35                                  # 1.5 x 12 pt
PT = 0.352778                                # points -> millimetres

FAMILY = "Times"                             # core Times (Times New Roman metrics)

ROMAN = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
         (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]


def roman(n: int) -> str:
    out = ""
    for v, s in ROMAN:
        while n >= v:
            out += s
            n -= v
    return out


# ------------------------------------------------------------ justification --
try:
    import pyphen
    _HYPH = pyphen.Pyphen(lang="en_GB")
except Exception:                                               # pragma: no cover
    _HYPH = None


def _split_long(word, pdf, avail):
    """Legal hyphenation points for a word that cannot fit on one line."""
    if _HYPH is None or len(word) < 8:
        return [word]
    out, acc = [], ""
    for part in _HYPH.inserted(word, hyphen="-").split("-"):
        acc = part if not out else acc + "-" + part
        out.append(acc)
    return out


def _wrap(pdf, text, width, first_indent):
    sp = pdf.get_string_width(" ")
    words = []
    for w in text.split():
        if pdf.get_string_width(w) <= width - 2 * sp:
            words.append(w)
        else:
            words.extend(_split_long(w, pdf, width))
    lines, cur, limit = [], [], width - first_indent
    for w in words:
        if not cur:
            cur = [w]
            continue
        if pdf.get_string_width(" ".join(cur + [w])) <= limit:
            cur.append(w)
        else:
            lines.append([cur, limit])
            cur, limit = [w], width
    if cur:
        lines.append([cur, width])
    return lines


def justify(pdf, text, width, lead, first_indent=0.0, align="J"):
    """Word-wrap with hyphenation; justify by distributing slack across the gaps.

    The final line of a paragraph (and any line holding a single word) is set
    flush left, which is what a word processor does and is what keeps the
    extracted text readable.
    """
    text = _san(text)
    if align in ("L", "C", "R"):
        pdf.multi_cell(width, lead, text, align=align,
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        return

    lines = _wrap(pdf, text, width, first_indent)
    bottom = pdf.h - pdf.b_margin
    y = pdf.get_y()

    for idx, (words, measure) in enumerate(lines):
        if y + lead > bottom:
            pdf.add_page()
            y = pdf.get_y()
            measure = width - (first_indent if idx == 0 else 0.0)
        x = pdf.l_margin + (first_indent if idx == 0 else 0.0)
        last = idx == len(lines) - 1
        if last or len(words) == 1:
            pdf.set_xy(x, y)
            pdf.cell(measure, lead, " ".join(words), align="L")
        else:
            used = sum(pdf.get_string_width(w) for w in words)
            gaps = len(words) - 1
            gap = (measure - used) / gaps if gaps else 0.0
            cx = x
            for j, w in enumerate(words):
                ww = pdf.get_string_width(w)
                pdf.set_xy(cx, y)
                pdf.cell(ww + (gap if j < gaps else 0.0), lead, w, align="L")
                cx += ww + gap
        y += lead

    pdf.set_y(y)
    pdf.set_x(pdf.l_margin)


# ------------------------------------------------------- character handling --
# The PDF uses the core Times font (Times New Roman metrics), which covers the
# Latin-1 range only. Typographic characters are mapped to the closest Latin-1
# equivalent so the typeset page stays in Times; the DOCX keeps the originals.
_TRANSLIT = {
    "\u2013": "-", "\u2014": "--", "\u2015": "--", "\u2010": "-", "\u2011": "-",
    "\u2018": "'", "\u2019": "'", "\u201a": ",", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"',
    "\u2026": "...", "\u2022": "\u00b7", "\u2032": "'", "\u2033": '"',
    "\u2192": "->", "\u2190": "<-", "\u2264": "<=", "\u2265": ">=",
    "\u00a0": " ", "\u2009": " ", "\u200a": " ", "\u202f": " ", "\u200b": "",
    "\u20b9": "Rs.", "\u2713": "v", "\u2717": "x", "\u00ad": "-",
}


def _san(text):
    if not isinstance(text, str):
        return text
    for k, v in _TRANSLIT.items():
        if k in text:
            text = text.replace(k, v)
    return text


# ---------------------------------------------------------------- renderer ---
class PDFReport(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(ML, MT, MR)
        self.c_margin = 0              # positions and padding are computed exactly
        self.set_auto_page_break(True, margin=MB)
        self.set_font(FAMILY, "", BODY)
        self.fam = FAMILY          # alias used by the content modules
        self.mode = "off"                 # off | roman | arabic
        self._roman_n = 0
        self._body_first = None
        self.labels: dict[int, str | None] = {}
        self._queue: list[tuple[str, str, float]] = []
        self.fig_no = 0
        self.tab_no = 0
        self.figmap = {}
        self.fignums = {}
        self.pagemap = {}          # key -> printed page label, filled during the build
        self.chapter_no = 0
        self.tab_in_ch = 0
        self._first_section = True
        self.set_title("ISMS ISO 27001 Audit Tracker \u2014 Minor Project Report")
        self.set_author("Chaitanya Nagre")
        self.set_subject("MBA Cyber Security Management \u2014 Minor Project Report")
        self.set_creator("SecureAudit report builder")

    # ---- every string that reaches the PDF passes through the transliterator ----
    def cell(self, *args, **kwargs):
        args = tuple(_san(a) for a in args)
        kwargs = {k: _san(v) for k, v in kwargs.items()}
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        args = tuple(_san(a) for a in args)
        kwargs = {k: _san(v) for k, v in kwargs.items()}
        return super().multi_cell(*args, **kwargs)

    def write(self, *args, **kwargs):
        args = tuple(_san(a) for a in args)
        kwargs = {k: _san(v) for k, v in kwargs.items()}
        return super().write(*args, **kwargs)

    def text(self, *args, **kwargs):
        args = tuple(_san(a) for a in args)
        kwargs = {k: _san(v) for k, v in kwargs.items()}
        return super().text(*args, **kwargs)

    # ------------------------------------------------------------ pagination
    def add_page(self, orientation="", format="", same=False):
        super().add_page(orientation, format, same)
        self._label_page()
        self.set_top_margin(MT)
        self.set_y(MT)

    def _label_page(self):
        i = self.page_no()
        if i in self.labels:
            return
        if self.mode == "off":
            self.labels[i] = None                      # title page: no number
        elif self.mode == "roman":
            self._roman_n += 1
            self.labels[i] = roman(self._roman_n)
        else:
            if self._body_first is None:
                self._body_first = i
            self.labels[i] = str(i - self._body_first + 1)

    def new_front_page(self):
        """Open the next front-matter page; numbering continues in lower-case Roman."""
        self.mode = "roman"
        self.add_page()

    def start_body(self):
        """Rule 5: the body restarts at Arabic numeral 1 from the first chapter page."""
        self.mode = "arabic"
        self._body_first = None

    # --------------------------------------------------------- page mapping
    def _record(self, key):
        if key:
            self.pagemap.setdefault(key, self.labels.get(self.page_no(), ""))

    def footer(self):
        label = self.labels.get(self.page_no())
        if not label:
            return
        self.set_y(-MB + 4.5)
        self.set_font(FAMILY, "", 11)
        self.cell(0, 6, label, align=Align.C)
        self.set_y(-MB + 4.5)

    # --------------------------------------------------------- float figures
    def _drain(self):
        """Emit any figure that was deferred, at a paragraph or heading boundary."""
        pending = getattr(self, "_queue", None)
        if not pending:
            return
        self._queue = []
        font, size, style = self.font_family, self.font_size_pt, self.font_style
        for path, caption, width_in in pending:
            from PIL import Image
            w, h = Image.open(path).size
            disp_w = min(TEXT_W, width_in * 25.4)
            disp_h = disp_w * h / w
            if disp_h > 185:
                disp_h, disp_w = 185, 185 * w / h
            if self.get_y() + disp_h + 24 > PAGE_H - MB:
                self.add_page()
            self._place_figure(path, caption, width_in)
        self.set_font(font, style, size)

    def _figure_label(self, path, caption):
        mapped = self.figmap.get(path, self.figmap.get(os.path.basename(path), path))
        num = self.fignums.get(os.path.basename(mapped))
        return f"Figure {num}. {caption}" if num else caption

    def _place_figure(self, path, caption, width_in):
        path = self.figmap.get(path, self.figmap.get(os.path.basename(path), path))
        from PIL import Image
        w, h = Image.open(path).size
        disp_w = min(TEXT_W, width_in * 25.4)
        disp_h = disp_w * h / w
        if disp_h > 185:
            disp_h, disp_w = 185, 185 * w / h
        self.ln(2.5)
        self.image(path, x=ML + (TEXT_W - disp_w) / 2, y=self.get_y(), w=disp_w)
        self.set_y(self.get_y() + disp_h + 2.2)
        self.set_font(FAMILY, "I", 9.8)
        lbl = self._figure_label(path, caption)
        if lbl.startswith("Figure "):
            num = lbl[len("Figure "):].split(".")[0] + "." + lbl[len("Figure "):].split(".")[1].split()[0]
            self._record(f"fig{num}")
        self.multi_cell(TEXT_W, 4.5, lbl,
                        align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def figure(self, path, caption, width_in=6.0):
        path = self.figmap.get(path, self.figmap.get(os.path.basename(path), path))
        from PIL import Image
        w, h = Image.open(path).size
        disp_w = min(TEXT_W, width_in * 25.4)
        disp_h = disp_w * h / w
        if disp_h > 185:
            disp_h, disp_w = 185, 185 * w / h
        # if it will not fit here, let the text run on and float the figure
        if self.get_y() + disp_h + 24 > PAGE_H - MB:
            self._queue.append((path, caption, width_in))
            return
        self._place_figure(path, caption, width_in)

    # ------------------------------------------------------------- headings
    def _need(self, h_mm):
        if self.get_y() + h_mm > PAGE_H - MB - 1:
            self.add_page()

    def chapter(self, number, title):
        super().add_page()
        self._label_page()
        top = MT + 30                                  # rule 6: 55 mm total
        self.set_top_margin(top)
        self.set_y(top)
        self.set_font(FAMILY, "B", 20)
        self.multi_cell(TEXT_W, 8.6, f"CHAPTER {number}", align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.multi_cell(TEXT_W, 8.6, title.upper(), align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_top_margin(MT)
        self._first_section = True
        self.chapter_no = int(number) if str(number).isdigit() else self.chapter_no + 1
        self.tab_in_ch = 0
        self._record(f"ch{number}")
        self._drain()

    def section(self, number, title, first=False):
        self._drain()
        before = 36 if (self._first_section or first) else 24      # rule 7
        self._need(before * PT + 24)
        self.ln(before * PT)
        self.set_font(FAMILY, "B", 14)
        self._record(f"s{number}")
        self.multi_cell(TEXT_W, 6.2, f"{number}   {title}", align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._first_section = False

    def subsection(self, number, title):
        self._drain()
        self._need(24 * PT + 16)
        self.ln(24 * PT)
        self.set_font(FAMILY, "B", 12)
        self.multi_cell(TEXT_W, 5.6, f"{number}   {title}", align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def heading_center(self, text, size=16, before=0):
        if before:
            self.ln(before)
        self.set_font(FAMILY, "B", size)
        self.multi_cell(TEXT_W, size * PT * 1.45, text, align=Align.C,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ----------------------------------------------------------------- text
    def para(self, text="", size=BODY, bold=False, italic=False, align="justify",
             space_before=None, space_after=0, first_line_indent=0, keep_with_next=False,
             line_spacing=1.5, style_color=None):
        self._drain()
        style = ("B" if bold and not italic else "I" if italic and not bold
                 else "BI" if bold and italic else "")
        lead = size * PT * (1.5 if line_spacing == 1.5 else 1.15)
        if not text:
            self.ln(lead * 0.5)
            return
        if space_before is None:
            # rule 4: paragraphs are separated by space, not by indentation
            space_before = 12 if align == "justify" else 0
        if space_before:
            self._need(space_before * PT + lead * 2)
            self.ln(space_before * PT)
        self.set_font(FAMILY, style, size)
        self._need(lead * 2.4)
        al = {"justify": "J", "center": "C", "left": "L", "right": "R"}[align]
        justify(self, text, TEXT_W, lead, first_indent=first_line_indent or 0.0, align=al)

    def body(self, text):
        """Rule 4: 12 pt between the heading line and the first paragraph."""
        self._drain()
        self.ln(12 * PT)
        self.set_font(FAMILY, "", BODY)
        justify(self, text, TEXT_W, LEAD)

    def rich(self, parts, size=BODY, align="justify", space_before=0, space_after=0,
             first_line_indent=0, line_spacing=1.5):
        self._drain()
        lead = size * PT * 1.5
        if space_before:
            self._need(space_before * PT + lead * 2)
            self.ln(space_before * PT)
        self._need(lead * 2.4)
        align = {"justify": "J", "center": "C", "left": "L"}[align]
        x, y = self.l_margin, self.get_y()
        for text, bold, italic in parts:
            text = _san(text)
            style = ("B" if bold and not italic else "I" if italic and not bold
                     else "BI" if bold and italic else "")
            self.set_font(FAMILY, style, size)
            w = self.get_string_width(text)
            if x + w > self.l_margin + TEXT_W:
                y += lead
                x = self.l_margin
            self.set_xy(x, y)
            self.cell(w, lead, text)
            x += w
        self.set_y(y + lead)
        self.set_x(self.l_margin)

    def _list_room(self, items, size, budget_mm):
        """Move a short list to the next page rather than leaving one orphan item."""
        lead = size * PT * 1.5
        est = 5.5 * len(items) + 1.6 * (len(items) - 1) + budget_mm
        if len(items) <= 8 and self.get_y() + est > PAGE_H - MB:
            self.add_page()

    def bullets(self, items, size=BODY, space_before=0):
        self._drain()
        self._list_room(items, size, 4)
        for i, it in enumerate(items):
            self._need(LEAD * 3)
            if i:
                self.ln(1.6)
            self.set_font(FAMILY, "", size)
            self.set_x(ML + 5)
            justify(self, "\u2022   " + it, TEXT_W - 5, LEAD)

    def numbered(self, items, size=BODY):
        self._drain()
        self._list_room(items, size, 4)
        for i, it in enumerate(items, 1):
            self._need(LEAD * 3)
            if i > 1:
                self.ln(1.6)
            self.set_font(FAMILY, "", size)
            self.set_x(ML + 6)
            justify(self, f"{i}.   {it}", TEXT_W - 6, LEAD)

    # ---------------------------------------------------------------- table
    def table(self, headers, rows, caption, widths=None, font_size=8.5, align_right=None):
        ncol = len(headers)
        wi = list(widths) if widths else [1.0] * ncol
        tot = sum(wi)
        cols = [w / tot * TEXT_W for w in wi]

        # no column may be narrower than its longest unbreakable word, otherwise
        # multi_cell has to split words mid-way and the table becomes unreadable
        minw = []
        for j in range(ncol):
            words = []
            for row in [headers] + list(rows):
                if j < len(row):
                    for part in str(row[j]).split():
                        words.append(part)
            w0 = 0.0
            for part in words:
                for piece in _split_long(part, self, 40):
                    self.set_font(FAMILY, "B", font_size)
                    w0 = max(w0, self.get_string_width(piece) + 3.8)
            minw.append(min(w0, TEXT_W * 0.55))
        fixed = [max(c, m) for c, m in zip(cols, minw)]
        if sum(fixed) > TEXT_W:
            # shrink the wide columns to pay for the narrow ones
            over = sum(fixed) - TEXT_W
            flex = [i for i in range(ncol) if fixed[i] > minw[i] + 0.5]
            while over > 0.05 and flex:
                share = over / len(flex)
                for i in list(flex):
                    room = fixed[i] - minw[i]
                    take = min(share, room)
                    fixed[i] -= take
                    over -= take
                    if fixed[i] <= minw[i] + 0.01:
                        flex.remove(i)
        cols = fixed
        rh = font_size * PT * 1.32

        self.tab_no += 1
        self.tab_in_ch += 1
        label = (f"Table {self.chapter_no}.{self.tab_in_ch}" if self.chapter_no
                 else f"Table F.{self.tab_in_ch}")
        self._record(f"tab{self.chapter_no}.{self.tab_in_ch}")
        self._need(16 + 4 * (rh + 1.3))
        self.ln(2.5)
        self.set_font(FAMILY, "I", 9.8)
        self.multi_cell(TEXT_W, 4.5, f"{label}. {caption}",
                        align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.4)

        def height_of(cells, bold):
            self.set_font(FAMILY, "B" if bold else "", font_size)
            n = 1
            unit = self.get_string_width("n") * 1.02
            for txt, w in zip(cells, cols):
                per = max(5, int((w - 3.4) / unit))
                ln = 0
                for part in str(txt).split("\n"):
                    ln += max(1, -(-len(part) // per))
                n = max(n, ln)
            return max(rh + 1.3, n * rh * 0.99 + 2.1)

        def blit(cells, bold):
            h = height_of(cells, bold)
            if self.get_y() + h > PAGE_H - MB:
                self.add_page()
            y0, x = self.get_y(), ML
            for j, (txt, w) in enumerate(zip(cells, cols)):
                if bold:
                    self.set_fill_color(226, 232, 240)
                    self.set_draw_color(120, 130, 145)
                    self.rect(x, y0, w, h, style="DF")
                else:
                    self.set_draw_color(200, 210, 222)
                    self.rect(x, y0, w, h, style="D")
                self.set_xy(x + 1.7, y0 + 1.2)
                self.set_font(FAMILY, "B" if bold else "", font_size)
                al = Align.C if (j > 0 and len(str(txt)) <= 4) else Align.L
                self.multi_cell(w - 3.4, rh, str(txt), align=al, padding=0,
                                new_x=XPos.RIGHT, new_y=YPos.TOP)
                x += w
            self.set_y(y0 + h)

        # orphan control: keep the caption, the header and at least the first two
        # body rows together, otherwise move the whole table to the next page
        probe = [height_of(headers, True)] + [height_of(r, False) for r in rows[:2]]
        if self.get_y() + sum(probe) > PAGE_H - MB:
            self.add_page()
            self.set_font(FAMILY, "I", 9.8)
            self.multi_cell(TEXT_W, 4.5, f"{label}. {caption}", align=Align.L,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1.4)

        blit(headers, True)
        for row in rows:
            if self.get_y() + height_of(row, False) > PAGE_H - MB:
                self.add_page()
                blit(headers, True)
            blit(row, False)
        self.ln(2.5)

    def code_line(self, text, size=10.5):
        self._need(8)
        self.set_font("Courier", "", size)
        self.multi_cell(TEXT_W, 5.8, text, align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.8)

    def save(self, path):
        self.output(path)
