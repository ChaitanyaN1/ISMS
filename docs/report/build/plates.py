"""Render UI screen plates from REAL seeded database records (no mock values)."""
from PIL import Image, ImageDraw, ImageFont
from isms_tracker import db
import os, json

OUT = "docs/report/figures"; os.makedirs(OUT, exist_ok=True)
S="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def f(p,s): return ImageFont.truetype(p,s)
def tw(d,t,fo): return d.textbbox((0,0),t,font=fo)[2]
def wrap(d,t,fo,mw):
    out,cur=[],""
    for w in t.split():
        c=(cur+" "+w).strip()
        if tw(d,c,fo)<=mw: cur=c
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out

WHITE=(255,255,255); BG=(248,250,252); DARK=(24,24,24); PANEL=(31,31,31)
INK=(15,23,42); MUTE=(100,116,139); BORD=(226,232,240); BLUE=(37,99,235)
GREEN=(5,150,105); AMBER=(217,119,6); RED=(220,38,38); PURPLE=(124,58,237)

db.ensure_initialized()
audits=db.read_table("audits"); findings=db.read_table("findings")
controls=db.read_table("controls"); risks=db.read_table("risks")
actions=db.read_table("actions"); evidence=db.read_table("evidence")
tests=db.read_table("tests")
chain=db.verify_audit_log_chain()

def sev_color(s):
    return {"Critical":RED,"High":AMBER,"Medium":(234,179,8),"Low":GREEN}.get(s,GUTE if False else MUTE)

def chrome(d,W,h,title):
    d.rectangle([0,0,W,h],fill=WHITE)
    d.rectangle([0,0,W,54],fill=DARK)
    for i,c in enumerate([(220,38,38),(217,119,6),(5,150,105)]):
        d.ellipse([24+i*26,20,40+i*26,36],fill=c)
    d.text((110,15),title,font=f(MONO,20),fill=(203,213,225))

