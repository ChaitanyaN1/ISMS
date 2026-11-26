from PIL import Image, ImageDraw, ImageFont
import os
OUT = "docs/report/figures"; os.makedirs(OUT, exist_ok=True)
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NAVY=(15,23,42); BLUE=(37,99,235); GREEN=(5,150,105); AMBER=(180,83,9); RED=(185,28,28)
GREY=(100,116,139); LIGHT=(248,250,252); BORDER=(203,213,225); INK=(51,65,85)
def f(p,s): return ImageFont.truetype(p,s)
def tw(d,t,fo): return d.textbbox((0,0),t,font=fo)[2]
def wrap(d,text,fo,maxw):
    out,cur=[],""
    for w in text.split():
        t=(cur+" "+w).strip()
        if tw(d,t,fo)<=maxw: cur=t
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out

def card(d, x, y, w, title, lines, fill, border, fs_=22):
    ft=f(SANS_B,25); fb=f(SANS,fs_)
    pad=22; inner=w-2*pad
    wrapped=[wrap(d,l,fb,inner-16) for l in lines]
    hdr=52
    h = hdr+pad+sum(len(ww)*30 for ww in wrapped)+pad
    d.rounded_rectangle([x,y,x+w,y+h],14,fill=fill,outline=border,width=3)
    d.rounded_rectangle([x,y,x+w,y+hdr],14,fill=border)
    d.rectangle([x,y+hdr-14,x+w,y+hdr],fill=border)
    d.text((x+pad,y+13),title,font=ft,fill="white")
    yy=y+hdr+pad-6
    for ww in wrapped:
        for k,sub in enumerate(ww):
            if k==0:
                d.ellipse([x+pad+2,yy+9,x+pad+8,yy+15],fill=INK)
                d.text((x+pad+18,yy),sub,font=fb,fill=INK)
            else:
                d.text((x+pad+18,yy),sub,font=fb,fill=INK)
            yy+=30
    return h

def title(d, x, y, text, sub=None):
    ft=f(SERIF_B,38)
    d.text((x,y),text,font=ft,fill=NAVY)
    d.line([x,y+54,x+1560,y+54],fill=BLUE,width=4)
    if sub:
        d.text((x,y+70),sub,font=f(SANS,22),fill=GREY)
        return y+112
    return y+90

# ============ FIG 3.1 ARCHITECTURE (tier bands) ============
W=1900
img=Image.new("RGB",(W,1500),"white"); d=ImageDraw.Draw(img)
y=title(d,70,44,"Figure 4.1  SecureAudit ISMS three-tier architecture",
        "Each tier is independently deployable; the shared core package keeps both interfaces consistent.")
layers=[
 ("PRESENTATION TIER", BLUE, (239,246,255), (37,99,235), [
   ("React + TypeScript SPA (Vite)", ["Landing page, role sign-in, dashboard, audits, findings and CAPA,","Annex A SoA, 5x5 risk register, evidence vault, reports","Static bundle served at https://isms1.vercel.app"]),
   ("Streamlit Governance Workbench", ["8 analytical pages for workpapers, registers and administration","Append-only CSV import, verified JSON backup, user admin","Local runtime on port 8501, same core package"])]),
 ("APPLICATION TIER", NAVY, (241,245,249), (71,85,105), [
   ("FastAPI service (api_server.py v2.0.0)", ["27 REST endpoints across auth, workspace, audits, tests, findings, CAPA,","controls, risks, evidence, reports, backup, import, demo, users and logs","Stateless HMAC-SHA256 bearer tokens with an RBAC dependency guard","Serverless entry point api/index.py on the Vercel Python runtime"]),
   ("isms_tracker core package", ["db.py - schema, CRUD, seeding, hash-chained log","security.py - scrypt KDF, lockout, HMAC, SHA-256","catalogue.py - ISO 27001:2022 reference data","reports.py - FPDF2 and OpenPyXL builders"])]),
 ("DATA TIER", RED, (254,242,242), (185,28,28), [
   ("SQLite database", ["12 tables: users, sessions, audits, tests, findings, actions, meta,","controls, risks, requirements, evidence, audit_logs","data/isms_tracker.db locally; /tmp/isms_vercel on Vercel"]),
   ("Controlled evidence store", ["SHA-256 digest and byte size recorded at upload","20 MB cap, MIME and extension allowlist, re-verified on download","data/uploads, overridable with ISMS_UPLOADS_DIR"])]),
]
for i,(label,labcol,fill,border,cards) in enumerate(layers):
    d.text((70,y+6),label,font=f(SANS_B,22),fill=labcol)
    cy=y+42; maxh=0
    cw=(W-140-40)//2
    for j,(t,ls) in enumerate(cards):
        h=card(d,70+j*(cw+40),cy,cw,t,ls,fill,border)
        maxh=max(maxh,h)
    y=cy+maxh+22
    if i<2:
        cx=W//2
        d.line([cx,y-6,cx,y+28],fill=GREY,width=5)
        d.polygon([(cx,y+40),(cx-9,y+20),(cx+9,y+20)],fill=GREY)
        y+=52
img=img.crop((0,0,W,y+30)); img.save(f"{OUT}/figure-4-1-architecture.png")

# ============ FIG 4.1 WORKFLOW ============
W=1900
img=Image.new("RGB",(W,860),"white"); d=ImageDraw.Draw(img)
y=title(d,70,44,"Figure 4.3  Seven-stage audit traceability model",
        "Each stage writes a record that carries the identifier of the stage before it.")
