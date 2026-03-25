from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

# ─────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1a2e4a")
MID_BLUE    = colors.HexColor("#2563eb")
LIGHT_BLUE  = colors.HexColor("#dbeafe")
CODE_BG     = colors.HexColor("#f1f5f9")
CODE_BORDER = colors.HexColor("#cbd5e1")
GRAY_TEXT   = colors.HexColor("#475569")
LIGHT_GRAY  = colors.HexColor("#f8fafc")
TABLE_HEAD  = colors.HexColor("#1e3a5f")
TABLE_ALT   = colors.HexColor("#f0f4f8")
ACCENT      = colors.HexColor("#0ea5e9")
WHITE       = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm

# ─────────────────────────────────────────────
# Header / Footer canvas
# ─────────────────────────────────────────────
def make_page_decorator(title="synthdid User Manual"):
    def decorate(canvas_obj, doc):
        canvas_obj.saveState()
        w, h = A4

        if doc.page > 1:
            # Top bar
            canvas_obj.setFillColor(DARK_BLUE)
            canvas_obj.rect(0, h - 1.1*cm, w, 1.1*cm, fill=1, stroke=0)
            canvas_obj.setFillColor(WHITE)
            canvas_obj.setFont("Helvetica-Bold", 8)
            canvas_obj.drawString(MARGIN, h - 0.7*cm, title)
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.drawRightString(w - MARGIN, h - 0.7*cm, "d2cml-ai / synthdid.py")

            # Bottom bar
            canvas_obj.setFillColor(DARK_BLUE)
            canvas_obj.rect(0, 0, w, 0.9*cm, fill=1, stroke=0)
            canvas_obj.setFillColor(WHITE)
            canvas_obj.setFont("Helvetica", 7.5)
            canvas_obj.drawString(MARGIN, 0.3*cm, "https://github.com/d2cml-ai/synthdid.py")
            canvas_obj.drawRightString(w - MARGIN, 0.3*cm, f"Page {doc.page}")

        canvas_obj.restoreState()
    return decorate


# ─────────────────────────────────────────────
# Styles
# ─────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["h1"] = ParagraphStyle(
        "h1", parent=base["Heading1"],
        fontSize=18, textColor=DARK_BLUE,
        spaceAfter=10, spaceBefore=22,
        borderPad=(0, 0, 4, 0),
        fontName="Helvetica-Bold",
    )
    styles["h2"] = ParagraphStyle(
        "h2", parent=base["Heading2"],
        fontSize=13, textColor=DARK_BLUE,
        spaceAfter=6, spaceBefore=16,
        fontName="Helvetica-Bold",
        borderWidth=0, borderColor=DARK_BLUE,
        borderPad=2,
    )
    styles["h3"] = ParagraphStyle(
        "h3", parent=base["Heading3"],
        fontSize=11, textColor=MID_BLUE,
        spaceAfter=4, spaceBefore=12,
        fontName="Helvetica-Bold",
    )
    styles["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontSize=9.5, leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6, alignment=TA_JUSTIFY,
        fontName="Helvetica",
    )
    styles["body_left"] = ParagraphStyle(
        "body_left", parent=base["Normal"],
        fontSize=9.5, leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4, alignment=TA_LEFT,
        fontName="Helvetica",
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"],
        fontSize=9.5, leading=15,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=16, spaceAfter=3,
        fontName="Helvetica",
    )
    styles["code"] = ParagraphStyle(
        "code", parent=base["Code"],
        fontSize=8.5, leading=13,
        fontName="Courier",
        textColor=colors.HexColor("#0f172a"),
        backColor=CODE_BG,
        borderColor=CODE_BORDER,
        borderWidth=0.5,
        borderPad=6,
        spaceAfter=8, spaceBefore=4,
        leftIndent=0,
    )
    styles["code_inline"] = ParagraphStyle(
        "code_inline", parent=base["Normal"],
        fontSize=8.5, fontName="Courier",
        textColor=colors.HexColor("#0f172a"),
        backColor=CODE_BG,
    )
    styles["caption"] = ParagraphStyle(
        "caption", parent=base["Normal"],
        fontSize=8, fontName="Helvetica-Oblique",
        textColor=GRAY_TEXT, spaceAfter=8, spaceBefore=2,
        alignment=TA_CENTER,
    )
    styles["note"] = ParagraphStyle(
        "note", parent=base["Normal"],
        fontSize=8.5, leading=13,
        fontName="Helvetica-Oblique",
        textColor=GRAY_TEXT,
        leftIndent=12, spaceAfter=6,
    )
    styles["toc_h1"] = ParagraphStyle(
        "toc_h1", parent=base["Normal"],
        fontSize=10, fontName="Helvetica-Bold",
        textColor=DARK_BLUE, leftIndent=0, spaceAfter=3,
    )
    styles["toc_h2"] = ParagraphStyle(
        "toc_h2", parent=base["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=GRAY_TEXT, leftIndent=16, spaceAfter=2,
    )
    return styles


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def code_block(lines, styles):
    text = "<br/>".join(
        line.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
        for line in lines
    )
    return Paragraph(text, styles["code"])


def param_table(rows, styles, col_widths=None):
    """rows = list of (name, type, description) or (name, description)"""
    has_type = len(rows[0]) == 3
    if has_type:
        header = [
            Paragraph("<b>Parameter</b>", ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
            Paragraph("<b>Type</b>",      ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
            Paragraph("<b>Description</b>", ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
        ]
        data = [header] + [
            [
                Paragraph(f"<font name='Courier' size='8.5'>{r[0]}</font>", styles["body_left"]),
                Paragraph(f"<i>{r[1]}</i>", styles["body_left"]),
                Paragraph(r[2], styles["body_left"]),
            ]
            for r in rows
        ]
        cw = col_widths or [4.5*cm, 3.5*cm, 8.5*cm]
    else:
        header = [
            Paragraph("<b>Parameter</b>", ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
            Paragraph("<b>Description</b>", ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
        ]
        data = [header] + [
            [
                Paragraph(f"<font name='Courier' size='8.5'>{r[0]}</font>", styles["body_left"]),
                Paragraph(r[1], styles["body_left"]),
            ]
            for r in rows
        ]
        cw = col_widths or [5.5*cm, 11*cm]

    style = TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), TABLE_HEAD),
        ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,0), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, TABLE_ALT]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING",(0,0), (-1,-1), 7),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ])
    t = Table(data, colWidths=cw)
    t.setStyle(style)
    return t


def result_table(header_row, data_rows, styles):
    ps_h = ParagraphStyle("rh", fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE)
    ps_d = ParagraphStyle("rd", fontName="Courier", fontSize=8.5, textColor=colors.HexColor("#0f172a"))
    header = [Paragraph(str(c), ps_h) for c in header_row]
    rows   = [[Paragraph(str(c), ps_d) for c in row] for row in data_rows]
    data   = [header] + rows
    n_cols = len(header_row)
    cw     = [(PAGE_W - 2*MARGIN) / n_cols] * n_cols
    style  = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), ACCENT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, TABLE_ALT]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTSIZE",      (0,0),(-1,-1), 8.5),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ])
    t = Table(data, colWidths=cw)
    t.setStyle(style)
    return t


def section_rule(styles):
    return HRFlowable(width="100%", thickness=1.2, color=MID_BLUE, spaceAfter=4, spaceBefore=0)


def info_box(text, styles, bg=LIGHT_BLUE, border=MID_BLUE):
    ps = ParagraphStyle(
        "infobox", fontName="Helvetica", fontSize=9,
        textColor=DARK_BLUE, leading=14,
        leftIndent=10, rightIndent=10,
        spaceAfter=8, spaceBefore=4,
    )
    t = Table(
        [[Paragraph(text, ps)]],
        colWidths=[PAGE_W - 2*MARGIN],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), bg),
        ("BOX",        (0,0),(-1,-1), 1.2, border),
        ("TOPPADDING", (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",(0,0),(-1,-1), 12),
        ("RIGHTPADDING",(0,0),(-1,-1), 12),
    ]))
    return t