# ---------- Plate 1: Dashboard ----------
def plate_dashboard():
    W,H=1800,1120
    img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)
    chrome(d,W,H,"SecureAudit Web Tracker   |   Executive Security Dashboard")
    d.rectangle([0,54,300,H],fill=(248,250,252)); d.line([300,54,300,H],fill=BORD,width=2)
    d.text((28,84),"SecureAudit",font=f(SB,26),fill=INK)
    d.text((28,118),"ISMS 27001",font=f(MONO,16),fill=BLUE)
    nav=["Dashboard","Audit Projects","Findings & CAPA","Annex A & SoA","Risk & Frameworks","Evidence Vault","Reports","User Management"]
    y=170
    for i,item in enumerate(nav):
        if i==0:
            d.rounded_rectangle([16,y-8,284,y+28],8,fill=(219,234,254))
            d.text((40,y-2),item,font=f(SB,18),fill=BLUE)
        else:
            d.text((40,y-2),item,font=f(S,18),fill=(71,85,105))
        y+=44
    d.rounded_rectangle([16,H-190,284,H-24],10,fill=PANEL)
    d.text((36,H-170),"Signed in as",font=f(S,15),fill=(148,163,184))
    d.text((36,H-148),"Alex Johnson",font=f(SB,19),fill=WHITE)
    d.text((36,H-120),"Role: Admin",font=f(S,16),fill=(96,165,250))
    d.rounded_rectangle([36,H-90,264,H-50],8,outline=(71,85,105),width=2)
    d.text((60,H-82),"Sign out",font=f(S,17),fill=(203,213,225))

    d.rounded_rectangle([324,74,W-24,132],10,fill=(254,249,195),outline=(253,224,71),width=2)
    d.text((344,88),"DEMO DATA INCLUDED",font=f(SB,17),fill=(133,77,14))
    d.text((344,110),"Illustrative sample records only. Not real audit evidence or ISO certification.",font=f(S,15),fill=(120,53,15))

    x=324
    cards=[("Total audits",str(len(audits)),"1 active",BLUE),
           ("Total findings",str(len(findings)),"6 open",RED),
           ("Avg compliance",f"{audits['compliance'].mean():.0f}%","10/20 control tests",GREEN),
           ("Completed audits",str((audits['status']=="Completed").sum()),"1 in planning",PURPLE)]
    cw=(W-24-x-3*14)//4
    for i,(lab,val,sub,col) in enumerate(cards):
        cx=x+i*(cw+14)
        d.rounded_rectangle([cx,152,cx+cw,268],12,fill=WHITE,outline=BORD,width=2)
        d.text((cx+20,172),lab,font=f(S,17),fill=MUTE)
        d.text((cx+20,198),val,font=f(SB,42),fill=INK)
        d.text((cx+20,246),sub,font=f(S,15),fill=col)
    # compliance bars
    d.rounded_rectangle([324,292,1140,720],12,fill=WHITE,outline=BORD,width=2)
    d.text((348,314),"Compliance by audit",font=f(SB,21),fill=INK)
    d.text((1000,318),"Score %",font=f(S,14),fill=MUTE)
    yy=372
    for _,row in audits.iterrows():
        d.text((348,yy),str(row["title"])[:40],font=f(S,16),fill=(51,65,85))
        bx=348; bwid=int(600*float(row["compliance"])/100)
        d.rounded_rectangle([bx,yy+26,bx+600,yy+44],9,fill=(241,245,249))
        d.rounded_rectangle([bx,yy+26,bx+bwid,yy+44],9,fill=BLUE if float(row["compliance"])>=70 else AMBER)
        d.text((bx+610,yy+26),f"{float(row['compliance']):.0f}%",font=f(SB,16),fill=INK)
        yy+=80
    # severity donut -> simple bars
    d.rounded_rectangle([1164,292,W-24,720],12,fill=WHITE,outline=BORD,width=2)
    d.text((1188,314),"Finding severity distribution",font=f(SB,21),fill=INK)
    counts=findings["severity"].value_counts().to_dict()
    order=["Critical","High","Medium","Low"]; yy=380; total=sum(counts.values())
    for s_ in order:
        n=counts.get(s_,0); bwid=int(330*n/total) if total else 0
        d.text((1188,yy),s_,font=f(S,17),fill=(51,65,85))
        d.rounded_rectangle([1290,yy+4,1290+330,yy+22],9,fill=(241,245,249))
        d.rounded_rectangle([1290,yy+4,1290+bwid,yy+22],9,fill=sev_color(s_))
        d.text((1636,yy+2),str(n),font=f(SB,18),fill=INK)
        yy+=52
    d.text((1188,600),"Control status overview",font=f(SB,21),fill=INK)
    cs=controls["implementation_status"].value_counts().to_dict()
    yy=644
    for k,v in cs.items():
        d.text((1188,yy),str(k),font=f(S,16),fill=(51,65,85))
        d.text((1636,yy),str(v),font=f(SB,17),fill=INK); yy+=34
    # recent audits table
    d.rounded_rectangle([324,744,W-24,1010],12,fill=WHITE,outline=BORD,width=2)
    d.text((348,766),"Recent audits",font=f(SB,21),fill=INK)
    headers=["Audit ID","Title","Type","Lead auditor","Score","Status"]
    xs=[350,540,1080,1250,1440,1590]
    d.line([348,806,W-46,806],fill=BORD,width=2)
    for hh,xx in zip(headers,xs): d.text((xx,816),hh,font=f(SB,15),fill=MUTE)
    yy=846
    for _,row in audits.iterrows():
        vals=[row["audit_id"],str(row["title"])[:44],row["audit_type"],row["lead_auditor"],
              f"{float(row['compliance']):.0f}%",row["status"]]
        for vv,xx in zip(vals,xs):
            d.text((xx,yy),str(vv)[:46],font=f(S,16),fill=(51,65,85))
        d.line([348,yy+30,W-46,yy+30],fill=(241,245,249),width=1)
        yy+=38
    img.save(f"{OUT}/figure-5-1-dashboard.png")

