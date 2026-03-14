"""
Phase 6: Final Report Assembly — UrbanRoof DDR Style
Matches the exact visual style of the reference DDR:
- Dark hexagon cover page with yellow accents
- Black header band on every page with report title + green underline
- Yellow section headings with yellow rule
- Condition tables (Good/Moderate/Poor) with colour-coded checkmarks
- Side-by-side visual + thermal image pairs
- Footer: website | company | page number
"""

import os
import json
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdfcanvas
from pypdf import PdfWriter, PdfReader

# ── Brand colours ─────────────────────────────────────────────────────────────
BLACK      = colors.HexColor("#1A1A1A")
DARK_GREY  = colors.HexColor("#3A3A3A")
YELLOW     = colors.HexColor("#F5A623")
LIME       = colors.HexColor("#7CB342")
WHITE      = colors.white
LIGHT_GREY = colors.HexColor("#F5F5F5")
MID_GREY   = colors.HexColor("#CCCCCC")
TABLE_HEAD = colors.HexColor("#2C2C2C")
GOOD_COL   = colors.HexColor("#388E3C")
MOD_COL    = colors.HexColor("#F57C00")
POOR_COL   = colors.HexColor("#D32F2F")
BLUE_ROW   = colors.HexColor("#C8D8F0")
DARK_BLUE  = colors.HexColor("#1A3A6B")

PAGE_W, PAGE_H = A4
MARGIN     = 1.8 * cm
CONTENT_W  = PAGE_W - 2 * MARGIN


