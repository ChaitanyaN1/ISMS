"""Generate report figures using only PIL (no matplotlib)."""
from PIL import Image, ImageDraw, ImageFont
import os, json, sqlite3

OUT = "docs/report/figures"
os.makedirs(OUT, exist_ok=True)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (15, 23, 42)
BLUE = (37, 99, 235)
GREEN = (5, 150, 105)
AMBER = (217, 119, 6)
RED = (220, 38, 38)
GREY = (100, 116, 139)
LIGHT = (241, 245, 249)
BORDER = (203, 213, 225)

def font(path, size): return ImageFont.truetype(path, size)
def tw(d, t, f): return d.textbbox((0,0), t, font=f)[2]

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ---------------- FIGURE 1: architecture ----------------
def fig_phases():
    W, H = 1900, 1140
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    ft = font(SERIF_B, 40); fbs = font(SANS_B, 25); fs = font(SANS, 22)
    d.text((70, 40), "Figure 3.1  Nine-phase implementation roadmap and deliverables", font=ft, fill=NAVY)
    d.line([70, 100, W-70, 100], fill=BLUE, width=4)
    phases = [
        ("Project foundation & local run configuration", "Vite + React scaffold, FastAPI app, run_all launchers"),
        ("SQLite schema & ISO reference catalogue", "11 tables, 40 Annex A controls, clauses 4–10, Amd 1:2024"),
        ("Risk, control and applicability registers", "SoA workflow, 5×5 risk scoring, treatment plans"),
        ("Audit planning and workpaper flow", "Audit container, test procedures, sample sizes, scoring"),
        ("Findings and corrective action management", "NC narrative, CAPA owners, due dates, verification"),
        ("Evidence vault and hash-chained audit log", "SHA-256 uploads, 20 MB cap, GENESIS-chained log"),
        ("Dashboard and analytics", "KPI cards, compliance trend, severity distribution"),
        ("Role-aware access and administration", "scrypt auth, RBAC, lockout, HMAC sessions, user admin"),
        ("Exports, documentation and deployment", "PDF/XLSX/JSON, README, Vercel serverless deployment"),
    ]
    y = 160
    for i, (title, deliv) in enumerate(phases):
        x = 90
        d.ellipse([x, y+18, x+70, y+88], fill=BLUE)
        s = str(i+1); wn = d.textbbox((0,0), s, font=fbs)[2]
        d.text((x+35-wn/2, y+35), s, font=fbs, fill="white")
        if i < len(phases)-1: d.line([x+35, y+92, x+35, y+110], fill=BLUE, width=4)
        d.rounded_rectangle([190, y, W-90, y+100], 12,
                            fill=(239,246,255) if i % 2 == 0 else (248,250,252),
                            outline=BORDER, width=2)
        d.text((215, y+16), title, font=fbs, fill=NAVY)
        d.text((215, y+56), deliv, font=fs, fill=(71,85,105))
        y += 112
    img.save(f"{OUT}/figure-3-1-phases.png")

fig_phases()
print("figures written:", sorted(os.listdir(OUT)))