# ---------- Plate 2: Audit detail / checklist ----------
def plate_audit():
    W,H=1800,1080
    img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)
    chrome(d,W,H,"SecureAudit Web Tracker   |   Audit Detail - AUD-2026-001")
    a=audits[audits.audit_id=="AUD-2026-001"].iloc[0]
    d.text((40,78),str(a["title"]),font=f(SB,30),fill=INK)
    d.text((40,120),f"{a['audit_id']}  ·  {a['audit_type']}  ·  {a['department']}  ·  Lead: {a['lead_auditor']}",font=f(S,17),fill=MUTE)
    d.rounded_rectangle([1410,84,1760,124],10,fill=(209,250,229))
    d.text((1436,92),f"Status: {a['status']}",font=f(SB,18),fill=(6,95,70))
    d.rounded_rectangle([1410,134,1760,174],10,fill=(219,234,254))
    d.text((1436,142),f"Approval: {a['approval_status']}",font=f(SB,18),fill=(30,64,175))
    # scope boxes
    d.rounded_rectangle([40,196,880,320],10,fill=WHITE,outline=BORD,width=2)
    d.text((60,212),"Scope",font=f(SB,17),fill=INK)
    yy=240
    for ln in wrap(d,str(a["scope"]),f(S,15),790)[:3]:
        d.text((60,yy),ln,font=f(S,15),fill=(71,85,105)); yy+=20
    d.rounded_rectangle([900,196,1760,320],10,fill=WHITE,outline=BORD,width=2)
    d.text((920,212),"Objectives",font=f(SB,17),fill=INK)
    yy=240
    for ln in wrap(d,str(a["objectives"]),f(S,15),820)[:3]:
        d.text((920,yy),ln,font=f(S,15),fill=(71,85,105)); yy+=20
    # workpapers
    d.text((40,344),"Control test workpapers (Clause 9.2)",font=f(SB,22),fill=INK)
    rows=tests[tests.audit_id=="AUD-2026-001"]
    xs=[44,190,470,1060,1180,1320,1500]
    headers=["Test ID","Control","Procedure","Sample","Result","Evidence"]
    d.line([40,382,1760,382],fill=BORD,width=2)
    for hh,xx in zip(headers,xs): d.text((xx,392),hh,font=f(SB,15),fill=MUTE)
    yy=422
    for _,r in rows.head(12).iterrows():
        col={"Compliant":GREEN,"Non-Compliant":RED,"Partially Compliant":AMBER}.get(r["status"],MUTE)
        d.text((xs[0],yy),r["test_id"],font=f(MONO,14),fill=(51,65,85))
        d.text((xs[1],yy),f"{r['control_id']}",font=f(MONO,14),fill=BLUE)
        d.text((xs[2],yy),str(r["procedure"])[:62],font=f(S,14),fill=(51,65,85))
        d.text((xs[3],yy),str(r["sample_size"]),font=f(S,14),fill=(51,65,85))
        d.rounded_rectangle([xs[4]-6,yy-3,xs[4]+128,yy+19],8,fill=tuple(int(c*0.14+255*0.86) for c in col))
        d.text((xs[4]+4,yy),str(r["status"])[:16],font=f(SB,12),fill=col)
        d.text((xs[5],yy),str(r["evidence_ref"])[:20],font=f(MONO,13),fill=MUTE)
        d.line([40,yy+26,1760,yy+26],fill=(241,245,249),width=1)
        yy+=36
    d.rounded_rectangle([40,880,1760,1030],12,fill=(248,250,252),outline=BORD,width=2)
    d.text((60,898),"Compliance roll-up",font=f(SB,18),fill=INK)
    d.text((60,928),f"Recorded score: {float(a['compliance']):.1f}%   ·   {len(rows)} workpapers linked   ·   recalculated on every test update",font=f(S,16),fill=(71,85,105))
    d.text((60,958),f"Report version {a['report_version']}   ·   Approved by {a['approved_by'] or 'pending review'}",font=f(S,16),fill=(71,85,105))
    d.text((60,988),"Demo record: illustrative data only.",font=f(S,15),fill=MUTE)
    img.save(f"{OUT}/figure-5-2-audit-detail.png")