# ── Styles ────────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    s = {}
    s["section_title"] = ParagraphStyle("SecTitle", fontSize=15,
        textColor=BLACK, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=2, leading=19)
    s["subsection"] = ParagraphStyle("SubSec", fontSize=11,
        textColor=BLACK, fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=2, leading=14)
    s["sub2"] = ParagraphStyle("Sub2", fontSize=9.5,
        textColor=DARK_GREY, fontName="Helvetica-Bold",
        spaceBefore=6, spaceAfter=2, leading=13)
    s["body"] = ParagraphStyle("Body", fontSize=9,
        textColor=BLACK, fontName="Helvetica",
        leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
    s["body_bold"] = ParagraphStyle("BodyBold", fontSize=9,
        textColor=BLACK, fontName="Helvetica-Bold",
        leading=13, spaceAfter=3)
    s["bullet"] = ParagraphStyle("Bullet", fontSize=9,
        textColor=BLACK, fontName="Helvetica",
        leading=13, leftIndent=14, spaceAfter=2)
    s["yellow_label"] = ParagraphStyle("YLabel", fontSize=9,
        textColor=YELLOW, fontName="Helvetica-Bold",
        leading=13, spaceAfter=2)
    s["caption"] = ParagraphStyle("Caption", fontSize=7.5,
        textColor=DARK_GREY, fontName="Helvetica-Oblique",
        leading=10, alignment=TA_CENTER, spaceAfter=6)
    s["image_title"] = ParagraphStyle("ImgTitle", fontSize=8.5,
        textColor=BLACK, fontName="Helvetica-Bold",
        leading=12, spaceAfter=4, spaceBefore=8)
    s["table_header"] = ParagraphStyle("TblH", fontSize=8,
        textColor=WHITE, fontName="Helvetica-Bold",
        leading=11, alignment=TA_CENTER)
    s["table_cell"] = ParagraphStyle("TblC", fontSize=8,
        textColor=BLACK, fontName="Helvetica",
        leading=11, alignment=TA_LEFT)
    s["na"] = ParagraphStyle("NA", fontSize=8.5,
        textColor=MID_GREY, fontName="Helvetica-Oblique",
        leading=12, spaceAfter=3)
    s["disclaimer"] = ParagraphStyle("Disc", fontSize=8.5,
        textColor=BLACK, fontName="Helvetica-Oblique",
        leading=13, spaceAfter=5, alignment=TA_JUSTIFY)
    return s


# ── Page header/footer ────────────────────────────────────────────────────────
def draw_header_footer(canv, doc, report_title, address_line):
    canv.saveState()
    w, h = A4
    band_h = 1.1 * cm

    # Black header band
    canv.setFillColor(BLACK)
    canv.rect(0, h - band_h, w, band_h, fill=1, stroke=0)

    # Yellow left accent
    canv.setFillColor(YELLOW)
    canv.rect(0, h - band_h, 0.35*cm, band_h, fill=1, stroke=0)

    # Header text
    canv.setFillColor(WHITE)
    canv.setFont("Helvetica-Bold", 7.5)
    canv.drawString(0.6*cm, h - 0.44*cm, report_title[:70])
    canv.setFont("Helvetica", 7)
    canv.drawString(0.6*cm, h - 0.80*cm, address_line[:80])

    # Green underline of header
    canv.setStrokeColor(LIME)
    canv.setLineWidth(1.8)
    canv.line(0, h - band_h, w, h - band_h)

    # Footer line
    canv.setStrokeColor(LIME)
    canv.setLineWidth(0.8)
    canv.line(MARGIN, 1.15*cm, w - MARGIN, 1.15*cm)

    # Footer text
    canv.setFillColor(YELLOW)
    canv.setFont("Helvetica-BoldOblique", 7)
    canv.drawString(MARGIN, 0.65*cm, "www.urbanroof.in")

    canv.setFillColor(YELLOW)
    canv.setFont("Helvetica-Bold", 7)
    canv.drawCentredString(w/2, 0.65*cm, "UrbanRoof Private Limited")

    canv.setFillColor(DARK_GREY)
    canv.setFont("Helvetica", 7)
    canv.drawRightString(w - MARGIN, 0.65*cm, f"Page{doc.page}")

    canv.restoreState()


# ── Cover page ────────────────────────────────────────────────────────────────
def build_cover_page(cover_path, cover_info, property_name):
    c = pdfcanvas.Canvas(cover_path, pagesize=A4)
    w, h = A4

    # Dark background
    c.setFillColor(colors.HexColor("#2E2E2E"))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Black diagonal wedge (left/bottom)
    c.setFillColor(BLACK)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(w*0.6, 0)
    p.lineTo(0, h*0.42)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Yellow small triangle (bottom-left corner)
    c.setFillColor(YELLOW)
    p2 = c.beginPath()
    p2.moveTo(0, 0)
    p2.lineTo(w*0.20, 0)
    p2.lineTo(0, h*0.13)
    p2.close()
    c.drawPath(p2, fill=1, stroke=0)

    # Title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(w/2, h*0.69, "Detailed Diagnosis")
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(w/2, h*0.62, "Report")

    # Yellow underline
    c.setStrokeColor(YELLOW)
    c.setLineWidth(3)
    c.line(w*0.13, h*0.595, w*0.87, h*0.595)

    # Date & Report ID
    c.setFillColor(YELLOW)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(w*0.08, h*0.435, cover_info.get("report_date", ""))
    c.drawString(w*0.08, h*0.400, "Report ID  -")

    # Labels
    c.setFillColor(YELLOW)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(w*0.08, h*0.315, "Inspected & Prepared By:")
    c.drawString(w*0.54, h*0.315, "Prepared For:")

    # Values
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(w*0.08, h*0.282, cover_info.get("inspector", "Inspector"))

    # Wrap address
    addr = cover_info.get("prepared_for", property_name)
    words = addr.split()
    lines_addr = []
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Helvetica-Bold", 9.5) < w*0.38:
            line = test
        else:
            if line:
                lines_addr.append(line)
            line = word
    if line:
        lines_addr.append(line)

    yy = h*0.282
    for ln in lines_addr:
        c.drawString(w*0.54, yy, ln)
        yy -= 0.38*cm

    c.save()


# ── Reusable helpers ──────────────────────────────────────────────────────────
def yellow_rule():
    return HRFlowable(width="100%", thickness=2, color=YELLOW, spaceAfter=5)


def section_heading(title, styles):
    return [Paragraph(title, styles["section_title"]), yellow_rule(), Spacer(1, 3)]


def subsection_heading(title, styles):
    return [Paragraph(title, styles["subsection"]), Spacer(1, 2)]


def condition_table(rows, styles):
    CHECK = "\u2713"
    header_row = [
        Paragraph("Sr\nNo", styles["table_header"]),
        Paragraph("Input Type", styles["table_header"]),
        Paragraph("Good", ParagraphStyle("GH", fontSize=8, textColor=GOOD_COL,
            fontName="Helvetica-Bold", alignment=TA_CENTER, leading=11)),
        Paragraph("Moderate", ParagraphStyle("MH", fontSize=8, textColor=MOD_COL,
            fontName="Helvetica-Bold", alignment=TA_CENTER, leading=11)),
        Paragraph("Poor", ParagraphStyle("PH", fontSize=8, textColor=POOR_COL,
            fontName="Helvetica-Bold", alignment=TA_CENTER, leading=11)),
        Paragraph("Remarks", styles["table_header"]),
    ]
    data = [header_row]
    row_cmds = []
    for i, row in enumerate(rows):
        bg = LIGHT_GREY if i % 2 == 0 else WHITE
        row_cmds.append(("BACKGROUND", (0, i+1), (-1, i+1), bg))
        na_val = row.get("na", False)
        data.append([
            Paragraph(str(row.get("sr", i+1)), styles["table_cell"]),
            Paragraph(str(row.get("input", ""))[:90], styles["table_cell"]),
            Paragraph(CHECK if row.get("good") else "",
                ParagraphStyle("GC", fontSize=10, textColor=GOOD_COL,
                    fontName="Helvetica-Bold", alignment=TA_CENTER, leading=12)),
            Paragraph(CHECK if row.get("moderate") else "",
                ParagraphStyle("MC", fontSize=10, textColor=MOD_COL,
                    fontName="Helvetica-Bold", alignment=TA_CENTER, leading=12)),
            Paragraph("NA" if na_val else (CHECK if row.get("poor") else ""),
                ParagraphStyle("PC", fontSize=10 if not na_val else 8,
                    textColor=POOR_COL if not na_val else MID_GREY,
                    fontName="Helvetica-Bold", alignment=TA_CENTER, leading=12)),
            Paragraph(str(row.get("remarks", ""))[:80], styles["table_cell"]),
        ])
    col_w = [1.0*cm, 5.8*cm, 1.4*cm, 1.7*cm, 1.2*cm, 4.0*cm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    ts = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), TABLE_HEAD),
        ("GRID",          (0,0), (-1,-1), 0.4, MID_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ] + row_cmds)
    t.setStyle(ts)
    return t