stages=[("1","Scope","audit_id, scope, objectives, criteria"),
        ("2","Controls","Annex A selection, SoA applicability"),
        ("3","Test","procedure, sample size, result, notes"),
        ("4","Evidence","SHA-256 digest, byte size, verifier"),
        ("5","Finding","criteria vs condition, cause, impact"),
        ("6","CAPA","owner, due date, verification note"),
        ("7","Report","PDF / XLSX, approval, log chain")]
n=len(stages); bw=250; gap=24; x0=(W-(n*bw+(n-1)*gap))//2; by=y+40
fsb=f(SANS,19)
for i,(num,name,sub) in enumerate(stages):
    x=x0+i*(bw+gap)
    d.rounded_rectangle([x,by,x+bw,by+320],14,fill=(239,246,255) if i%2==0 else (240,253,244),outline=BLUE,width=3)
    d.ellipse([x+bw//2-30,by+22,x+bw//2+30,by+82],fill=BLUE)
    wn=tw(d,num,f(SERIF_B,30)); d.text((x+bw//2-wn//2,by+32),num,font=f(SERIF_B,30),fill="white")
    nn=f(SANS_B,24); d.text((x+bw//2-tw(d,name,nn)//2,by+98),name,font=nn,fill=NAVY)
    yy=by+145
    for ln in wrap(d,sub,fsb,bw-30):
        d.text((x+bw//2-tw(d,ln,fsb)//2,yy),ln,font=fsb,fill=(71,85,105)); yy+=27
    if i<n-1:
        d.line([x+bw+3,by+150,x+bw+gap-5,by+150],fill=GREY,width=5)
        d.polygon([(x+bw+gap-1,by+150),(x+bw+gap-15,by+143),(x+bw+gap-15,by+157)],fill=GREY)
by2=by+370
d.rounded_rectangle([200,by2,W-200,by2+150],14,fill=LIGHT,outline=BORDER,width=3)
d.text((230,by2+20),"Traceability keys carried through every stage",font=f(SANS_B,24),fill=NAVY)
d.text((230,by2+62),"audit_id  ->  test_id  ->  control_id  ->  evidence_id  ->  finding_id  ->  action_id",font=f(SANS,25),fill=BLUE)
d.text((230,by2+106),"Every mutation is appended to the SHA-256 hash chain:  GENESIS -> prev_hash -> entry_hash",font=f(SANS,22),fill=INK)
img=img.crop((0,0,W,by2+190)); img.save(f"{OUT}/figure-4-3-workflow.png")

# ============ FIG 4.2 ER (clean grid) ============
W,H=1900,1330
img=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(img)
title(d,70,44,"Figure 4.2  Entity relationship model of the ISMS schema")
tables={
 "users":(70,165,["PK user_id","username","password_hash","role","failed_attempts"]),
 "audits":(490,165,["PK audit_id","title, scope","lead_auditor","status","approval_status"]),
 "controls":(910,165,["PK control_id","domain","title","applicable","implementation"]),
 "risks":(1330,165,["PK risk_id","likelihood, impact","treatment","residual_level","FK control_id"]),
 "sessions":(70,555,["PK token","FK user_id","created_at","expires_at"]),
 "tests":(490,555,["PK test_id","FK audit_id","FK control_id","sample_size","result"]),
 "findings":(910,555,["PK finding_id","FK audit_id","FK control_id","severity, status","root_cause"]),
 "actions":(1330,555,["PK action_id","FK finding_id","owner, due_date","status"]),
 "audit_logs":(70,955,["PK log_id","timestamp, actor","action, entity_id","prev_hash, entry_hash"]),
 "evidence":(490,955,["PK evidence_id","entity_type + id","sha256_hash","file_size_bytes"]),
 "requirements":(910,955,["PK req_id","framework","reference","mapping"]),
 "meta_state":(1330,955,["PK key","value","",""]),
}
TW=340; pos={}
for name,(x,yy,fields) in tables.items():
    fields=[x_ for x_ in fields if x_]
    h=52+len(fields)*32+14
    d.rounded_rectangle([x,yy,x+TW,yy+h],10,fill=(248,250,252),outline=BORDER,width=3)
    d.rounded_rectangle([x,yy,x+TW,yy+50],10,fill=BLUE,outline=BLUE)
    d.rectangle([x,yy+40,x+TW,yy+50],fill=BLUE)
    d.text((x+18,yy+13),name,font=f(SANS_B,24),fill="white")
    fyy=yy+62
    for fl in fields:
        d.text((x+18,fyy),fl,font=f(SANS,20),fill=INK); fyy+=32
    pos[name]=(x,yy,TW,h)

def varrow(a,b):
    ax,ay,aw,ah=pos[a]; bx,byy,bw,bh=pos[b]
    x=ax+aw//2; y1=ay+ah; y2=byy
    d.line([x,y1,x,y2-10],fill=GREY,width=4)
    d.polygon([(x,y2-2),(x-9,y2-18),(x+9,y2-18)],fill=GREY)
def harrow(a,b):
    ax,ay,aw,ah=pos[a]; bx,byy,bw,bh=pos[b]
    y=ay+ah//2; x1=ax+aw; x2=bx
    d.line([x1,y,x2-10,y],fill=GREY,width=4)
    d.polygon([(x2-2,y),(x2-18,y-9),(x2-18,y+9)],fill=GREY)
varrow("users","sessions"); varrow("sessions","audit_logs")
varrow("audits","tests");   varrow("tests","evidence")
harrow("controls","risks"); harrow("tests","findings"); harrow("findings","actions")
d.text((70,1290),"PK = primary key    FK = application-enforced reference    Arrows show the traceability path from audit through tests and findings to actions",
       font=f(SANS,20),fill=GREY)
img.save(f"{OUT}/figure-4-2-er-model.png")
print("done", sorted(os.listdir(OUT)))