# ─────────────────────────────────────────────
# Cover page
# ─────────────────────────────────────────────
def cover_page(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = A4

    # Background gradient simulation (two rects)
    canvas_obj.setFillColor(DARK_BLUE)
    canvas_obj.rect(0, 0, w, h, fill=1, stroke=0)

    canvas_obj.setFillColor(colors.HexColor("#0f2240"))
    canvas_obj.rect(0, 0, w, h * 0.45, fill=1, stroke=0)

    # Accent bar
    canvas_obj.setFillColor(MID_BLUE)
    canvas_obj.rect(0, h * 0.45, w, 0.35*cm, fill=1, stroke=0)

    # Package name
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont("Helvetica-Bold", 52)
    canvas_obj.drawCentredString(w/2, h * 0.72, "synthdid")

    # Subtitle
    canvas_obj.setFont("Helvetica", 17)
    canvas_obj.setFillColor(colors.HexColor("#93c5fd"))
    canvas_obj.drawCentredString(w/2, h * 0.64,
        "Synthetic Difference-in-Differences")
    canvas_obj.drawCentredString(w/2, h * 0.605, "Estimation for Python")

    # Divider
    canvas_obj.setStrokeColor(colors.HexColor("#3b82f6"))
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(MARGIN * 2, h * 0.578, w - MARGIN * 2, h * 0.578)

    # Document type
    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.setFillColor(colors.HexColor("#bfdbfe"))
    canvas_obj.drawCentredString(w/2, h * 0.545, "User Manual  ·  v0.10.1")

    # Authors label
    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.setFillColor(colors.HexColor("#93c5fd"))
    canvas_obj.drawCentredString(w/2, h * 0.365, "AUTHORS")

    # Authors list
    authors = [
        "Jhon Flores  ·  Franco Caceres  ·  Rodrigo Grijalba",
        "Alexander Quispe  ·  Damian Clarke  ·  Jesus Nicho",
    ]
    canvas_obj.setFont("Helvetica", 9.5)
    canvas_obj.setFillColor(WHITE)
    for i, line in enumerate(authors):
        canvas_obj.drawCentredString(w/2, h * 0.335 - i*0.033*h, line)

    # Organization
    canvas_obj.setFont("Helvetica-Oblique", 9)
    canvas_obj.setFillColor(colors.HexColor("#94a3b8"))
    canvas_obj.drawCentredString(w/2, h * 0.255, "D2CML Team  ·  2024")
    canvas_obj.drawCentredString(w/2, h * 0.225,
        "https://github.com/d2cml-ai/synthdid.py")

    # Bottom license note
    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.setFillColor(colors.HexColor("#64748b"))
    canvas_obj.drawCentredString(w/2, 1*cm,
        "Released under the MIT License")

    canvas_obj.restoreState()


# ─────────────────────────────────────────────
# Document builder
# ─────────────────────────────────────────────
def build_manual(output_path="Manual.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=2.0*cm, bottomMargin=1.8*cm,
        title="synthdid User Manual",
        author="D2CML Team",
        subject="Synthetic Difference-in-Differences",
    )

    S = build_styles()
    decorator = make_page_decorator()
    story = []

    # ── Cover (first page handled by onFirstPage) ─────────────────────
    story.append(PageBreak())   # skip first page content, cover drawn on canvas

    # ── Table of Contents ─────────────────────────────────────────────
    story.append(Paragraph("Table of Contents", S["h1"]))
    story.append(section_rule(S))
    toc_entries = [
        ("1", "Introduction"),
        ("1.1", "Overview"),
        ("1.2", "Key Features"),
        ("2", "Installation"),
        ("3", "Quick Start"),
        ("4", "API Reference"),
        ("4.1", "Class: Synthdid"),
        ("4.2", "Method: .fit()"),
        ("4.3", "Method: .vcov()"),
        ("4.4", "Method: .summary()"),
        ("4.5", "Methods: .plot_outcomes() and .plot_weights()"),
        ("5", "Examples"),
        ("5.1", "Block Design — SDID"),
        ("5.2", "Block Design — Synthetic Control (SC)"),
        ("5.3", "Block Design — Difference-in-Differences (DiD)"),
        ("5.4", "Staggered Adoption Design"),
        ("5.5", "Covariate Adjustment"),
        ("6", "Inference Methods"),
        ("6.1", "Bootstrap"),
        ("6.2", "Placebo"),
        ("6.3", "Jackknife"),
        ("7", "Datasets"),
        ("8", "Mathematical Background"),
        ("9", "How to Cite"),
    ]
    for num, title in toc_entries:
        indent = 16 if "." in num else 0
        ps = ParagraphStyle(
            f"toc_{num}", fontName="Helvetica-Bold" if "." not in num else "Helvetica",
            fontSize=9.5 if "." not in num else 9,
            textColor=DARK_BLUE if "." not in num else GRAY_TEXT,
            leftIndent=indent, spaceAfter=3,
        )
        story.append(Paragraph(f"{num}  {title}", ps))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 1. INTRODUCTION
    # ══════════════════════════════════════════
    story.append(Paragraph("1. Introduction", S["h1"]))
    story.append(section_rule(S))

    story.append(Paragraph("1.1  Overview", S["h2"]))
    story.append(Paragraph(
        "The <b>synthdid</b> package is a Python implementation of the Synthetic Difference-in-Differences (SDID) "
        "estimator introduced by Arkhangelsky, Athey, Hirshberg, Imbens, and Wager (2021). The SDID estimator "
        "is a modern approach to causal inference in panel data settings that simultaneously reweights observations "
        "across both the unit dimension (like Synthetic Control) and the time dimension (like Difference-in-Differences), "
        "producing a more robust estimate of the Average Treatment Effect on the Treated (ATT).",
        S["body"]
    ))
    story.append(Paragraph(
        "The estimator is designed to be robust to heterogeneous treatment effects, time trends, and "
        "unit-level heterogeneity. The package also extends the original SDID framework to handle staggered "
        "adoption designs, where different units adopt the treatment at different points in time.",
        S["body"]
    ))

    story.append(Paragraph("1.2  Key Features", S["h2"]))
    features = [
        ("<b>Block designs</b> — single treatment adoption period with support for SDID, Synthetic Control (SC), "
         "and standard DiD estimators via the same interface."),
        ("<b>Staggered adoption</b> — multiple treatment cohorts across different time periods, with cohort-level "
         "ATT decomposition."),
        ("<b>Covariate adjustment</b> — two methods available: <font name='Courier' size='8.5'>\"optimized\"</font> "
         "(joint estimation) and <font name='Courier' size='8.5'>\"projected\"</font> (residual-based)."),
        ("<b>Inference</b> — three standard error methods: bootstrap, placebo, and jackknife, all accessible "
         "via a single <font name='Courier' size='8.5'>.vcov()</font> call."),
        ("<b>Visualization</b> — weighted outcome trend plots and weight distribution plots via "
         "<font name='Courier' size='8.5'>.plot_outcomes()</font> and <font name='Courier' size='8.5'>.plot_weights()</font>."),
        ("<b>Method chaining</b> — the entire workflow can be expressed as a single chained expression."),
    ]
    for f in features:
        story.append(Paragraph(f"• &nbsp; {f}", S["bullet"]))
    story.append(Spacer(1, 0.3*cm))

    story.append(info_box(
        "[!]  <b>Related implementations:</b> This package draws on the R package "
        "<font name='Courier' size='8.5'>synthdid</font> (synth-inference/synthdid), the Julia package "
        "<font name='Courier' size='8.5'>Synthdid.jl</font> (d2cml-ai/Synthdid.jl), and the Stata "
        "command <font name='Courier' size='8.5'>sdid</font> (Daniel-Pailanir/sdid).",
        S
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 2. INSTALLATION
    # ══════════════════════════════════════════
    story.append(Paragraph("2. Installation", S["h1"]))
    story.append(section_rule(S))

    story.append(Paragraph(
        "Install the latest stable release from PyPI:", S["body"]
    ))
    story.append(code_block(["pip install synthdid"], S))

    story.append(Paragraph(
        "Or install the development version directly from GitHub:", S["body"]
    ))
    story.append(code_block(
        ["pip install git+https://github.com/d2cml-ai/synthdid.py"], S
    ))

    story.append(Paragraph("<b>Dependencies</b>", S["h3"]))
    story.append(Paragraph(
        "The package requires Python >= 3.8 and the following libraries:", S["body"]
    ))
    deps = [
        ("numpy", ">= 1.23", "Numerical computations and array operations"),
        ("pandas", ">= 1.5", "Data manipulation and panel data handling"),
        ("scipy", ">= 1.10", "Optimization routines and statistical functions"),
        ("statsmodels", ">= 0.13", "Statistical models and inference utilities"),
        ("matplotlib", ">= 3.7", "Visualization of outcomes and weights"),
    ]
    story.append(param_table(deps, S))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 3. QUICK START
    # ══════════════════════════════════════════
    story.append(Paragraph("3. Quick Start", S["h1"]))
    story.append(section_rule(S))
    story.append(Paragraph(
        "The following example shows the full SDID workflow in three lines, from data loading "
        "to a summary table of results:", S["body"]
    ))
    story.append(code_block([
        "from synthdid.get_data import california_prop99",
        "from synthdid.synthdid import Synthdid",
        "",
        "df = california_prop99()",
        "",
        "result = (",
        "    Synthdid(df, \"State\", \"Year\", \"treated\", \"PacksPerCapita\")",
        "    .fit()",
        "    .vcov()",
        "    .summary()",
        ")",
        "result.summary2",
    ], S))

    story.append(Paragraph(
        "This produces the following output:", S["body"]
    ))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "-15.60383", "10.789924", "-1.446148", "0.148136"]],
        S
    ))
    story.append(Spacer(1, 0.4*cm))
    story.append(info_box(
        " <b>Tip:</b> All methods return <font name='Courier' size='8.5'>self</font>, enabling full method "
        "chaining. You can call <font name='Courier' size='8.5'>.vcov()</font> multiple times with different "
        "methods on the same fitted model without re-running <font name='Courier' size='8.5'>.fit()</font>.",
        S
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 4. API REFERENCE
    # ══════════════════════════════════════════
    story.append(Paragraph("4. API Reference", S["h1"]))
    story.append(section_rule(S))

    # 4.1 Constructor
    story.append(Paragraph("4.1  Class: Synthdid", S["h2"]))
    story.append(code_block([
        "Synthdid(data, unit, time, treatment, outcome, covariates=None)"
    ], S))
    story.append(Paragraph(
        "Initializes the SDID model. This step parses the panel data into internal matrices "
        "and identifies treatment cohorts. No estimation is performed at this stage.",
        S["body"]
    ))
    story.append(Paragraph("<b>Parameters</b>", S["h3"]))
    constructor_params = [
        ("data",       "pd.DataFrame",   "Panel dataset in long format. Each row is one observation for a unit-time pair."),
        ("unit",       "str",            "Column name identifying the cross-sectional unit (e.g., state, country, firm). Accepts numeric or string values."),
        ("time",       "str",            "Column name for the time variable (e.g., year, quarter). Must be numeric."),
        ("treatment",  "str",            "Column name for the treatment dummy. Must equal 1 in the first period a unit is treated and all subsequent periods, and 0 otherwise."),
        ("outcome",    "str",            "Column name for the outcome variable. Must be numeric."),
        ("covariates", "list[str] | None","Optional list of column names for covariates to include in the estimation. Default is None."),
    ]
    story.append(param_table(constructor_params, S))
    story.append(Spacer(1, 0.3*cm))

    # 4.2 .fit()
    story.append(Paragraph("4.2  Method: .fit()", S["h2"]))
    story.append(code_block([
        ".fit(cov_method=\"optimized\", did=False, synth=False)"
    ], S))
    story.append(Paragraph(
        "Estimates the ATT, unit weights (omega), and time weights (lambda). In a staggered adoption "
        "design, this produces a weighted average of cohort-specific ATTs stored in "
        "<font name='Courier' size='8.5'>att_info</font>. Returns <font name='Courier' size='8.5'>self</font>.",
        S["body"]
    ))
    story.append(Paragraph("<b>Parameters</b>", S["h3"]))
    fit_params = [
        ("cov_method", "str | None",
         "Covariate adjustment method. "
         "\"optimized\": jointly estimates weights and covariate coefficients. "
         "\"projected\": removes covariate variation by projection first, then estimates weights on residuals. "
         "Ignored if no covariates were passed to the constructor. Default: \"optimized\"."),
        ("did",  "bool",
         "If True, uses uniform unit and time weights, reducing the estimator to a standard "
         "Difference-in-Differences. Default: False."),
        ("synth","bool",
         "If True, uses zero pre-period time weights, reducing the estimator to a "
         "Synthetic Control (SC) estimator. Default: False."),
    ]
    story.append(param_table(fit_params, S, col_widths=[3.8*cm, 2.8*cm, 10*cm]))
    story.append(Paragraph("<b>Attributes set after .fit()</b>", S["h3"]))
    fit_attrs = [
        ("self.att",      "float",          "Overall average treatment effect on the treated."),
        ("self.att_info", "pd.DataFrame",   "Cohort-level ATT decomposition with columns: time, att_time, att_wt, N0, T0, N1, T1."),
        ("self.weights",  "dict",           "Dictionary with keys 'lambda' (time weights) and 'omega' (unit weights) per cohort."),
    ]
    story.append(param_table(fit_attrs, S))
    story.append(Spacer(1, 0.3*cm))

    # 4.3 .vcov()
    story.append(Paragraph("4.3  Method: .vcov()", S["h2"]))
    story.append(code_block([
        ".vcov(method=\"placebo\", n_reps=50)"
    ], S))
    story.append(Paragraph(
        "Estimates the standard error of the ATT estimator. Must be called after "
        "<font name='Courier' size='8.5'>.fit()</font>. Can be called multiple times with different "
        "methods without re-fitting the model. Returns <font name='Courier' size='8.5'>self</font>.",
        S["body"]
    ))
    story.append(Paragraph("<b>Parameters</b>", S["h3"]))
    vcov_params = [
        ("method",  "str",
         "Variance estimation method. One of \"placebo\", \"bootstrap\", or \"jackknife\". "
         "Default: \"placebo\"."),
        ("n_reps",  "int",
         "Number of simulation replications for the placebo and bootstrap methods. "
         "Higher values give more stable estimates but take longer. Default: 50."),
    ]
    story.append(param_table(vcov_params, S, col_widths=[3.8*cm, 2.8*cm, 10*cm]))
    story.append(Paragraph("<b>Attributes set after .vcov()</b>", S["h3"]))
    story.append(param_table([
        ("self.se", "float", "Estimated standard error of the ATT."),
    ], S))
    story.append(Spacer(1, 0.3*cm))

    # 4.4 .summary()
    story.append(Paragraph("4.4  Method: .summary()", S["h2"]))
    story.append(code_block([".summary()"], S))
    story.append(Paragraph(
        "Computes the summary statistics table. If <font name='Courier' size='8.5'>.vcov()</font> was not called, "
        "the standard error, t-statistic, and p-value are shown as <font name='Courier' size='8.5'>\"-\"</font>. "
        "Returns <font name='Courier' size='8.5'>self</font>.",
        S["body"]
    ))
    story.append(Paragraph("<b>Attributes set after .summary()</b>", S["h3"]))
    story.append(param_table([
        ("self.summary2", "pd.DataFrame",
         "DataFrame with columns: ATT, Std. Err., t, P>|t|. Access via result.summary2."),
    ], S))
    story.append(Spacer(1, 0.3*cm))

    # 4.5 plot methods
    story.append(Paragraph("4.5  Methods: .plot_outcomes() and .plot_weights()", S["h2"]))
    story.append(code_block([
        ".plot_outcomes()",
        ".plot_weights()",
    ], S))
    story.append(Paragraph(
        "<font name='Courier' size='8.5'>.plot_outcomes()</font> plots the weighted outcome trends for the treated "
        "group and its synthetic control, allowing visual inspection of pre-treatment fit and post-treatment divergence.",
        S["body"]
    ))
    story.append(Paragraph(
        "<font name='Courier' size='8.5'>.plot_weights()</font> plots the estimated unit weights (omega) and time weights (lambda), "
        "showing which control units and pre-treatment periods are most important for constructing the counterfactual.",
        S["body"]
    ))
    story.append(code_block([
        "from matplotlib import pyplot as plt",
        "",
        "plt.show(result.plot_outcomes())",
        "plt.show(result.plot_weights())",
    ], S))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 5. EXAMPLES
    # ══════════════════════════════════════════
    story.append(Paragraph("5. Examples", S["h1"]))
    story.append(section_rule(S))
    story.append(Paragraph(
        "All examples use the two built-in datasets available in "
        "<font name='Courier' size='8.5'>synthdid.get_data</font>. "
        "See Section 7 for a detailed description of each dataset.",
        S["body"]
    ))
    story.append(code_block([
        "from synthdid.get_data import california_prop99, quota",
        "from synthdid.synthdid import Synthdid",
        "from matplotlib import pyplot as plt",
    ], S))

    # 5.1 SDID
    story.append(Paragraph("5.1  Block Design — Synthetic DiD (SDID)", S["h2"]))
    story.append(Paragraph(
        "This is the canonical SDID estimator. It assigns data-driven weights to both control units "
        "and pre-treatment time periods to construct the most credible counterfactual.",
        S["body"]
    ))
    story.append(code_block([
        "df = california_prop99()",
        "",
        "california_sdid = (",
        "    Synthdid(df, \"State\", \"Year\", \"treated\", \"PacksPerCapita\")",
        "    .fit()",
        "    .vcov()",
        "    .summary()",
        ")",
        "california_sdid.summary2",
    ], S))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "-15.60383", "10.789924", "-1.446148", "0.148136"]],
        S
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "The estimate suggests that Proposition 99 reduced cigarette consumption by approximately "
        "15.6 packs per capita, though the effect is not statistically significant at conventional levels "
        "with the placebo standard error (p = 0.148).",
        S["note"]
    ))
    story.append(code_block([
        "plt.show(california_sdid.plot_outcomes())",
        "plt.show(california_sdid.plot_weights())",
    ], S))
    story.append(Spacer(1, 0.3*cm))

    # 5.2 SC
    story.append(Paragraph("5.2  Block Design — Synthetic Control (SC)", S["h2"]))
    story.append(Paragraph(
        "Passing <font name='Courier' size='8.5'>synth=True</font> to <font name='Courier' size='8.5'>.fit()</font> "
        "sets all pre-period time weights to zero, reducing the estimator to a pure Synthetic Control.",
        S["body"]
    ))
    story.append(code_block([
        "california_sc = (",
        "    Synthdid(df, \"State\", \"Year\", \"treated\", \"PacksPerCapita\")",
        "    .fit(synth=True)",
        ")",
        "plt.show(california_sc.plot_outcomes())",
        "plt.show(california_sc.plot_weights())",
    ], S))

    # 5.3 DiD
    story.append(Paragraph("5.3  Block Design — Difference-in-Differences (DiD)", S["h2"]))
    story.append(Paragraph(
        "Passing <font name='Courier' size='8.5'>did=True</font> sets all unit and time weights to uniform values "
        "(1/N0 and 1/T0 respectively), reducing the estimator to a standard two-way fixed effects DiD.",
        S["body"]
    ))
    story.append(code_block([
        "california_did = (",
        "    Synthdid(df, \"State\", \"Year\", \"treated\", \"PacksPerCapita\")",
        "    .fit(did=True)",
        ")",
        "plt.show(california_did.plot_outcomes())",
        "plt.show(california_did.plot_weights())",
    ], S))
    story.append(Spacer(1, 0.3*cm))

    # 5.4 Staggered
    story.append(Paragraph("5.4  Staggered Adoption Design", S["h2"]))
    story.append(Paragraph(
        "When different units adopt the treatment at different points in time, the package automatically "
        "detects the treatment cohorts and estimates a cohort-weighted average ATT. The individual cohort "
        "ATTs are available via the <font name='Courier' size='8.5'>att_info</font> attribute.",
        S["body"]
    ))
    story.append(code_block([
        "df = quota()",
        "",
        "fit_model = (",
        "    Synthdid(df, \"country\", \"year\", \"quota\", \"womparl\")",
        "    .fit()",
        "    .vcov()",
        "    .summary()",
        ")",
        "fit_model.summary2",
    ], S))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "8.0341", "1.684382", "4.769762", "0.000002"]],
        S
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "The ATT decomposed by treatment cohort:", S["body"]
    ))
    story.append(code_block(["fit_model.att_info"], S))
    story.append(result_table(
        ["", "time", "att_time", "att_wt", "N0", "T0", "N1", "T1"],
        [
            ["0", "2000.0", "8.388868",  "0.170213", "110", "10", "1", "16"],
            ["1", "2002.0", "6.967746",  "0.297872", "110", "12", "2", "14"],
            ["2", "2003.0", "13.952256", "0.276596", "110", "13", "2", "13"],
            ["3", "2005.0", "-3.450543", "0.117021", "110", "15", "1", "11"],
            ["4", "2010.0", "2.749035",  "0.063830", "110", "20", "1", "6"],
            ["5", "2012.0", "21.762715", "0.042553", "110", "22", "1", "4"],
            ["6", "2013.0", "-0.820324", "0.031915", "110", "23", "1", "3"],
        ],
        S
    ))
    story.append(Paragraph(
        "Columns: <b>time</b> = adoption year of the cohort; <b>att_time</b> = cohort-specific ATT; "
        "<b>att_wt</b> = cohort weight in the overall ATT (proportional to N1xT1); "
        "<b>N0/N1</b> = number of control/treated units; <b>T0/T1</b> = pre/post-treatment periods.",
        S["note"]
    ))
    story.append(Spacer(1, 0.3*cm))

    # 5.5 Covariates
    story.append(Paragraph("5.5  Covariate Adjustment", S["h2"]))
    story.append(Paragraph(
        "Covariates are passed as a list to the constructor. Two adjustment methods are available, "
        "controlled by the <font name='Courier' size='8.5'>cov_method</font> argument in "
        "<font name='Courier' size='8.5'>.fit()</font>.",
        S["body"]
    ))
    story.append(Paragraph("<b>Optimized method (default)</b>", S["h3"]))
    story.append(Paragraph(
        "Jointly estimates the unit weights, time weights, and covariate coefficients beta in a single "
        "optimization problem. This is the recommended method when covariates are expected to explain "
        "pre-treatment outcome trends.",
        S["body"]
    ))
    story.append(code_block([
        "fit_covar = (",
        "    Synthdid(",
        "        df[~df.lngdp.isnull()], \"country\", \"year\", \"quota\", \"womparl\",",
        "        covariates=[\"lngdp\"]",
        "    )",
        "    .fit()          # cov_method=\"optimized\" by default",
        "    .vcov(method=\"bootstrap\")",
        "    .summary()",
        ")",
        "fit_covar.summary2",
    ], S))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "8.04901", "3.395295", "2.370636", "0.017757"]],
        S
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("<b>Projected method</b>", S["h3"]))
    story.append(Paragraph(
        "First removes the variation explained by covariates via linear projection onto the control "
        "group pre-treatment outcomes, then estimates the SDID weights on the residuals. Use this method "
        "when the covariate effect is expected to be stable over time.",
        S["body"]
    ))
    story.append(code_block([
        "fit_proj = (",
        "    Synthdid(",
        "        df[~df.lngdp.isnull()], \"country\", \"year\", \"quota\", \"womparl\",",
        "        covariates=[\"lngdp\"]",
        "    )",
        "    .fit(cov_method=\"projected\")",
        "    .vcov(method=\"bootstrap\")",
        "    .summary()",
        ")",
        "fit_proj.summary2",
    ], S))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "8.05903", "3.428897", "2.350327", "0.018757"]],
        S
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 6. INFERENCE
    # ══════════════════════════════════════════
    story.append(Paragraph("6. Inference Methods", S["h1"]))
    story.append(section_rule(S))
    story.append(Paragraph(
        "Standard errors can be computed by calling <font name='Courier' size='8.5'>.vcov(method=...)</font> "
        "after <font name='Courier' size='8.5'>.fit()</font>. The three available methods differ in their "
        "assumptions and computational cost. You can switch between methods on the same fitted model "
        "without re-running estimation.",
        S["body"]
    ))
    story.append(code_block([
        "# Setup: fit once, then try all three methods",
        "countries_to_exclude = [\"Algeria\", \"Kenya\", \"Samoa\", \"Swaziland\", \"Tanzania\"]",
        "df_sub = df[~df.country.isin(countries_to_exclude)]",
        "",
        "model = (",
        "    Synthdid(df_sub, \"country\", \"year\", \"quota\", \"womparl\")",
        "    .fit()",
        ")",
    ], S))

    story.append(Paragraph("6.1  Bootstrap", S["h2"]))
    story.append(Paragraph(
        "Resamples cross-sectional units with replacement "
        "<font name='Courier' size='8.5'>n_reps</font> times and re-estimates the ATT on each bootstrap "
        "sample. The standard error is the standard deviation of the bootstrap ATT distribution. "
        "Suitable for large samples where the number of control units is much larger than the number "
        "of treated units.",
        S["body"]
    ))
    story.append(code_block([
        "model.vcov(method=\"bootstrap\", n_reps=50).summary()",
        "model.summary2",
    ], S))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "10.33066", "5.404923", "1.911343", "0.055961"]],
        S
    ))

    story.append(Paragraph("6.2  Placebo", S["h2"]))
    story.append(Paragraph(
        "Randomly assigns treatment to control units, mimicking the treatment adoption pattern, "
        "and estimates the ATT on these placebo-treated samples "
        "<font name='Courier' size='8.5'>n_reps</font> times. The standard error is the standard deviation "
        "of the placebo ATT distribution. This is the <b>default method</b> and is recommended when the "
        "number of treated units is small, as bootstrap can be unstable in that case.",
        S["body"]
    ))
    story.append(code_block([
        "model.vcov(method=\"placebo\", n_reps=50).summary()",
        "model.summary2",
    ], S))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "10.33066", "2.244618", "4.602413", "0.000004"]],
        S
    ))

    story.append(Paragraph("6.3  Jackknife", S["h2"]))
    story.append(Paragraph(
        "Applies leave-one-unit-out resampling, re-estimating the ATT each time one control unit is "
        "excluded from the sample. The standard error is computed from the jackknife variance formula. "
        "This method is deterministic (no random replications), conservative, and computationally intensive "
        "for large panels. Requires that each treatment cohort has more than one treated unit.",
        S["body"]
    ))
    story.append(code_block([
        "model.vcov(method=\"jackknife\").summary()",
        "model.summary2",
    ], S))
    story.append(result_table(
        ["", "ATT", "Std. Err.", "t", "P > |t|"],
        [["0", "10.33066", "6.04213", "1.709771", "0.087308"]],
        S
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(info_box(
        "[!]  <b>Jackknife restriction:</b> The jackknife method raises a "
        "<font name='Courier' size='8.5'>ValueError</font> if any treatment cohort has only one treated unit, "
        "since leaving that unit out would result in no treated units for that cohort.",
        S,
        bg=colors.HexColor("#fff7ed"),
        border=colors.HexColor("#f97316"),
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 7. DATASETS
    # ══════════════════════════════════════════
    story.append(Paragraph("7. Datasets", S["h1"]))
    story.append(section_rule(S))

    story.append(Paragraph(
        "Two datasets are bundled with the package and are loaded from the project's GitHub repository. "
        "They are the canonical empirical applications in the SDID literature.",
        S["body"]
    ))

    story.append(Paragraph(
        "<font name='Courier' size='9'>california_prop99()</font>", S["h2"]
    ))
    story.append(Paragraph(
        "Annual U.S. state-level panel data on cigarette consumption from 1970 to 2000. "
        "Used in Abadie, Diamond, and Hainmueller (2010) and Arkhangelsky et al. (2021) as the "
        "canonical application for Synthetic Control and SDID respectively.",
        S["body"]
    ))
    dataset1 = [
        ("State",          "str",   "U.S. state name. California is the single treated unit."),
        ("Year",           "int",   "Calendar year, ranging from 1970 to 2000."),
        ("PacksPerCapita", "float", "Per capita cigarette consumption in packs per year. This is the outcome variable."),
        ("treated",        "int",   "Treatment dummy. Equals 1 for California from 1989 onward, 0 otherwise."),
    ]
    story.append(param_table(dataset1, S))

    story.append(Paragraph(
        "<font name='Courier' size='9'>quota()</font>", S["h2"]
    ))
    story.append(Paragraph(
        "Country-year panel data on women's parliamentary representation, covering 116 countries "
        "from 1990 to 2015. Countries adopted gender quota laws at different points in time, making "
        "this a natural staggered adoption application.",
        S["body"]
    ))
    dataset2 = [
        ("country", "str",   "Country name identifier."),
        ("year",    "int",   "Calendar year, ranging from 1990 to 2015."),
        ("womparl", "float", "Share of women in parliament (%). This is the outcome variable."),
        ("quota",   "int",   "Treatment dummy. Equals 1 once a country has adopted a gender quota law."),
        ("lngdp",   "float", "Log of GDP per capita. Available as an optional covariate. Contains missing values."),
    ]
    story.append(param_table(dataset2, S))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 8. MATH BACKGROUND
    # ══════════════════════════════════════════
    story.append(Paragraph("8. Mathematical Background", S["h1"]))
    story.append(section_rule(S))
    story.append(Paragraph(
        "This section provides a detailed description of the SDID estimator, the meaning of its "
        "weights, and how SDID, SC, and DiD differ mathematically. "
        "For full derivations and asymptotic theory, refer to Arkhangelsky et al. (2021).",
        S["body"]
    ))

    # ── 8.1 Setup ────────────────────────────────────────────────────
    story.append(Paragraph("8.1  Setup and Notation", S["h2"]))
    story.append(Paragraph(
        "Consider a balanced panel with N units observed over T time periods. "
        "There are N1 treated units and N0 = N - N1 control units. "
        "Treatment begins at period T0 + 1, so T0 pre-treatment and T1 = T - T0 post-treatment periods exist. "
        "Let Y<sub>it</sub> denote the observed outcome for unit i at time t, and D<sub>it</sub> = 1 "
        "if unit i is treated at time t.",
        S["body"]
    ))
    story.append(Paragraph(
        "The SDID estimator — and its variants SC and DiD — builds a <b>synthetic counterfactual</b> "
        "by combining control units and pre-treatment time periods using two types of weights:",
        S["body"]
    ))

    # Two weight boxes side by side
    ps_box = ParagraphStyle("wbox", fontName="Helvetica", fontSize=9, textColor=DARK_BLUE,
                            leading=14, leftIndent=8, rightIndent=8)
    ps_box_title = ParagraphStyle("wbox_t", fontName="Helvetica-Bold", fontSize=9.5,
                                  textColor=WHITE, spaceAfter=4)

    half_w = (PAGE_W - 2*MARGIN - 0.4*cm) / 2
    omega_box = Table(
        [[Paragraph("Unit weights  omega_i  (WHO)", ps_box_title)],
         [Paragraph(
             "Determine which control units contribute to the counterfactual and in what proportion. "
             "A high omega_i means unit i closely resembles the treated group in the pre-treatment period. "
             "Required: omega_i >= 0 and sum(omega_i) = 1.",
             ps_box)]],
        colWidths=[half_w],
    )
    omega_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), TABLE_HEAD),
        ("BACKGROUND", (0,1),(0,1), LIGHT_BLUE),
        ("BOX",        (0,0),(0,-1), 1, MID_BLUE),
        ("TOPPADDING", (0,0),(0,-1), 7),
        ("BOTTOMPADDING",(0,0),(0,-1), 7),
        ("LEFTPADDING", (0,0),(0,-1), 10),
        ("RIGHTPADDING",(0,0),(0,-1), 10),
    ]))

    lambda_box = Table(
        [[Paragraph("Time weights  lambda_t  (WHEN)", ps_box_title)],
         [Paragraph(
             "Determine which pre-treatment years are most informative for predicting the counterfactual "
             "level just before treatment. "
             "Required: lambda_t >= 0 and sum(lambda_t) = 1. "
             "Only active in SDID and DiD — in SC they are all fixed at zero.",
             ps_box)]],
        colWidths=[half_w],
    )
    lambda_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), TABLE_HEAD),
        ("BACKGROUND", (0,1),(0,1), LIGHT_BLUE),
        ("BOX",        (0,0),(0,-1), 1, MID_BLUE),
        ("TOPPADDING", (0,0),(0,-1), 7),
        ("BOTTOMPADDING",(0,0),(0,-1), 7),
        ("LEFTPADDING", (0,0),(0,-1), 10),
        ("RIGHTPADDING",(0,0),(0,-1), 10),
    ]))

    two_col = Table([[omega_box, lambda_box]], colWidths=[half_w, half_w],
                    hAlign="LEFT")
    two_col.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ("COLPADDING",   (0,0),(-1,-1), 4),
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(two_col)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        "Each method obtains these weights differently:",
        S["body"]
    ))
    method_compare = [
        ("omega_i", "Regularized optimization", "Optimization (no regularization)", "Uniform  1/N0"),
        ("lambda_t", "Regularized optimization", "Fixed at 0 for all t", "Uniform  1/T0"),
    ]
    ps_th = ParagraphStyle("cth", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)
    ps_td = ParagraphStyle("ctd", fontName="Courier", fontSize=8.5, textColor=colors.HexColor("#0f172a"))
    ps_td2 = ParagraphStyle("ctd2", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#0f172a"))
    cw3 = [2.5*cm, 5.5*cm, 5.5*cm, 3*cm]
    method_header = [
        Paragraph("Weight", ps_th),
        Paragraph("SDID", ps_th),
        Paragraph("SC", ps_th),
        Paragraph("DiD", ps_th),
    ]
    method_rows = [method_header] + [
        [Paragraph(r[0], ps_td), Paragraph(r[1], ps_td2),
         Paragraph(r[2], ps_td2), Paragraph(r[3], ps_td2)]
        for r in method_compare
    ]
    method_t = Table(method_rows, colWidths=cw3)
    method_t.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0), TABLE_HEAD),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, TABLE_ALT]),
        ("GRID",           (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",     (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 5),
        ("LEFTPADDING",    (0,0),(-1,-1), 7),
        ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(method_t)
    story.append(Spacer(1, 0.3*cm))

    # ── 8.2 SDID Estimator ───────────────────────────────────────────
    story.append(Paragraph("8.2  The SDID Estimator", S["h2"]))
    story.append(Paragraph(
        "Given weights omega and lambda, the SDID estimator solves a weighted two-way fixed effects regression:",
        S["body"]
    ))
    story.append(info_box(
        "<b>tau_hat_sdid</b> = argmin_{tau, alpha, beta}  "
        "sum_{i,t} omega_i * lambda_t * (Y_it - alpha_i - beta_t - tau * D_it)^2",
        S, bg=LIGHT_GRAY, border=colors.HexColor("#94a3b8"),
    ))
    story.append(Paragraph(
        "where alpha_i are unit fixed effects, beta_t are time fixed effects, and "
        "D_it = 1 for treated units in post-treatment periods. "
        "The weights make the regression focus on the most comparable units and most "
        "informative time periods.",
        S["body"]
    ))

    # ── 8.3 Unit weights ─────────────────────────────────────────────
    story.append(Paragraph("8.3  Unit Weight Estimation  (omega_hat)", S["h2"]))
    story.append(Paragraph(
        "Unit weights are chosen so that the weighted average of control unit pre-treatment outcomes "
        "is parallel to the treated group's pre-treatment trend:",
        S["body"]
    ))
    story.append(info_box(
        "<b>omega_hat</b> = argmin_{omega in Delta(N0)}  "
        "sum_{t <= T0} ( sum_{i <= N0} omega_i * Y_it  -  Y_bar_t^tr )^2  +  zeta_omega^2 * T0 * ||omega||^2",
        S, bg=LIGHT_GRAY, border=colors.HexColor("#94a3b8"),
    ))
    story.append(Paragraph(
        "where Delta(N0) is the probability simplex (omega_i >= 0, sum = 1), "
        "Y_bar_t^tr is the mean outcome of treated units at time t, and "
        "zeta_omega is a regularization parameter that prevents extreme weights:",
        S["body"]
    ))
    story.append(info_box(
        "<b>zeta_omega</b> = eta * sigma_hat      where      "
        "<b>eta</b> = (N1 * T1)^(1/4)      and      "
        "<b>sigma_hat</b> = sqrt( Var( Delta Y_it ) )  over control units pre-treatment",
        S, bg=colors.HexColor("#f0f9ff"), border=ACCENT,
    ))
    story.append(Paragraph(
        "The term eta = (N1T1)^(1/4) grows with the treated cell size, "
        "producing stronger regularization when more treated unit-time observations are available. "
        "sigma_hat is the noise level estimated from first differences of control outcomes in the pre-period. "
        "This adaptive regularization prevents the algorithm from overfitting the pre-treatment period.",
        S["body"]
    ))
    story.append(Paragraph(
        "<b>Behavior by method:</b>",
        S["body"]
    ))
    omega_behavior = [
        ("SDID",
         "Regularized optimization (Frank-Wolfe). Weights are diffuse: typically 25-35 of N0 units "
         "receive positive weight. Maximum weight typically 0.10-0.27. Low overfitting risk."),
        ("SC",
         "Optimization with minimal regularization (zeta = 1e-6 * sigma_hat). Weights are sparse: "
         "only 3-8 units receive positive weight, often 1 unit dominates (max weight 0.38-0.92). "
         "High overfitting risk."),
        ("DiD",
         "No optimization. Uniform weights: omega_i = 1/N0 for all control units. "
         "All units are treated as equally comparable regardless of their pre-trend."),
    ]
    story.append(param_table(omega_behavior, S, col_widths=[2.5*cm, 14*cm]))
    story.append(Spacer(1, 0.3*cm))

    # ── 8.4 Time weights ─────────────────────────────────────────────
    story.append(Paragraph("8.4  Time Weight Estimation  (lambda_hat)", S["h2"]))
    story.append(Paragraph(
        "Time weights are estimated analogously to unit weights, by transposing the panel "
        "(swapping the roles of units and time periods):",
        S["body"]
    ))
    story.append(info_box(
        "<b>lambda_hat</b> = argmin_{lambda in Delta(T0)}  "
        "sum_{i <= N0} ( sum_{t <= T0} lambda_t * Y_it  -  Y_bar_i^post )^2  +  zeta_lambda^2 * N0 * ||lambda||^2",
        S, bg=LIGHT_GRAY, border=colors.HexColor("#94a3b8"),
    ))
    story.append(Paragraph(
        "where zeta_lambda = 1e-6 * sigma_hat (much smaller than zeta_omega, "
        "allowing time weights to concentrate more sharply).",
        S["body"]
    ))
    story.append(Paragraph(
        "<b>Behavior by method — key patterns observed empirically:</b>",
        S["body"]
    ))
    lambda_behavior = [
        ("SDID",
         "Regularized optimization. Concentrates almost all weight on 1-2 years immediately before "
         "treatment. The last pre-treatment year typically receives 0.76-1.00 of total weight. "
         "This reflects that recent years are the best predictors of the counterfactual level. "
         "In the outcome plot, these are the years shown with darker shading."),
        ("SC",
         "Fixed at zero by design: lambda_t = 0 for all t. Matching is done entirely through unit "
         "weights omega_i. The outcome plot shows no pre-period shading for SC."),
        ("DiD",
         "Uniform: lambda_t = 1/T0 for all pre-treatment years. All past periods are treated as "
         "equally informative. Since each cohort has different T0, the uniform weight differs: "
         "e.g. T0=12 gives lambda=0.0833, T0=23 gives lambda=0.0435."),
    ]
    story.append(param_table(lambda_behavior, S, col_widths=[2.5*cm, 14*cm]))
    story.append(Spacer(1, 0.3*cm))
    story.append(info_box(
        "<b>Why does SDID concentrate lambda on the last pre-treatment year?</b>  "
        "The algorithm searches for the years where the synthetic control (built with omega_hat) most "
        "closely matches the treated group. The most recent pre-treatment year captures short-run trends "
        "and is the best predictor of the counterfactual level just before treatment.",
        S, bg=colors.HexColor("#f0fdf4"), border=colors.HexColor("#16a34a"),
    ))
    story.append(PageBreak())

    # ── 8.5 DiD decomposition ────────────────────────────────────────
    story.append(Paragraph("8.5  DiD as a Difference of Means", S["h2"]))
    story.append(Paragraph(
        "When omega_i = 1/N0 and lambda_t = 1/T0, the SDID formula reduces to the "
        "classic two-way fixed effects DiD, which is equivalent to a difference of group means:",
        S["body"]
    ))
    story.append(info_box(
        "<b>ATT_DiD</b>  =  ( Y_bar_treated,post  -  Y_bar_treated,pre )  "
        "-  ( Y_bar_controls,post  -  Y_bar_controls,pre )",
        S, bg=LIGHT_GRAY, border=colors.HexColor("#94a3b8"),
    ))
    story.append(Paragraph(
        "where each Y_bar is a simple (unweighted) group average. "
        "DiD assumes the parallel trends assumption holds unconditionally — "
        "i.e. the average of all control units is a valid counterfactual for the treated group. "
        "When treated units have pre-treatment trends different from the control average, "
        "DiD will produce a biased estimate. SDID and SC correct this by assigning higher weights "
        "to the control units that best match the treated group's pre-trend.",
        S["body"]
    ))
    story.append(Spacer(1, 0.3*cm))

    # ── 8.6 Comparison summary ───────────────────────────────────────
    story.append(Paragraph("8.6  Summary: Weight Properties by Method", S["h2"]))
    story.append(Paragraph(
        "The following tables summarize the key properties of lambda and omega for each method, "
        "as documented empirically using the Cigar dataset (Baltagi, 2002) — "
        "46 U.S. states, 1963-1992, with 7 staggered adoption cohorts.",
        S["body"]
    ))

    story.append(Paragraph("<b>Time weights (lambda_hat)</b>", S["h3"]))
    lambda_summary_data = [
        [Paragraph("<b>Property</b>",      ps_th),
         Paragraph("<b>SDID</b>",          ps_th),
         Paragraph("<b>SC</b>",            ps_th),
         Paragraph("<b>DiD</b>",           ps_th)],
        [Paragraph("Optimization",         ps_td2), Paragraph("Yes (regularized)", ps_td2), Paragraph("No — fixed at 0",   ps_td2), Paragraph("No — uniform",      ps_td2)],
        [Paragraph("Years with weight > 0",ps_td2), Paragraph("1-3 per cohort",    ps_td2), Paragraph("None",             ps_td2), Paragraph("All pre-periods",    ps_td2)],
        [Paragraph("Concentration",        ps_td2), Paragraph("High (1 yr dominates)", ps_td2), Paragraph("—",            ps_td2), Paragraph("None (uniform)",     ps_td2)],
        [Paragraph("Typical max weight",   ps_td2), Paragraph("0.76 – 1.00",       ps_td2), Paragraph("0",               ps_td2), Paragraph("1/T0",               ps_td2)],
        [Paragraph("Shown in outcome plot",ps_td2), Paragraph("Yes (shaded area)", ps_td2), Paragraph("No shading",      ps_td2), Paragraph("Uniform shading",    ps_td2)],
    ]
    lambda_sum_t = Table(lambda_summary_data, colWidths=[4*cm, 4.2*cm, 4.2*cm, 4.1*cm])
    lambda_sum_t.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0), TABLE_HEAD),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, TABLE_ALT]),
        ("GRID",           (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",     (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",    (0,0),(-1,-1), 7), ("VALIGN",(0,0),(-1,-1), "TOP"),
    ]))
    story.append(lambda_sum_t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Unit weights (omega_hat)</b>", S["h3"]))
    omega_summary_data = [
        [Paragraph("<b>Property</b>",          ps_th),
         Paragraph("<b>SDID</b>",              ps_th),
         Paragraph("<b>SC</b>",                ps_th),
         Paragraph("<b>DiD</b>",               ps_th)],
        [Paragraph("Optimization",             ps_td2), Paragraph("Yes (regularized)", ps_td2), Paragraph("Yes (minimal reg.)", ps_td2), Paragraph("No — uniform",    ps_td2)],
        [Paragraph("Units with weight > 0",    ps_td2), Paragraph("~25-35 of N0",      ps_td2), Paragraph("3-8 of N0",         ps_td2), Paragraph("All N0",          ps_td2)],
        [Paragraph("Concentration",            ps_td2), Paragraph("Low-moderate",      ps_td2), Paragraph("High",               ps_td2), Paragraph("None (uniform)",  ps_td2)],
        [Paragraph("Typical max weight",       ps_td2), Paragraph("0.10 – 0.27",       ps_td2), Paragraph("0.38 – 0.92",        ps_td2), Paragraph("1/N0",            ps_td2)],
        [Paragraph("Overfitting risk",         ps_td2), Paragraph("Low",               ps_td2), Paragraph("High",               ps_td2), Paragraph("Very low",        ps_td2)],
        [Paragraph("Regularization param.",    ps_td2), Paragraph("zeta=(N1*T1)^(1/4)*sigma", ps_td2), Paragraph("zeta=1e-6*sigma",   ps_td2), Paragraph("N/A",             ps_td2)],
    ]
    omega_sum_t = Table(omega_summary_data, colWidths=[4*cm, 4.2*cm, 4.2*cm, 4.1*cm])
    omega_sum_t.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0), TABLE_HEAD),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, TABLE_ALT]),
        ("GRID",           (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",     (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",    (0,0),(-1,-1), 7), ("VALIGN",(0,0),(-1,-1), "TOP"),
    ]))
    story.append(omega_sum_t)
    story.append(Spacer(1, 0.3*cm))
    story.append(info_box(
        "<b>Key takeaway:</b> SDID balances between the extremes of SC (very sparse, overfitting risk) "
        "and DiD (uniform, no matching). Its regularization parameter zeta_omega = (N1*T1)^(1/4) * sigma_hat "
        "is adaptive: it grows with the treated cell size, preventing overfitting while still allowing "
        "meaningful differentiation between control units. "
        "SC produces similar ATT estimates to SDID when matching is perfect, but is more sensitive to "
        "idiosyncratic shocks in the few dominant control units.",
        S, bg=colors.HexColor("#f0fdf4"), border=colors.HexColor("#16a34a"),
    ))
    story.append(Spacer(1, 0.3*cm))

    # ── 8.7 Staggered Adoption ───────────────────────────────────────
    story.append(Paragraph("8.7  Staggered Adoption", S["h2"]))
    story.append(Paragraph(
        "For staggered adoption, the data is decomposed into K independent subproblems — one per "
        "treatment cohort k (defined by the year of first treatment). Each cohort k has its own "
        "N0 control units, T0_k pre-treatment periods, N1_k treated units, and T1_k post-treatment periods. "
        "SDID, SC, and DiD weights are estimated independently for each cohort.",
        S["body"]
    ))
    story.append(Paragraph(
        "The overall ATT is the cohort-weighted average:",
        S["body"]
    ))
    story.append(info_box(
        "<b>tau_hat_sdid</b>  =  sum_k  w_k * tau_hat_k      "
        "where      w_k = N1_k * T1_k / sum_k ( N1_k * T1_k )",
        S, bg=LIGHT_GRAY, border=colors.HexColor("#94a3b8"),
    ))
    story.append(Paragraph(
        "The cohort weight w_k is proportional to the number of treated unit-time observations in "
        "cohort k. This is what appears in the <font name='Courier' size='8.5'>att_wt</font> column "
        "of <font name='Courier' size='8.5'>fit_model.att_info</font>. "
        "Cohorts with more treated units or longer post-treatment windows receive higher weight.",
        S["body"]
    ))
    story.append(Spacer(1, 0.3*cm))

    # ── 8.8 Numerical precision ──────────────────────────────────────
    story.append(Paragraph("8.8  Numerical Implementation: Frank-Wolfe Algorithm", S["h2"]))
    story.append(Paragraph(
        "Both unit and time weights are computed using the <b>Frank-Wolfe</b> (conditional gradient) "
        "algorithm, which iteratively moves toward the feasible direction that most reduces the objective. "
        "The algorithm is run in two phases: first with "
        "<font name='Courier' size='8.5'>max_iter_pre_sparsify=100</font> iterations to find an initial "
        "solution, then the weights are sparsified (small weights are set to zero) and the algorithm "
        "is re-run with <font name='Courier' size='8.5'>max_iter=10000</font> iterations to refine.",
        S["body"]
    ))
    story.append(Paragraph(
        "Validation against Stata's <font name='Courier' size='8.5'>sdid</font> command (Pailanir & Clarke, 2022) "
        "shows that both implementations converge to the same mathematical optimum. "
        "The maximum absolute difference between Python and Stata weights is on the order of 10-8 — "
        "pure floating-point rounding noise from different arithmetic environments "
        "(NumPy/C vs Stata's Mata engine, both using IEEE 754 double precision). "
        "At 4 decimal places, the weights are identical across all methods and cohorts.",
        S["body"]
    ))
    precision_data = [
        [Paragraph("<b>Method</b>",  ps_th),
         Paragraph("<b>max |omega_Py - omega_Stata|</b>", ps_th),
         Paragraph("<b>max |lambda_Py - lambda_Stata|</b>", ps_th)],
        [Paragraph("SDID", ps_td2), Paragraph("4.8 x 10^-8", ps_td), Paragraph("4.0 x 10^-8", ps_td)],
        [Paragraph("SC",   ps_td2), Paragraph("5.0 x 10^-8", ps_td), Paragraph("0  (exact)",  ps_td)],
        [Paragraph("DiD",  ps_td2), Paragraph("1.1 x 10^-8", ps_td), Paragraph("4.4 x 10^-8", ps_td)],
    ]
    precision_t = Table(precision_data, colWidths=[3*cm, 7.5*cm, 6*cm])
    precision_t.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0), TABLE_HEAD),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, TABLE_ALT]),
        ("GRID",           (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",     (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",    (0,0),(-1,-1), 7), ("ALIGN", (1,1),(-1,-1), "CENTER"),
        ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(precision_t)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Note: lambda_SC = 0 exactly in both packages because it is a fixed design value, "
        "not a numerical result.",
        S["note"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 9. HOW TO CITE
    # ══════════════════════════════════════════
    story.append(Paragraph("9. How to Cite", S["h1"]))
    story.append(section_rule(S))
    story.append(Paragraph(
        "If you use <b>synthdid</b> in your research, please cite both the original paper "
        "that introduces the SDID estimator and this software package:",
        S["body"]
    ))

    story.append(Paragraph("<b>Original paper</b>", S["h3"]))
    story.append(code_block([
        "@article{Arkhangelsky2021,",
        "  author  = {Arkhangelsky, Dmitry and Athey, Susan and",
        "             Hirshberg, David A. and Imbens, Guido W.",
        "             and Wager, Stefan},",
        "  title   = {Synthetic Difference-in-Differences},",
        "  journal = {American Economic Review},",
        "  volume  = {111},",
        "  number  = {12},",
        "  pages   = {4088--4118},",
        "  year    = {2021},",
        "  doi     = {10.1257/aer.20190159}",
        "}",
    ], S))

    story.append(Paragraph("<b>This software package</b>", S["h3"]))
    story.append(code_block([
        "@software{synthdid,",
        "  author  = {Flores, Jhon and Caceres, Franco and",
        "             Grijalba, Rodrigo and Quispe, Alexander",
        "             and Clarke, Damian and Nicho, Jesus},",
        "  title   = {{synthdid: Synthetic Difference-in-Differences",
        "             Estimation in Python}},",
        "  year    = {2024},",
        "  url     = {https://github.com/d2cml-ai/synthdid.py}",
        "}",
    ], S))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1")))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "MIT License · D2CML Team · https://github.com/d2cml-ai/synthdid.py",
        ParagraphStyle("footer_text", fontName="Helvetica", fontSize=8,
                       textColor=GRAY_TEXT, alignment=TA_CENTER)
    ))

    # ── Build ─────────────────────────────────────────────────────────
    doc.build(
        story,
        onFirstPage=cover_page,
        onLaterPages=decorator,
    )
    print(f"Manual saved to: {output_path}")


if __name__ == "__main__":
    build_manual("Manual.pdf")