def image_pair(v_path, t_path, caption, styles):
    half_w = (CONTENT_W - 0.6*cm) / 2
    max_h  = 6.5*cm
    elements = []
    if caption:
        elements.append(Paragraph(caption, styles["image_title"]))

    cells = []
    for path in [v_path, t_path]:
        if path and os.path.exists(path):
            try:
                img = Image(path, width=half_w, height=max_h, kind="proportional")
                img.hAlign = "CENTER"
                cells.append(img)
            except Exception:
                cells.append(Paragraph("Image Not Available", styles["na"]))
        else:
            cells.append(Paragraph("Image Not Available", styles["na"]))

    pt = Table([cells], colWidths=[half_w + 0.2*cm, half_w + 0.2*cm])
    pt.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 0.5, MID_GREY),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, MID_GREY),
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT_GREY),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    elements.append(pt)
    return elements


# ── Section builders ──────────────────────────────────────────────────────────
def build_introduction(sections, property_info, styles):
    elements = []
    elements += section_heading("SECTION 1   INTRODUCTION", styles)
    elements += subsection_heading("1.1  Background:", styles)
    s1 = sections.get("1. Property Issue Summary", "")
    for line in s1.split("\n"):
        line = line.strip()
        if line:
            elements.append(Paragraph(line, styles["body"]))
    elements.append(Spacer(1, 8))

    elements += subsection_heading("1.2  Objective of the Health Assessment", styles)
    for obj in [
        "To facilitate detection of all possible flaws, problems and occurrences that might exist and analyse cause effects of it.",
        "To prioritize the immediate repair and protection measures to be taken if any.",
        "To evaluate possibly accurate scope of work further to design estimate and cost analysis for execution/treatment.",
        "Classification of recommendations and solutions based on existing flaws and precautionary measures and its effective implementation.",
        "Tracking, record keeping during the life expectancy or the warranty period.",
    ]:
        elements.append(Paragraph(f"\u2022  {obj}", styles["bullet"]))
    elements.append(Spacer(1, 8))

    elements += subsection_heading("1.3  Scope of Work:", styles)
    elements.append(Paragraph(
        "Conducting visual site inspection using necessary assessment tools like Tapping Hammer, "
        "Crack gauge, IR Thermography, Moisture and pH meter to be carried out by the technical team "
        "involving skilled applicators on site.", styles["body"]))
    elements.append(PageBreak())

    elements += section_heading("SECTION 2   GENERAL INFORMATION", styles)
    elements += subsection_heading("2.1  Client & Inspection Details", styles)
    client_data = [
        ["Particular", "Description"],
        ["Customer Name:",      property_info.get("customer_name", "Not Available")],
        ["Property Address:",   property_info.get("address", "Not Available")],
        ["Date of Inspection:", property_info.get("inspection_date", date.today().strftime("%d/%m/%Y"))],
        ["Inspected By:",       property_info.get("inspector", "Not Available")],
        ["Type of Structure:",  property_info.get("structure_type", "Residential")],
        ["Report Generated:",   date.today().strftime("%d %B %Y")],
    ]
    ct = Table(client_data, colWidths=[5*cm, 13*cm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), TABLE_HEAD),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1),(0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT_GREY, WHITE]),
        ("GRID",          (0,0),(-1,-1), 0.5, MID_GREY),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    elements.append(ct)
    return elements