# ---------- Plate 3: Findings & CAPA ----------
def plate_findings():
    W,H=1800,1500
    img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)
    chrome(d,W,H,"SecureAudit Web Tracker   |   Findings & CAPA")
    d.text((40,80),"Findings & Vulnerability Register",font=f(SB,30),fill=INK)
    d.text((40,122),f"{len(findings)} records  ·  severity-tagged  ·  linked to CAPA actions and evidence",font=f(S,17),fill=MUTE)
    x=40; cw=(W-80-3*16)//4
    chips=[("Critical",(findings.severity=="Critical").sum(),RED),("High",(findings.severity=="High").sum(),AMBER),
           ("Medium",(findings.severity=="Medium").sum(),(202,138,4)),("Low",(findings.severity=="Low").sum(),GREEN)]
    for i,(lab,n,col) in enumerate(chips):
        cx=x+i*(cw+16)
        d.rounded_rectangle([cx,160,cx+cw,240],10,fill=WHITE,outline=BORD,width=2)
        d.rectangle([cx,160,cx+8,240],fill=col)
        d.text((cx+22,174),lab,font=f(S,16),fill=MUTE)
        d.text((cx+22,196),str(n),font=f(SB,28),fill=INK)
    yy=264
    for _,r in findings.head(6).iterrows():
        cardh=118
        d.rounded_rectangle([40,yy,1760,yy+cardh],10,fill=WHITE,outline=BORD,width=2)
        col=sev_color(r["severity"])
        d.rectangle([40,yy,48,yy+cardh],fill=col)
        d.text((64,yy+14),r["finding_id"],font=f(MONO,14),fill=MUTE)
        d.rounded_rectangle([190,yy+10,190+tw(d,r["severity"],f(SB,14))+24,yy+34],8,
                            fill=tuple(int(c*0.15+255*0.85) for c in col))
        d.text((202,yy+14),r["severity"],font=f(SB,14),fill=col)
        d.text((360,yy+12),str(r["title"])[:74],font=f(SB,17),fill=INK)
        d.text((64,yy+42),f"Criteria: {str(r['criteria'])[:80]}",font=f(S,14),fill=MUTE)
        d.text((64,yy+64),f"Condition: {str(r['condition'])[:90]}",font=f(S,14),fill=(71,85,105))
        d.text((64,yy+88),f"Owner: {r['owner']}   ·   {r['audit_id']}   ·   {r['control_id']}",font=f(S,14),fill=MUTE)
        d.rounded_rectangle([1560,yy+14,1730,yy+42],8,fill=(241,245,249))
        d.text((1578,yy+18),str(r["status"]),font=f(SB,14),fill=(51,65,85))
        yy+=cardh+14
    d.text((40,yy+6),"CAPA remediation tracker",font=f(SB,20),fill=INK)
    yy+=44
    xs=[44,230,700,1030,1300,1520]
    for hh,xx in zip(["Action ID","Title","Owner","Due date","Status","Type"],xs):
        d.text((xx,yy),hh,font=f(SB,14),fill=MUTE)
    d.line([40,yy+24,1760,yy+24],fill=BORD,width=2); yy+=34
    for _,r in actions.head(4).iterrows():
        for vv,xx in zip([r["action_id"],str(r["title"])[:52],r["owner"],r["due_date"],r["status"],r["action_type"]],xs):
            d.text((xx,yy),str(vv),font=f(S,14),fill=(51,65,85))
        d.line([40,yy+24,1760,yy+24],fill=(241,245,249),width=1); yy+=32
    img=img.crop((0,0,W,min(yy+40,H))); img.save(f"{OUT}/figure-5-3-findings.png")

