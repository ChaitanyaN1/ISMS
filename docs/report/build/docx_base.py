"""Reusable DOCX scaffolding that enforces the institutional format rules.

Rules implemented (from Format.pdf):
 1  A4 paper
 2  Margins: left 1.5in (38.1mm), right 0.75in (19.05mm), top/bottom 1.0in (25.4mm)
 3  1.5 line spacing, 10-12 cpi  -> Times New Roman 12pt (= 12 cpi pitch)
 4  12pt before each first paragraph after a heading; no indentation; justified single column
 5  Pagination: roman i,ii,iii for front matter (no number on title page);
    arabic 1,2,3 restarting at Chapter 1; every number centred in the footer
 6  Each chapter starts on a new page; 20pt bold, title case, 30mm extra top margin
 7  Section 14pt / subsection 12pt bold; 36pt before first section, 24pt after
 8  Times New Roman
 9  Body 12, subtitle 14, title 16/20
10  Bold/italic used only for specific purposes
11  Fully justified
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

FONT = "Times New Roman"
BODY = 12
SECTION = 14
SUBSECTION = 12
CHAPTER = 20

def _set_cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        if edge in kwargs:
            el = OxmlElement(f"w:{edge}")
            for k, v in kwargs[edge].items():
                el.set(qn(f"w:{k}"), str(v))
            tcBorders.append(el)
    tcPr.append(tcBorders)

def _shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)

def _field(paragraph, instr):
    """Insert a Word field (used for PAGE / SECTIONPAGES)."""
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar"); fld_begin.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    fld_sep = OxmlElement("w:fldChar"); fld_sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t"); txt.text = "1"
    fld_end = OxmlElement("w:fldChar"); fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin); run._r.append(it); run._r.append(fld_sep)
    run._r.append(txt); run._r.append(fld_end)
    return run


class Report:
    def __init__(self):
        self.doc = Document()
        self._init_styles()
        self._init_section(self.doc.sections[0])
        self.figure_no = 0
        self.table_no = 0
        self.headings = []  # (number, title) in document order, for the contents page
        self.fignums = {}
        self.chapter_no = 0
        self.tab_in_ch = 0
        self.figures = []   # (number, caption, page_hint)
        self.tables = []    # (number, caption)
        self._sec = self.doc.sections[0]
        self._first_section_of_chapter = False

    # ---------- setup ----------
    def _init_styles(self):
        normal = self.doc.styles["Normal"]
        normal.font.name = FONT
        normal.font.size = Pt(BODY)
        rpr = normal.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts"); rpr.append(rf)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(attr), FONT)
        pf = normal.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def _init_section(self, s):
        s.page_width = Inches(8.27)      # A4
        s.page_height = Inches(11.69)
        s.left_margin = Inches(1.5)      # rule 2
        s.right_margin = Inches(0.75)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.header_distance = Inches(0.5)
        s.footer_distance = Inches(0.5)

    def new_section(self, footer_fmt="decimal", start=None, top_extra_mm=None):
        """Add a section break; optionally format/restart page numbering."""
        s = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._init_section(s)
        if top_extra_mm:
            s.top_margin = Inches(1.0 + top_extra_mm / 25.4)
        self._number_section(s, footer_fmt, start)
        self._sec = s
        return s

    def _number_section(self, s, fmt, start):
        sectPr = s._sectPr
        pg = sectPr.find(qn("w:pgNumType"))
        if pg is None:
            pg = OxmlElement("w:pgNumType"); sectPr.append(pg)
        pg.set(qn("w:fmt"), fmt)
        if start is not None:
            pg.set(qn("w:start"), str(start))
        elif pg.get(qn("w:start")) is not None:
            # a section inherits the previous one's sectPr: drop any restart so
            # the body keeps counting up from Chapter 1
            del pg.attrib[qn("w:start")]
        # centred page number in the footer
        footer = s.footer
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        for r in list(p.runs):
            r._r.getparent().remove(r._r)
        run = _field(p, " PAGE ")
        run.font.name = FONT
        run.font.size = Pt(11)
        # header: make sure it is empty and unlinked
        header = s.header
        header.is_linked_to_previous = False
        for hp in header.paragraphs:
            for r in list(hp.runs):
                r._r.getparent().remove(r._r)

    def suppress_footer(self):
        """No page number (title page)."""
        s = self._sec
        s.footer.is_linked_to_previous = False
        for p in s.footer.paragraphs:
            for r in list(p.runs):
                r._r.getparent().remove(r._r)

    # ---------- content primitives ----------
    def para(self, text="", size=BODY, bold=False, italic=False, align="justify",
             space_before=0, space_after=0, first_line_indent=0, keep_with_next=False,
             line_spacing=1.5, style_color=None):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
                        "center": WD_ALIGN_PARAGRAPH.CENTER,
                        "left": WD_ALIGN_PARAGRAPH.LEFT,
                        "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
        pf.space_before = Pt(space_before)
        pf.space_after = Pt(space_after)
        pf.first_line_indent = Inches(first_line_indent)
        pf.keep_with_next = keep_with_next
        if line_spacing == 1.5:
            pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        else:
            pf.line_spacing = line_spacing
        if text:
            r = p.add_run(text)
            r.font.name = FONT
            r.font.size = Pt(size)
            r.bold = bold
            r.italic = italic
            if style_color:
                r.font.color.rgb = RGBColor.from_string(style_color)
        return p

    def rich(self, parts, size=BODY, align="justify", space_before=0, space_after=0,
             first_line_indent=0, line_spacing=1.5):
        """parts = list of (text, bold, italic) tuples."""
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
                        "center": WD_ALIGN_PARAGRAPH.CENTER,
                        "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
        pf.space_before = Pt(space_before); pf.space_after = Pt(space_after)
        pf.first_line_indent = Inches(first_line_indent)
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE if line_spacing == 1.5 else WD_LINE_SPACING.SINGLE
        if line_spacing != 1.5:
            pf.line_spacing = line_spacing
        for text, bold, italic in parts:
            r = p.add_run(text)
            r.font.name = FONT; r.font.size = Pt(size)
            r.bold = bold; r.italic = italic
        return p

    def page_break(self):
        self.doc.add_page_break()

    def chapter(self, number, title):
        """Rule 6: new page, 20pt bold, title case, +30mm top margin."""
        s = self.new_section(footer_fmt="decimal", start=1 if number == 1 else None,
                             top_extra_mm=30)
        self._first_section_of_chapter = True
        self.chapter_no = int(number) if str(number).isdigit() else self.chapter_no + 1
        self.tab_in_ch = 0
        p = self.doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"CHAPTER {number}")
        r.font.name = FONT; r.font.size = Pt(CHAPTER); r.bold = True
        p.paragraph_format.outline_level = 0
        p2 = self.doc.add_paragraph()
        p2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p2.paragraph_format.keep_with_next = True
        r2 = p2.add_run(title.upper())
        r2.font.name = FONT; r2.font.size = Pt(CHAPTER); r2.bold = True
        p2.paragraph_format.outline_level = 0
        self.headings.append((f"ch{number}", title))
        return p2

    def section(self, number, title, first=False):
        """Rule 7: 36pt before the first section, 24pt for subsequent."""
        first = first or getattr(self, "_first_section_of_chapter", False)
        self._first_section_of_chapter = False
        p = self.doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(36 if first else 24)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"{number}  {title}")
        r.font.name = FONT; r.font.size = Pt(SECTION); r.bold = True
        p.paragraph_format.outline_level = 1
        self.headings.append((f"s{number}", f"{number}  {title}"))
        return p

    def subsection(self, number, title):
        p = self.doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"{number}  {title}")
        r.font.name = FONT; r.font.size = Pt(SUBSECTION); r.bold = True
        p.paragraph_format.outline_level = 2
        return p

    def body(self, text, first_after_heading=True):
        """Rule 4: 12pt gap after a heading, no indentation, justified."""
        return self.para(text, space_before=12 if first_after_heading else 0,
                         space_after=0, first_line_indent=0)

    def bullets(self, items, size=BODY, space_before=0):
        for i, it in enumerate(items):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pf.left_indent = Inches(0.3)
            pf.first_line_indent = Inches(-0.15)
            pf.space_before = Pt(space_before if i == 0 else 4)
            pf.space_after = Pt(0)
            pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            r = p.add_run("\u2022  " + it)
            r.font.name = FONT; r.font.size = Pt(size)

    def numbered(self, items, size=BODY):
        for i, it in enumerate(items, 1):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pf.left_indent = Inches(0.35)
            pf.first_line_indent = Inches(-0.2)
            pf.space_before = Pt(0 if i == 1 else 4)
            pf.space_after = Pt(0)
            pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            r = p.add_run(f"{i}.  " + it)
            r.font.name = FONT; r.font.size = Pt(size)

    def figure(self, path, caption, width_in=6.0):
        import os as _os
        from PIL import Image as _Image
        num = self.fignums.get(_os.path.basename(path)) if getattr(self, "fignums", None) else None
        self.figure_no += 1
        if num is None:
            num = str(self.figure_no)
        p = self.doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.keep_with_next = True
        from PIL import Image as _Image
        w, h = _Image.open(path).size
        draw_w = min(6.0, width_in)
        if draw_w * h / w > 7.3:                 # keep a plate inside one page
            draw_w = 7.3 * w / h
        p.add_run().add_picture(path, width=Inches(draw_w))
        c = self.doc.add_paragraph()
        c.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_before = Pt(0)
        c.paragraph_format.space_after = Pt(12)
        c.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        r = c.add_run(f"Figure {num}. {caption}")
        r.font.name = FONT; r.font.size = Pt(10); r.italic = True
        self.figures.append((num, caption))
        return num

    def table(self, headers, rows, caption, widths=None, font_size=9.5, align_right=None):
        self.table_no += 1
        self.tab_in_ch = getattr(self, "tab_in_ch", 0) + 1
        tlabel = (f"Table {self.chapter_no}.{self.tab_in_ch}" if self.chapter_no
                  else f"Table F.{self.tab_in_ch}")
        cap = self.doc.add_paragraph()
        cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cap.paragraph_format.space_before = Pt(12)
        cap.paragraph_format.space_after = Pt(6)
        cap.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        cap.paragraph_format.keep_with_next = True
        r = cap.add_run(f"{tlabel}. {caption}")
        r.font.name = FONT; r.font.size = Pt(10); r.italic = True

        t = self.doc.add_table(rows=1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        hdr = t.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = ""
            p = hdr[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            run = p.add_run(h)
            run.font.name = FONT; run.font.size = Pt(font_size); run.bold = True
            _shade(hdr[i], "E2E8F0")
            _set_cell_border(hdr[i], top={"val": "single", "sz": 8, "color": "475569"},
                             bottom={"val": "single", "sz": 8, "color": "475569"},
                             left={"val": "single", "sz": 4, "color": "94A3B8"},
                             right={"val": "single", "sz": 4, "color": "94A3B8"})
        for row in rows:
            cells = t.add_row().cells
            for i, val in enumerate(row):
                cells[i].text = ""
                p = cells[i].paragraphs[0]
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                p.paragraph_format.alignment = (WD_ALIGN_PARAGRAPH.CENTER
                                                if align_right and i in align_right
                                                else WD_ALIGN_PARAGRAPH.LEFT)
                run = p.add_run(str(val))
                run.font.name = FONT; run.font.size = Pt(font_size)
                _set_cell_border(cells[i], top={"val": "single", "sz": 2, "color": "CBD5E1"},
                                 bottom={"val": "single", "sz": 2, "color": "CBD5E1"},
                                 left={"val": "single", "sz": 2, "color": "CBD5E1"},
                                 right={"val": "single", "sz": 2, "color": "CBD5E1"})
        if widths:
            for ri in range(len(t.rows)):
                for ci, w in enumerate(widths):
                    t.rows[ri].cells[ci].width = Inches(w)
        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(0)
        sp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        sp.add_run("").font.size = Pt(6)
        self.tables.append((tlabel, caption))
        return tlabel

    def toc_field(self):
        """Insert a real Word TOC field (updates on open / F9)."""
        p = self.doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        run = p.add_run()
        b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin"); b.set(qn("w:dirty"), "true")
        it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
        it.text = r'TOC \o "1-2" \h \z \u'
        sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
        t = OxmlElement("w:t"); t.text = "Right-click and choose Update Field to build the table of contents."
        end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
        run._r.append(b); run._r.append(it); run._r.append(sep); run._r.append(t); run._r.append(end)

    def contents_table(self, rows, page_col=True):
        """Printed table of contents with explicit page numbers (no field update needed)."""
        if not rows:
            return
        data = [(t, str(pg)) for t, pg in rows]
        self.table(["Title", "Page"], data, "Contents.", widths=[4.6, 0.9], font_size=10.2)

    def save(self, path):
        self.doc.save(path)