def build_observations(merged_records, styles):
    elements = []
    elements += section_heading("SECTION 3   VISUAL OBSERVATION AND READINGS", styles)

    # Leakage summary
    elements += subsection_heading("3.1  Sources of Leakage — Summary", styles)
    for idx, record in enumerate(merged_records):
        area = record.get("area_name", f"Area {idx+1}")
        insp = record.get("inspection") or {}
        obs = insp.get("observations") or []
        if obs:
            elements.append(Paragraph(f"{area.upper()}:", styles["body_bold"]))
            for ob in obs[:2]:
                elements.append(Paragraph(ob, styles["body"]))
            elements.append(Spacer(1, 4))

    elements.append(PageBreak())

    # Per-area details
    for idx, record in enumerate(merged_records):
        area    = record.get("area_name", f"Area {idx+1}")
        insp    = record.get("inspection") or {}
        therm   = record.get("thermal") or {}
        images  = record.get("images") or []
        conflicts = record.get("conflicts") or []

        sec_num = f"3.{idx+2}"
        elements += subsection_heading(f"{sec_num}  NEGATIVE SIDE INPUTS FOR {area.upper()}", styles)

        # Negative inputs as checkbox-style list
        neg_items = [
            ("No leakage",                  False),
            ("Dampness",                    "damp" in " ".join(insp.get("observations",[])).lower()),
            ("Seepage / Mild Leakage",      "seep" in " ".join(insp.get("observations",[])).lower()),
            ("Live Leakage (plumbing)",     "leak" in " ".join(insp.get("observations",[])).lower()),
        ]
        for label, checked in neg_items:
            mark = "\u2612" if checked else "\u2610"
            elements.append(Paragraph(f"  {mark}  {label}", styles["bullet"]))

        elements.append(Spacer(1, 6))
        elements += subsection_heading(f"  POSITIVE SIDE INPUTS FOR {area.upper()}", styles)

        pos_items = insp.get("defect_types") or []
        anomalies = therm.get("thermal_anomalies") or []
        all_pos = pos_items + anomalies
        if all_pos:
            for item in all_pos:
                elements.append(Paragraph(f"  \u2612  {item}", styles["bullet"]))
        else:
            elements.append(Paragraph("  \u2610  No positive inputs recorded.", styles["bullet"]))

        # Thermal readings
        readings = therm.get("temperature_readings") or {}
        if any(v is not None for v in readings.values()):
            parts = []
            for k, v in readings.items():
                if v is not None:
                    parts.append(f"{k.replace('_',' ').title()}: {v}°C")
            elements.append(Spacer(1, 4))
            elements.append(Paragraph("Thermal Readings: " + "  |  ".join(parts), styles["yellow_label"]))

        if conflicts:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph("\u26a0 Conflict Noted:", styles["body_bold"]))
            for c in conflicts:
                elements.append(Paragraph(f"  \u2192 {c}",
                    ParagraphStyle("CF", fontSize=8.5, textColor=POOR_COL,
                        fontName="Helvetica-Bold", leading=12, leftIndent=10)))

        elements.append(Spacer(1, 6))

        # Images side-by-side
        t_imgs = [i for i in images if i.get("source") == "thermal"]
        v_imgs = [i for i in images if i.get("source") == "inspection"]
        n_pairs = max(len(t_imgs), len(v_imgs))

        if n_pairs > 0:
            for pi in range(n_pairs):
                vp = v_imgs[pi]["file_path"] if pi < len(v_imgs) else None
                tp = t_imgs[pi]["file_path"] if pi < len(t_imgs) else None
                cap = f"IMAGE {idx+1}: {area.upper()} — Visual (Left) | Thermal (Right)"
                elements += image_pair(vp, tp, cap, styles)
                elements.append(Spacer(1, 6))
        else:
            elements.append(Paragraph("IMAGE: Not Available", styles["na"]))

        elements.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY,
            spaceBefore=8, spaceAfter=8))

    return elements