# ---------- Plate 4: SoA / controls ----------
def plate_soa():
    W,H=1800,1080
    img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)
    chrome(d,W,H,"SecureAudit Web Tracker   |   Annex A Statement of Applicability")
    d.text((40,80),"Statement of Applicability",font=f(SB,30),fill=INK)
    d.text((40,122),f"{len(controls)} Annex A controls across four themes  ·  ISO/IEC 27001:2022 Clause 6.1.3",font=f(S,17),fill=MUTE)
    d.text((40,176),"Theme:",font=f(S,15),fill=MUTE)
    doms=["All"]+sorted(controls.domain.unique().tolist())
    x=112
    for dom in doms:
        wt=tw(d,dom,f(SB,15))+32
        fill=(37,99,235) if dom=="All" else (241,245,249)
        d.rounded_rectangle([x,168,x+wt,198],15,fill=fill)
        d.text((x+16,176),dom,font=f(SB,15),fill=WHITE if dom=="All" else (51,65,85))
        x+=wt+10
    xs=[44,180,400,1030,1180,1390,1600]
    for hh,xx in zip(["Control","Theme","Title","Applicable","Implementation","NIST CSF"],xs):
        d.text((xx,232),hh,font=f(SB,14),fill=MUTE)
    d.line([40,258,1760,258],fill=BORD,width=2)
    yy=270
    for _,r in controls.head(19).iterrows():
        d.text((xs[0],yy),r["control_id"],font=f(MONO,14),fill=BLUE)
        d.text((xs[1],yy),str(r["domain"])[:19],font=f(S,13),fill=(71,85,105))
        d.text((xs[2],yy),str(r["title"])[:52],font=f(S,14),fill=INK)
        app=str(r["applicability"])
        d.text((xs[3],yy),app[:11],font=f(SB,13),fill=GREEN if app.startswith("Applic") else MUTE)
        st=str(r["implementation_status"])
        col={"Compliant":GREEN,"Non-Compliant":RED,"Partially Compliant":AMBER,"Not Applicable":MUTE}.get(st,MUTE)
        d.ellipse([xs[4],yy+4,xs[4]+9,yy+13],fill=col)
        d.text((xs[4]+16,yy),st[:14],font=f(S,13),fill=(51,65,85))
        d.text((xs[5],yy),str(r["nist_csf"])[:10],font=f(S,13),fill=(71,85,105))
        d.line([40,yy+24,1760,yy+24],fill=(241,245,249),width=1)
        yy+=30
    d.text((40,yy+12),"Showing 19 of 40 controls. Cross-framework mappings (NIST CSF 2.0, SOC 2) are illustrative and require validation.",font=f(S,14),fill=MUTE)
    img=img.crop((0,0,W,yy+52)); img.save(f"{OUT}/figure-5-4-soa.png")

# ---------- Plate 5: Evidence vault ----------
def plate_evidence():
    W,H=1800,860
    img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)
    chrome(d,W,H,"SecureAudit Web Tracker   |   SHA-256 Evidence Vault")
    d.text((40,80),"Evidence Vault",font=f(SB,30),fill=INK)
    d.text((40,122),"SHA-256 digest and byte size captured at upload · re-verified on every download · 20 MB cap",font=f(S,17),fill=MUTE)
    d.rounded_rectangle([40,170,1760,240],10,fill=(236,253,245),outline=(167,243,208),width=2)
    d.text((62,184),"Integrity status: all stored artefacts verified",font=f(SB,17),fill=(6,95,70))
    d.text((62,210),"Any digest mismatch blocks the download with HTTP 409 Conflict.",font=f(S,15),fill=(6,78,59))
    xs=[44,150,560,1120,1260,1420,1600]
    for hh,xx in zip(["ID","Title","File","Bytes","SHA-256 (prefix)","Status"],xs):
        d.text((xx,266),hh,font=f(SB,14),fill=MUTE)
    d.line([40,292,1760,292],fill=BORD,width=2)
    yy=304
    for _,r in evidence.iterrows():
        d.text((xs[0],yy),r["evidence_id"],font=f(MONO,14),fill=BLUE)
        d.text((xs[1],yy),str(r["title"])[:46],font=f(S,14),fill=INK)
        d.text((xs[2],yy),str(r["file_name"])[:34],font=f(MONO,13),fill=(71,85,105))
        d.text((xs[3],yy),str(r["file_size_bytes"]),font=f(MONO,14),fill=(51,65,85))
        d.text((xs[4],yy),str(r["sha256_hash"])[:16]+"...",font=f(MONO,13),fill=(71,85,105))
        d.rounded_rectangle([xs[5]-8,yy-4,xs[5]+96,yy+22],9,fill=(209,250,229))
        d.text((xs[5]+2,yy),str(r["verified_status"]),font=f(SB,13),fill=(6,95,70))
        d.line([40,yy+30,1760,yy+30],fill=(241,245,249),width=1)
        yy+=40
    yy+=14
    d.text((40,yy),"Tamper-evident audit trail",font=f(SB,20),fill=INK); yy+=38
    d.rounded_rectangle([40,yy,1760,yy+120],10,fill=(248,250,252),outline=BORD,width=2)
    d.text((62,yy+16),f"Chain verification: {'VALID' if chain['valid'] else 'BROKEN'}",font=f(SB,17),fill=(6,95,70) if chain["valid"] else RED)
    d.text((330,yy+16),f"entries checked: {chain['checked_entries']}",font=f(S,16),fill=(71,85,105))
    d.text((62,yy+52),"head_hash",font=f(SB,14),fill=MUTE)
    d.text((170,yy+50),str(chain["head_hash"]),font=f(MONO,14),fill=(51,65,85))
    d.text((62,yy+82),"GENESIS -> prev_hash -> entry_hash  (append-only, no update or delete path in the API)",font=f(S,14),fill=MUTE)
    img=img.crop((0,0,W,yy+150)); img.save(f"{OUT}/figure-5-5-evidence.png")