def build_condition_assessment(merged_records, styles):
    elements = []
    elements += section_heading("Structural Condition Assessment Tables", styles)

    SEV = {"low":0,"medium":1,"high":2,"critical":3,"unknown":1}

    for idx, record in enumerate(merged_records):
        area  = record.get("area_name", f"Area {idx+1}")
        insp  = record.get("inspection") or {}
        therm = record.get("thermal") or {}
        sev   = insp.get("severity_hint", "medium").lower()

        def to_cond(s):
            r = SEV.get(s, 1)
            return {"good": r==0, "moderate": r==1, "poor": r>=2}

        obs_list = insp.get("observations") or ["General condition"]
        rows = []
        for i, ob in enumerate(obs_list[:5]):
            cond = to_cond(sev)
            rows.append({"sr": i+1, "input": ob[:80],
                         "good": cond["good"], "moderate": cond["moderate"],
                         "poor": cond["poor"], "remarks": ""})

        anomalies = therm.get("thermal_anomalies") or []
        if anomalies:
            ts = therm.get("severity_hint","medium").lower()
            cond = to_cond(ts)
            rows.append({"sr": len(rows)+1,
                         "input": f"Thermal: {anomalies[0][:65]}",
                         "good": cond["good"], "moderate": cond["moderate"],
                         "poor": cond["poor"],
                         "remarks": therm.get("probable_cause_hint","")})

        elements += subsection_heading(f"{area} — Condition Input Table", styles)
        elements.append(condition_table(rows, styles))
        elements.append(Paragraph(
            "Good = No Action Needed   |   Moderate = Necessary Repairs Needed   |   Poor = Immediate Action Needed",
            ParagraphStyle("Legend", fontSize=7, textColor=DARK_GREY,
                fontName="Helvetica-Oblique", leading=10)))
        elements.append(Spacer(1, 12))

    return elements


def build_summary_table(merged_records, styles):
    elements = []
    elements += section_heading("4.3  Summary Table", styles)

    header = [
        Paragraph("Point\nNo", styles["table_header"]),
        Paragraph("Impacted area (-ve side)", styles["table_header"]),
        Paragraph("Point\nNo", styles["table_header"]),
        Paragraph("Exposed area (+ve side)", styles["table_header"]),
    ]
    data = [header]
    for i, record in enumerate(merged_records):
        insp  = record.get("inspection") or {}
        therm = record.get("thermal") or {}
        obs   = (insp.get("observations") or ["No issue observed"])
        anom  = (therm.get("thermal_anomalies") or ["No thermal anomaly"])
        pt    = f"4.{i+1}"
        data.append([
            Paragraph(pt, styles["table_cell"]),
            Paragraph(obs[0][:100], styles["table_cell"]),
            Paragraph(pt, styles["table_cell"]),
            Paragraph(anom[0][:100], styles["table_cell"]),
        ])

    t = Table(data, colWidths=[1.5*cm, 7.5*cm, 1.5*cm, 7.5*cm], repeatRows=1)
    row_cmds = [("BACKGROUND",(0,0),(-1,0), DARK_BLUE),
                ("TEXTCOLOR", (0,0),(-1,0), WHITE),
                ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold")]
    for i in range(1, len(data)):
        row_cmds.append(("BACKGROUND",(0,i),(-1,i), BLUE_ROW if i%2==1 else WHITE))
    t.setStyle(TableStyle([
        ("GRID",          (0,0),(-1,-1), 0.5, MID_GREY),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ] + row_cmds))
    elements.append(t)
    elements.append(Spacer(1, 10))
    return elements


def build_analysis(sections, styles):
    elements = []
    elements += section_heading("SECTION 4   ANALYSIS & SUGGESTIONS", styles)

    elements += subsection_heading("4.1  Actions Required & Suggested Therapies", styles)
    s5 = sections.get("5. Recommended Actions", "Not Available")
    for line in s5.split("\n"):
        line = line.strip().lstrip("-\u2022*# ").strip()
        if not line:
            elements.append(Spacer(1, 3))
        elif line.replace("*","").isupper() or line.startswith("**"):
            elements.append(Paragraph(line.replace("**",""), styles["sub2"]))
        else:
            elements.append(Paragraph(line, styles["body"]))

    elements.append(Spacer(1, 8))
    elements += subsection_heading("4.2  Further Possibilities Due to Delayed Action", styles)
    elements.append(Paragraph(
        "Delaying the recommended repairs may result in progressive structural deterioration, "
        "increased repair costs, potential health hazards due to mold and dampness, and reduction "
        "in the structural life of the property. Water ingress through unattended cracks may "
        "damage reinforcement steel, weaken RCC members, and cause irreversible damage to "
        "internal finishes and electrical fittings.", styles["body"]))

    elements.append(Spacer(1, 4))

    elements += build_summary_table([], styles)  # placeholder; overridden below

    elements += subsection_heading("4.4  Thermal References for Negative Side Inputs", styles)
    s3 = sections.get("3. Probable Root Cause", "Not Available")
    for line in s3.split("\n"):
        line = line.strip().lstrip("-\u2022*# ").strip()
        if line:
            elements.append(Paragraph(line, styles["body"]))

    elements.append(Spacer(1, 8))
    elements += subsection_heading("Severity Assessment", styles)
    s4 = sections.get("4. Severity Assessment", "")
    for line in s4.split("\n"):
        line = line.strip()
        if not line or line.startswith("|---"):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            elements.append(Paragraph(" | ".join(cells), styles["body"]))
        elif line:
            elements.append(Paragraph(line.lstrip("-\u2022*# ").strip(), styles["body"]))

    return elements


def build_limitation(styles):
    elements = []
    elements += section_heading("SECTION 5   LIMITATION AND PRECAUTION NOTE", styles)
    paras = [
        "Information provided in this report is a general overview of the most obvious repairs that may be needed. It is not intended to be an exhaustive list. The ultimate decision of what to repair or replace is the client's.",
        "The inspection is not technically exhaustive. The property inspection provides the client with a basic overview of the condition of the unit. There are many complex systems in the property that are not within the scope of the inspection.",
        "Some conditions noted, such as structural cracks and other signs of settlement indicate a potential problem that the structure of the building, or at least part of it, is overstressed. When such cracks suddenly develop or appear to widen and/or spread, the findings must be reported immediately to a Structural Engineer.",
        "THIS IS NOT A CODE COMPLIANCE INSPECTION. The Inspector does NOT try to determine whether or not any aspect of the property complies with any past, present or future codes such as building codes, regulations, laws, by-laws, ordinances or other regulatory requirements.",
        "The Inspector's Report is an opinion of the present condition of the property based on a visual examination of the readily accessible features. A property inspection does not include identifying defects that are hidden behind walls, floors, ceilings, or finishing surfaces.",
    ]
    for p in paras:
        elements.append(Paragraph(p, styles["disclaimer"]))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 8))
    elements += section_heading("Legal Disclaimer", styles)
    elements.append(Paragraph(
        "UrbanRoof (hereinafter 'INSPECTOR') has performed a visual and non-destructive test inspection "
        "of the property/structure and provides the CLIENT with an inspection report giving an opinion of "
        "the present condition of the property based on a visual and non-destructive examination of the "
        "readily accessible features and elements of the property. The inspection and report are performed "
        "and prepared for the use of CLIENT only. INSPECTOR accepts no responsibility for use or "
        "misinterpretation by third parties. This report is subject to copyrights. No part may be reproduced "
        "or transmitted in any form without written approval.", styles["disclaimer"]))
    return elements