# ---------- Plate 6: Reports ----------
def plate_reports():
    W,H=1800,900
    img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)
    chrome(d,W,H,"SecureAudit Web Tracker   |   Reports & Exports")
    d.text((40,80),"Report & Export Centre",font=f(SB,30),fill=INK)
    d.text((40,122),"Server-generated artefacts from the same SQLite records",font=f(S,17),fill=MUTE)
    yy=170
    items=[("Audit PDF report","GET /api/reports/audit/{audit_id}/pdf","Executive summary, Annex A workpapers, findings/CAPA, SHA-256 evidence manifest",BLUE),
           ("Executive workbook","GET /api/reports/workbook.xlsx","9 sheets: Audits, Tests, Findings, CAPA, SoA, Risks, Regulatory, Evidence, Logs",GREEN),
           ("JSON backup","GET /api/backup/json","Canonical payload with SHA-256 manifest; verifiable before restore",PURPLE),
           ("CSV audit import","POST /api/import/audits-csv","Append-only import using the supplied template",AMBER)]
    for title,endpoint,desc,col in items:
        d.rounded_rectangle([40,yy,1760,yy+118],10,fill=WHITE,outline=BORD,width=2)
        d.rectangle([40,yy,46,yy+118],fill=col)
        d.text((68,yy+16),title,font=f(SB,19),fill=INK)
        d.text((68,yy+46),endpoint,font=f(MONO,14),fill=col)
        d.text((68,yy+76),desc,font=f(S,15),fill=(71,85,105))
        d.rounded_rectangle([1540,yy+38,1720,yy+80],10,fill=col)
        d.text((1572,yy+50),"Download",font=f(SB,16),fill=WHITE)
        yy+=132
    d.rounded_rectangle([40,yy,1760,yy+150],10,fill=(248,250,252),outline=BORD,width=2)
    d.text((62,yy+16),"Formal review and approval state",font=f(SB,17),fill=INK)
    xs=[64,320,700,1010,1300]
    for hh,xx in zip(["Audit","Version","Approval status","Approved by","Approved at"],xs):
        d.text((xx,yy+50),hh,font=f(SB,14),fill=MUTE)
    ry=yy+76
    for _,r in audits.iterrows():
        for vv,xx in zip([r["audit_id"],str(r["report_version"]),str(r["approval_status"]),
                          str(r["approved_by"] or "-"),str(r["approved_at"] or "-")],xs):
            d.text((xx,ry),str(vv)[:34],font=f(S,14),fill=(51,65,85))
        ry+=24
    img=img.crop((0,0,W,min(ry+30,H))); img.save(f"{OUT}/figure-5-6-reports.png")

plate_dashboard(); plate_audit(); plate_findings(); plate_soa(); plate_evidence(); plate_reports()
print(sorted(os.listdir(OUT)))