# ── Main assembler ─────────────────────────────────────────────────────────────
def assemble_pdf(merged_records, sections, output_path, property_name="Site Inspection",
                 property_info=None):
    if property_info is None:
        property_info = {
            "customer_name": property_name, "address": property_name,
            "inspector": "AI-Assisted DDR System",
            "inspection_date": date.today().strftime("%d/%m/%Y"),
            "structure_type": "Residential Property"
        }

    print(f"\n[Phase 6] Assembling UrbanRoof-style DDR PDF...")
    styles  = build_styles()

    report_title = f"Detailed Diagnosis Report of {property_name}"
    address_line  = property_info.get("address", property_name)

    # Build story
    story = [Spacer(1, 0.3*cm)]
    story += build_introduction(sections, property_info, styles)
    story.append(PageBreak())

    # Disclaimer
    story += section_heading("Data and Information Disclaimer", styles)
    for para in [
        "This property inspection is not an exhaustive inspection of the structure, systems, or components. The inspection may not reveal all deficiencies. A health checkup helps to reduce some of the risk involved in the property/structure and premises, but it cannot eliminate these risks.",
        "It is recommended that you obtain as much information as is available about this property/structure, including any owners disclosures, previous inspection reports, engineering reports, building/remodeling permits, and reports performed for or by relocation companies, municipal inspection departments, lenders, insurers, and appraisers.",
        "An inspection addresses only those components and conditions that are present, visible, and accessible at the time of the inspection. The inspection report may address issues that are code based, however this is NOT a code compliance inspection.",
    ]:
        story.append(Paragraph(para, styles["disclaimer"]))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    story += build_observations(merged_records, styles)
    story.append(PageBreak())

    story += build_condition_assessment(merged_records, styles)
    story.append(PageBreak())

    # Analysis with real summary table
    story += section_heading("SECTION 4   ANALYSIS & SUGGESTIONS", styles)
    story += [Paragraph("4.1  Actions Required & Suggested Therapies", styles["subsection"])]
    s5 = sections.get("5. Recommended Actions", "Not Available")
    for line in s5.split("\n"):
        line = line.strip().lstrip("-\u2022*# ").strip()
        if not line:
            story.append(Spacer(1, 3))
        else:
            story.append(Paragraph(line, styles["body"]))

    story.append(Spacer(1, 8))
    story += [Paragraph("4.2  Further Possibilities Due to Delayed Action", styles["subsection"])]
    story.append(Paragraph(
        "Delaying repairs may result in progressive structural deterioration, increased repair costs, "
        "health hazards from mold/dampness, damage to reinforcement steel and RCC members.",
        styles["body"]))
    story.append(Spacer(1, 8))

    story += build_summary_table(merged_records, styles)
    story.append(PageBreak())

    story += section_heading("4.4  Thermal References for Negative Side Inputs", styles)
    s3 = sections.get("3. Probable Root Cause", "Not Available")
    for line in s3.split("\n"):
        line = line.strip().lstrip("-\u2022*# ").strip()
        if line:
            story.append(Paragraph(line, styles["body"]))

    story.append(PageBreak())
    story += section_heading("4.5  Visual References for Positive Side Inputs", styles)
    story.append(Paragraph(sections.get("6. Additional Notes", ""), styles["body"]))

    story.append(PageBreak())
    story += build_limitation(styles)

    story.append(PageBreak())
    story += section_heading("7. Missing or Unclear Information", styles)
    s7 = sections.get("7. Missing or Unclear Information", "All required data was available.")
    for line in s7.split("\n"):
        line = line.strip().lstrip("-\u2022*# ").strip()
        if line:
            story.append(Paragraph(line, styles["body"]))

    # Build content PDF
    content_path = output_path + "_content.pdf"
    doc = SimpleDocTemplate(content_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.6*cm, bottomMargin=1.9*cm,
        title="Detailed Diagnosis Report", author="DDR AI Pipeline")

    def on_page(canv, doc):
        draw_header_footer(canv, doc, report_title, address_line)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    # Build cover PDF
    cover_path = output_path + "_cover.pdf"
    cover_info = {
        "report_date":  date.today().strftime("%B %d, %Y"),
        "inspector":    property_info.get("inspector", "Inspector"),
        "prepared_for": property_info.get("address", property_name),
    }
    build_cover_page(cover_path, cover_info, property_name)

    # Merge cover + content
    writer = PdfWriter()
    for path in [cover_path, content_path]:
        reader = PdfReader(path)
        for pg in reader.pages:
            writer.add_page(pg)
    with open(output_path, "wb") as f:
        writer.write(f)

    # Cleanup
    for tmp in [cover_path, content_path]:
        try: os.remove(tmp)
        except: pass

    print(f"[Phase 6] DDR Report saved: {output_path}")


def run_phase6(merged_records, sections, output_dir="ddr_workspace",
               property_name="Site Inspection"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "DDR_Report.pdf")
    property_info = {
        "customer_name": property_name,
        "address": property_name,
        "inspector": "AI-Assisted DDR System",
        "inspection_date": date.today().strftime("%d/%m/%Y"),
        "structure_type": "Residential Property"
    }
    assemble_pdf(merged_records, sections, output_path, property_name, property_info)
    return output_path