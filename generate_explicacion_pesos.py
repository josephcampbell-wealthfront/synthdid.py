"""
Genera Explicacion_pesos.pdf con ecuaciones LaTeX renderizadas via matplotlib mathtext.
"""
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ── Paleta ─────────────────────────────────────────────────────────────────────
DARK      = colors.HexColor("#1a2e4a")
BLUE      = colors.HexColor("#2563eb")
BLUE_LT   = colors.HexColor("#dbeafe")
GREEN     = colors.HexColor("#16a34a")
GREEN_LT  = colors.HexColor("#dcfce7")
ORANGE    = colors.HexColor("#ea580c")
ORANGE_LT = colors.HexColor("#ffedd5")
GRAY      = colors.HexColor("#64748b")
GRAY_LT   = colors.HexColor("#f8fafc")
SLATE     = colors.HexColor("#334155")
ROW_ALT   = colors.HexColor("#f1f5f9")
WHITE     = colors.white
YELLOW_LT = colors.HexColor("#fefce8")

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
BODY_W = PAGE_W - 2 * MARGIN


# ── Renderizador de ecuaciones LaTeX ──────────────────────────────────────────
def latex_img(latex: str, fontsize: int = 13, dpi: int = 160,
              bg: str = "none", color: str = "#0f172a") -> Image:
    """
    Convierte una cadena LaTeX a una imagen ReportLab usando matplotlib mathtext.
    bg='none' = transparente; de lo contrario color CSS (ej. '#f8fafc').
    """
    fig = plt.figure()
    fig.patch.set_alpha(0.0 if bg == "none" else 1.0)
    if bg != "none":
        fig.patch.set_facecolor(bg)

    txt = fig.text(0.0, 0.5, f"${latex}$",
                   fontsize=fontsize, va="center", ha="left",
                   color=color,
                   fontfamily="DejaVu Sans")  # mathtext built-in
    # Primer render para medir
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bb = txt.get_window_extent(renderer)
    pad_x, pad_y = 12, 8
    fig_w = (bb.width  + pad_x * 2) / dpi
    fig_h = (bb.height + pad_y * 2) / dpi
    fig.set_size_inches(max(fig_w, 0.5), max(fig_h, 0.3))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                transparent=(bg == "none"),
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    # Escalar al ancho del cuerpo (max) manteniendo aspecto
    img = Image(buf)
    max_w = BODY_W - 1.0 * cm
    if img.drawWidth > max_w:
        scale = max_w / img.drawWidth
        img.drawWidth  *= scale
        img.drawHeight *= scale
    return img


def latex_block(latex: str, fontsize: int = 13, dpi: int = 160,
                bg: str = "#f8fafc", borde: object = None) -> Table:
    """Ecuación centrada dentro de una caja con fondo."""
    img = latex_img(latex, fontsize=fontsize, dpi=dpi, bg=bg)
    borde = borde or colors.HexColor("#94a3b8")
    t = Table([[img]], colWidths=[BODY_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor(bg) if bg != "none" else WHITE),
        ("BOX",           (0,0),(-1,-1), 1.0, borde),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
    ]))
    return t


def latex_inline(latex: str, fontsize: int = 11) -> Image:
    """Ecuacion inline (sin caja, transparente)."""
    return latex_img(latex, fontsize=fontsize, bg="none")


# ── Cabecera / Pie ─────────────────────────────────────────────────────────────
def header_footer(c, doc):
    c.saveState()
    w, h = A4
    if doc.page > 1:
        c.setFillColor(DARK)
        c.rect(0, h - 1.0*cm, w, 1.0*cm, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 8)
        c.drawString(MARGIN, h - 0.67*cm, "Explicacion de Pesos: SDID vs SC vs DiD")
        c.setFont("Helvetica", 8)
        c.drawRightString(w - MARGIN, h - 0.67*cm, "d2cml-ai / synthdid.py")
        c.setFillColor(GRAY_LT)
        c.rect(0, 0, w, 0.8*cm, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.line(0, 0.8*cm, w, 0.8*cm)
        c.setFillColor(GRAY); c.setFont("Helvetica", 7.5)
        c.drawString(MARGIN, 0.28*cm, "Dataset: Cigar (Baltagi, 2002) - 46 estados EE.UU., 1963-1992")
        c.drawRightString(w - MARGIN, 0.28*cm, f"Pagina {doc.page}")
    c.restoreState()


def portada(c, doc):
    c.saveState()
    w, h = A4
    c.setFillColor(DARK); c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#0f172a")); c.rect(0, 0, w, h*0.38, fill=1, stroke=0)
    c.setFillColor(BLUE); c.rect(0, h*0.38, w, 0.25*cm, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(w/2, h*0.73, "Explicacion de Pesos")
    c.setFont("Helvetica-Bold", 20); c.setFillColor(colors.HexColor("#93c5fd"))
    c.drawCentredString(w/2, h*0.665, "Omega (unidades) y Lambda (tiempo)")
    c.setFont("Helvetica", 13); c.setFillColor(colors.HexColor("#bfdbfe"))
    c.drawCentredString(w/2, h*0.625, "SDID   |   SC   |   DiD")
    c.setStrokeColor(colors.HexColor("#3b82f6")); c.setLineWidth(1.0)
    c.line(MARGIN*2.5, h*0.605, w - MARGIN*2.5, h*0.605)
    items = [
        ("Contenido",  "Tablas 7 a 13 con ecuaciones y derivaciones matematicas"),
        ("Dataset",    "Cigar (Baltagi, 2002) - 46 estados, 1963-1992"),
        ("Comparacion","Python (synthdid.py)  vs  Stata (sdid)"),
        ("Cohortes",   "1975, 1976, 1978, 1979, 1981, 1983, 1986"),
    ]
    for i, (k, v) in enumerate(items):
        y = h*0.578 - i*0.038*h
        c.setFont("Helvetica-Bold", 9); c.setFillColor(colors.HexColor("#93c5fd"))
        c.drawString(MARGIN*2.5, y, f"{k}:")
        c.setFont("Helvetica", 9); c.setFillColor(WHITE)
        c.drawString(MARGIN*2.5 + 2.5*cm, y, v)
    c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawCentredString(w/2, h*0.27, "Flores · Caceres · Grijalba · Quispe · Clarke · Nicho")
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(w/2, 0.9*cm, "MIT License  ·  github.com/d2cml-ai/synthdid.py")
    c.restoreState()


# ── Estilos ────────────────────────────────────────────────────────────────────
def estilos():
    S = {}
    S["h1"]     = ParagraphStyle("h1",  fontName="Helvetica-Bold", fontSize=17,
                                  textColor=DARK, spaceAfter=6, spaceBefore=18)
    S["h2"]     = ParagraphStyle("h2",  fontName="Helvetica-Bold", fontSize=12,
                                  textColor=DARK, spaceAfter=5, spaceBefore=12)
    S["h3"]     = ParagraphStyle("h3",  fontName="Helvetica-Bold", fontSize=10.5,
                                  textColor=BLUE, spaceAfter=4, spaceBefore=9)
    S["body"]   = ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
                                  leading=15.5, textColor=SLATE, spaceAfter=5,
                                  alignment=TA_JUSTIFY)
    S["body_l"] = ParagraphStyle("body_l", fontName="Helvetica", fontSize=9.5,
                                  leading=15.5, textColor=SLATE, spaceAfter=5)
    S["bullet"] = ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.5,
                                  leading=14.5, textColor=SLATE,
                                  leftIndent=16, spaceAfter=3)
    S["nota"]   = ParagraphStyle("nota", fontName="Helvetica-Oblique", fontSize=8.5,
                                  leading=12.5, textColor=GRAY,
                                  spaceAfter=4, leftIndent=8)
    S["th"]     = ParagraphStyle("th",  fontName="Helvetica-Bold",  fontSize=8.5,
                                  textColor=WHITE, alignment=TA_CENTER, leading=12)
    S["td"]     = ParagraphStyle("td",  fontName="Helvetica",       fontSize=8.5,
                                  textColor=SLATE, alignment=TA_CENTER, leading=12)
    S["td_m"]   = ParagraphStyle("td_m", fontName="Courier",        fontSize=8.5,
                                  textColor=SLATE, alignment=TA_CENTER, leading=12)
    S["td_l"]   = ParagraphStyle("td_l", fontName="Helvetica",      fontSize=8.5,
                                  textColor=SLATE, alignment=TA_LEFT,   leading=12)
    return S


# ── Helpers visuales ───────────────────────────────────────────────────────────
def linea(color=BLUE):
    return HRFlowable(width="100%", thickness=1.2, color=color, spaceAfter=5)

def esp(h=0.3):
    return Spacer(1, h*cm)

def caja(texto, S, bg=BLUE_LT, borde=BLUE, titulo=None):
    ps = ParagraphStyle("cj", fontName="Helvetica", fontSize=9.2,
                        leading=14.5, textColor=DARK)
    filas = []
    if titulo:
        filas.append([Table([[Paragraph(titulo, ParagraphStyle(
            "cjt", fontName="Helvetica-Bold", fontSize=9.2,
            textColor=WHITE, leading=13))]],
            colWidths=[BODY_W],
            style=[("BACKGROUND",(0,0),(-1,-1),DARK),
                   ("TOPPADDING",(0,0),(-1,-1),5),
                   ("BOTTOMPADDING",(0,0),(-1,-1),5),
                   ("LEFTPADDING",(0,0),(-1,-1),10)])])
    filas.append([Table([[Paragraph(texto, ps)]], colWidths=[BODY_W],
        style=[("BACKGROUND",(0,0),(-1,-1),bg),
               ("TOPPADDING",(0,0),(-1,-1),8),
               ("BOTTOMPADDING",(0,0),(-1,-1),8),
               ("LEFTPADDING",(0,0),(-1,-1),12),
               ("RIGHTPADDING",(0,0),(-1,-1),12)])])
    t = Table(filas, colWidths=[BODY_W])
    t.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),1.2,borde),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def etiqueta(texto, S):
    ps = ParagraphStyle("et", fontName="Helvetica-Bold", fontSize=9,
                        textColor=WHITE)
    t = Table([[Paragraph(texto, ps)]], colWidths=[BODY_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), DARK),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ]))
    return t

def tabla(S, header, filas, anchos=None, marcar_ult=False, col_verde=None):
    hrow = [Paragraph(str(c), S["th"]) for c in header]
    data = [hrow] + [
        [Paragraph(str(c), S["td_m"] if j == 0 else S["td"])
         for j, c in enumerate(fila)]
        for fila in filas
    ]
    n  = len(header)
    cw = anchos or [BODY_W/n]*n
    t  = Table(data, colWidths=cw, repeatRows=1)
    style = [
        ("BACKGROUND",    (0,0),(-1,0),  DARK),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, ROW_ALT]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]
    if marcar_ult:
        style += [("BACKGROUND",(0,-1),(-1,-1), YELLOW_LT),
                  ("FONTNAME",  (0,-1),(-1,-1), "Helvetica-Bold"),
                  ("TEXTCOLOR", (0,-1),(-1,-1), colors.HexColor("#78350f"))]
    if col_verde is not None:
        style.append(("BACKGROUND",(col_verde,1),(col_verde,-1), GREEN_LT))
    t.setStyle(TableStyle(style))
    return t

def tabla_comp(S, header, filas, anchos=None):
    ps_h = ParagraphStyle("tch", fontName="Helvetica-Bold", fontSize=8.5,
                           textColor=WHITE, alignment=TA_CENTER, leading=12)
    ps_k = ParagraphStyle("tck", fontName="Helvetica-Bold", fontSize=8.5,
                           textColor=DARK, alignment=TA_LEFT, leading=13)
    ps_v = ParagraphStyle("tcv", fontName="Helvetica", fontSize=8.5,
                           textColor=SLATE, alignment=TA_LEFT, leading=13)
    hrow = [Paragraph(str(c), ps_h) for c in header]
    data = [hrow] + [
        [Paragraph(str(c).replace("\n","<br/>"), ps_k if i==0 else ps_v)
         for i, c in enumerate(fila)]
        for fila in filas
    ]
    n  = len(header)
    cw = anchos or [BODY_W/n]*n
    t  = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  DARK),
        ("BACKGROUND",    (0,1),(0,-1),  BLUE_LT),
        ("ROWBACKGROUNDS",(1,1),(-1,-1), [WHITE, ROW_ALT]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# ECUACIONES (todas renderizadas en LaTeX)
# ══════════════════════════════════════════════════════════════════════════════
def eq_omega_sdid():
    return latex_block(
        r"\hat{\omega}^{SDID} = \arg\min_{\omega \in \Delta(N_0)}"
        r"\;\sum_{t=1}^{T_0}\left(\sum_{i=1}^{N_0}\omega_i Y_{it}"
        r" - \bar{Y}_{t}^{tr}\right)^{2}"
        r"\;+\;\zeta_\omega^2\,T_0\,\|\omega\|^2",
        fontsize=12, bg="#f0f9ff", borde=BLUE
    )

def eq_zeta_omega():
    return latex_block(
        r"\zeta_\omega = \eta_\omega\,\hat{\sigma},\qquad"
        r"\eta_\omega = (N_1 T_1)^{1/4},\qquad"
        r"\hat{\sigma} = \sqrt{\mathrm{Var}(\Delta Y_{it})},\quad"
        r"\Delta Y_{it} = Y_{it} - Y_{i,t-1}",
        fontsize=12, bg="#f0f9ff", borde=BLUE
    )

def eq_omega_constraint():
    return latex_block(
        r"\omega_i \geq 0 \;\;\forall\,i, \qquad"
        r"\sum_{i=1}^{N_0} \omega_i = 1"
        r"\quad\Rightarrow\quad \omega \in \Delta(N_0)",
        fontsize=12
    )

def eq_lambda_sdid():
    return latex_block(
        r"\hat{\lambda}^{SDID} = \arg\min_{\lambda \in \Delta(T_0)}"
        r"\;\sum_{i=1}^{N_0}\left(\sum_{t=1}^{T_0}\lambda_t Y_{it}"
        r" - \bar{Y}_{i}^{post}\right)^{2}"
        r"\;+\;\zeta_\lambda^2\,N_0\,\|\lambda\|^2",
        fontsize=12, bg="#f0f9ff", borde=BLUE
    )

def eq_zeta_lambda():
    return latex_block(
        r"\zeta_\lambda = 10^{-6}\,\hat{\sigma} \;\ll\; \zeta_\omega"
        r"\qquad\Rightarrow\qquad"
        r"\mathrm{alta\ concentracion\ temporal}",
        fontsize=12
    )

def eq_lambda_sc():
    return latex_block(
        r"\lambda_t^{SC} = 0 \quad \forall\; t = 1, \ldots, T_0"
        r"\qquad(\mathrm{restriccion\ de\ diseno,\ no\ optimizacion})",
        fontsize=12, bg="#fff7ed", borde=ORANGE
    )

def eq_lambda_did():
    return latex_block(
        r"\lambda_t^{DiD} = \frac{1}{T_0} \quad \forall\; t = 1, \ldots, T_0"
        r"\qquad(\mathrm{uniforme,\ sin\ optimizacion})",
        fontsize=12, bg="#fff7ed", borde=ORANGE
    )

def eq_omega_sc():
    return latex_block(
        r"\hat{\omega}^{SC} = \arg\min_{\omega \in \Delta(N_0)}"
        r"\;\sum_{t=1}^{T_0}\left(\sum_{i}\omega_i Y_{it}"
        r" - \bar{Y}_{t}^{tr}\right)^{2}"
        r"\;+\;(10^{-6}\hat{\sigma})^2\,T_0\,\|\omega\|^2",
        fontsize=12, bg="#fff7ed", borde=ORANGE
    )

def eq_omega_did():
    return latex_block(
        r"\omega_i^{DiD} = \frac{1}{N_0} \quad \forall\; i = 1, \ldots, N_0"
        r"\qquad\Rightarrow\qquad"
        r"\mathrm{todos\ los\ estados\ pesan\ igual}",
        fontsize=12, bg="#fff7ed", borde=ORANGE
    )

def eq_delta_omega():
    return latex_block(
        r"\delta_\omega = \max_{k}\;\max_{i \in \{1,\ldots,N_0\}}"
        r"\;\left|\hat{\omega}_i^{Py}(k) - \hat{\omega}_i^{Stata}(k)\right|",
        fontsize=12
    )

def eq_delta_lambda():
    return latex_block(
        r"\delta_\lambda = \max_{k}\;\max_{t \in \{1,\ldots,T_0(k)\}}"
        r"\;\left|\hat{\lambda}_t^{Py}(k) - \hat{\lambda}_t^{Stata}(k)\right|",
        fontsize=12
    )

def eq_frank_wolfe():
    return latex_block(
        r"g^{(k)} = \nabla f(\omega^{(k)}), \quad"
        r"s^{(k)} = \arg\min_{s \in \Delta(N_0)} (g^{(k)})^{\top} s, \quad"
        r"\gamma^{(k)} = \arg\min_{\gamma \in [0,1]}"
        r"\;f(\omega^{(k)} + \gamma(s^{(k)} - \omega^{(k)}))",
        fontsize=11
    )

def eq_fw_update():
    return latex_block(
        r"\omega^{(k+1)} = \omega^{(k)} + \gamma^{(k)}(s^{(k)} - \omega^{(k)})"
        r"\qquad\mathrm{Parada{:}}\; f(\omega^{(k)}) - f(\omega^*) < 10^{-5}\hat{\sigma}",
        fontsize=12
    )

def eq_att():
    return latex_block(
        r"\hat{\tau}^{SDID} = \sum_k w_k\left["
        r"\left(\bar{Y}_{tr,post}^{(k)} - \bar{Y}_{tr,pre}^{(k)}\right)"
        r" - \sum_i \hat{\omega}_i^{(k)}"
        r"\left(\bar{Y}_{i,post}^{(k)} - \bar{Y}_{i,pre}^{(k)}\right)\right]",
        fontsize=12, bg="#f0fdf4", borde=GREEN
    )

def eq_att_did():
    return latex_block(
        r"\hat{\tau}^{DiD} ="
        r"\left(\bar{Y}_{tr,post} - \bar{Y}_{tr,pre}\right)"
        r" - \left(\bar{Y}_{co,post} - \bar{Y}_{co,pre}\right)",
        fontsize=12, bg="#fff7ed", borde=ORANGE
    )

def eq_sigma():
    return latex_block(
        r"\hat{\sigma} = \sqrt{\frac{1}{(N_0-1)(T_0-1)}"
        r"\sum_{i,t}\left(\Delta Y_{it} - \overline{\Delta Y}\right)^2},"
        r"\qquad \Delta Y_{it} = Y_{it} - Y_{i,t-1}",
        fontsize=12
    )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DEL DOCUMENTO
# ══════════════════════════════════════════════════════════════════════════════
def build(output="Explicacion_pesos.pdf"):
    doc = SimpleDocTemplate(
        output, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.8*cm, bottomMargin=1.5*cm,
        title="Explicacion de Pesos — synthdid.py",
        author="D2CML Team",
    )
    S     = estilos()
    story = [PageBreak()]  # portada en onFirstPage

    # ── Índice ─────────────────────────────────────────────────────────────────
    story += [Paragraph("Contenido", S["h1"]), linea(), esp(0.1)]
    toc = [
        ("1", "Que son los pesos omega y lambda?", False),
        ("", "  1.1  Pesos de unidades omega_i — QUIEN contribuye al contrafactual", True),
        ("", "  1.2  Pesos temporales lambda_t — CUANDO contribuye al contrafactual", True),
        ("", "  1.3  Comparacion entre los tres metodos", True),
        ("2", "Tabla 7 — Diferencia maxima entre Python y Stata", False),
        ("", "  2.1  Que mide y como se calcula", True),
        ("", "  2.2  Por que hay diferencias numericas (algoritmo Frank-Wolfe)", True),
        ("3", "Tablas 8-10 — Pesos temporales lambda por metodo", False),
        ("", "  3.1  Tabla 8: lambda SDID", True),
        ("", "  3.2  Tabla 9: lambda SC", True),
        ("", "  3.3  Tabla 10: lambda DiD", True),
        ("4", "Tablas 11-13 — Pesos de unidades omega por metodo", False),
        ("", "  4.1  Tabla 11: omega SDID", True),
        ("", "  4.2  Tabla 12: omega SC", True),
        ("", "  4.3  Tabla 13: omega DiD", True),
        ("5", "Comparacion final — los tres metodos", False),
        ("", "  5.1  Resumen de pesos lambda", True),
        ("", "  5.2  Resumen de pesos omega", True),
        ("", "  5.3  Impacto en el ATT estimado", True),
    ]
    for num, txt, sub in toc:
        ps = ParagraphStyle("ti",
            fontName="Helvetica" if sub else "Helvetica-Bold",
            fontSize=9 if sub else 10,
            textColor=GRAY if sub else DARK,
            spaceAfter=2, leading=14)
        story.append(Paragraph(
            f"{num+'.' if num else ''} {txt}", ps))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 1. QUE SON LOS PESOS
    # ══════════════════════════════════════════════════════════════════
    story += [Paragraph("1. Que son los pesos omega y lambda?", S["h1"]), linea()]
    story.append(Paragraph(
        "El estimador SDID — y sus variantes SC y DiD — construye un <b>contrafactual sintetico</b>: "
        "una trayectoria hipotetica de como hubiera evolucionado el grupo tratado sin el tratamiento. "
        "Para eso combina datos de unidades de control y periodos previos usando dos tipos de pesos:",
        S["body"]
    ))

    # Tarjetas omega / lambda
    ps_ic = ParagraphStyle("ic", fontName="Helvetica-Bold", fontSize=26,
                            textColor=BLUE, alignment=TA_CENTER, leading=30)
    ps_it = ParagraphStyle("it", fontName="Helvetica-Bold", fontSize=10.5,
                            textColor=DARK, leading=14)
    ps_is = ParagraphStyle("is", fontName="Helvetica", fontSize=9,
                            textColor=SLATE, leading=13)
    hw = (BODY_W - 0.4*cm) / 2
    def card(sym, tit, desc):
        t = Table([[Paragraph(sym, ps_ic)],
                   [Paragraph(tit, ps_it)],
                   [Paragraph(desc, ps_is)]],
                  colWidths=[hw])
        t.setStyle(TableStyle([
            ("BOX",           (0,0),(-1,-1), 1.0, BLUE),
            ("BACKGROUND",    (0,0),(-1,0),  BLUE_LT),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ]))
        return t
    story.append(Table([[
        card("omega", "omega_i  —  QUIEN",
             "Peso de cada unidad de control.\nDice que estados son mas parecidos\nal grupo tratado."),
        card("lambda", "lambda_t  —  CUANDO",
             "Peso de cada periodo pre-tratamiento.\nDice que anos son mas informativos\npara predecir el contrafactual."),
    ]], colWidths=[hw]*2,
        style=[("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
               ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
               ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"TOP"),
               ("INNERGRID",(0,0),(-1,-1),0,WHITE)]))
    story.append(esp(0.3))

    # 1.1 omega
    story += [Paragraph("1.1  Pesos de unidades  omega_i  (QUIEN)", S["h2"])]
    story.append(caja(
        "<b>En palabras simples:</b> omega_i responde a: ¿cuanto debe pesar el estado i "
        "para que el promedio ponderado de controles replique la tendencia del tratado? "
        "Un estado con omega alto es muy similar al grupo tratado en el periodo pre-tratamiento.",
        S, bg=BLUE_LT, borde=BLUE
    ))
    story += [esp(0.2),
              Paragraph("<b>Ecuacion de optimizacion (SDID):</b>", S["body_l"]),
              eq_omega_sdid(), esp(0.1),
              eq_omega_constraint(), esp(0.1),
              Paragraph("El parametro de regularizacion adaptativo zeta_omega controla "
                        "la dispersion de los pesos:", S["body"]),
              eq_zeta_omega(),
              Paragraph(
                  "A mayor N1 y T1 (celda tratada mas grande), mayor es zeta y mas difusos "
                  "quedan los pesos — reduciendo el riesgo de overfitting.",
                  S["nota"]),
              esp(0.2),
              Paragraph("El estimador de ruido sigma se calcula como:", S["body_l"]),
              eq_sigma(), esp(0.3)]

    # 1.2 lambda
    story += [Paragraph("1.2  Pesos temporales  lambda_t  (CUANDO)", S["h2"])]
    story.append(caja(
        "<b>En palabras simples:</b> lambda_t responde a: ¿que tan informativo es el "
        "año t para predecir el nivel contrafactual justo antes del tratamiento? "
        "Un año con lambda alto es muy representativo del nivel base.",
        S, bg=BLUE_LT, borde=BLUE
    ))
    story += [esp(0.2),
              Paragraph("<b>Ecuacion de optimizacion (SDID):</b>", S["body_l"]),
              eq_lambda_sdid(), esp(0.1),
              eq_zeta_lambda(),
              Paragraph(
                  "La penalizacion en lambda es 10^6 veces menor que en omega. "
                  "Esto permite que casi todo el peso se concentre en 1 o 2 "
                  "años — tipicamente el año inmediatamente anterior al tratamiento.",
                  S["nota"]), esp(0.3)]

    # 1.3 comparacion
    story += [Paragraph("1.3  Comparacion entre los tres metodos", S["h2"])]
    story.append(tabla_comp(S,
        ["Peso", "SDID", "SC", "DiD"],
        [
            ("omega_i\n(unidades)",
             "Optimizacion regularizada\n(zeta = (N1*T1)^(1/4)*sigma)\nPesos difusos: 20-35 estados",
             "Optimizacion con zeta = 1e-6*sigma\n(casi sin penalizacion)\nPesos esparsos: 3-8 estados",
             "Sin optimizacion\nomega = 1/N0\nTodos los estados iguales"),
            ("lambda_t\n(tiempo)",
             "Optimizacion regularizada\n(zeta = 1e-6*sigma)\n76-100% en el ultimo año",
             "Fijo en 0 por diseno\n(no hay optimizacion)\nNo usa info temporal",
             "Sin optimizacion\nlambda = 1/T0\nTodos los años iguales"),
        ],
        anchos=[3.0*cm, 4.8*cm, 4.5*cm, 4.2*cm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 2. TABLA 7
    # ══════════════════════════════════════════════════════════════════
    story += [Paragraph("2. Tabla 7 — Diferencia maxima entre Python y Stata", S["h1"]), linea()]

    story += [Paragraph("2.1  Que mide y como se calcula", S["h2"])]
    story.append(Paragraph(
        "Para cada metodo calcula la maxima diferencia absoluta entre los pesos de "
        "Python y Stata, tomando el maximo sobre todas las cohortes k y unidades (o periodos):",
        S["body"]
    ))
    story += [eq_delta_omega(), esp(0.1), eq_delta_lambda(), esp(0.2)]
    story.append(etiqueta("Tabla 7: Diferencia maxima absoluta de pesos — Python vs Stata", S))
    story.append(tabla(S,
        ["Metodo", "max |omega_Py - omega_Stata|", "max |lambda_Py - lambda_Stata|",
         "Equivalentes a 4 decimales?"],
        [
            ["SDID", "4.8 x 10^-8", "4.0 x 10^-8", "Si (diferencia en 8va cifra)"],
            ["SC",   "5.0 x 10^-8", "0.0 (exacto)", "Si (lambda=0 es valor fijo)"],
            ["DiD",  "1.1 x 10^-8", "4.4 x 10^-8", "Si (diferencia en 8va cifra)"],
        ],
        anchos=[2.2*cm, 4.5*cm, 4.5*cm, 5.3*cm], col_verde=3
    ))
    story.append(esp(0.3))

    story += [Paragraph("2.2  Por que hay diferencias numericas (algoritmo Frank-Wolfe)", S["h2"])]
    story.append(Paragraph(
        "Ambos paquetes resuelven el mismo problema de optimizacion con el "
        "<b>algoritmo Frank-Wolfe</b> (gradiente condicional), pero en motores distintos "
        "(NumPy/C en Python, Mata en Stata). En cada iteracion:",
        S["body"]
    ))
    story += [eq_frank_wolfe(), esp(0.1), eq_fw_update(), esp(0.2)]
    story.append(caja(
        "Con 10.000 iteraciones, el error acumulado de redondeo entre Python y Stata "
        "llega a ~5x10^-8 — equivalente a 1 en la <b>octava cifra decimal</b>. "
        "A efectos practicos, ambas implementaciones son identicas.",
        S, bg=GREEN_LT, borde=GREEN,
        titulo="Conclusion: Python y Stata son numericamente equivalentes"
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 3. TABLAS 8–10 (lambda)
    # ══════════════════════════════════════════════════════════════════
    story += [Paragraph("3. Tablas 8-10 — Pesos temporales lambda por metodo", S["h1"]), linea()]

    # 3.1 lambda SDID
    story += [Paragraph("3.1  Tabla 8 — lambda SDID", S["h2"])]
    story.append(Paragraph(
        "El SDID optimiza lambda con penalizacion minima. Casi todo el peso "
        "se concentra en el <b>ultimo año pre-tratamiento</b>:",
        S["body"]
    ))
    story += [eq_lambda_sdid(), esp(0.2)]
    story.append(etiqueta("Tabla 8: Pesos lambda SDID por año y cohorte  (Python = Stata a 4 decimales)", S))
    story.append(tabla(S,
        ["Año", "c.1975", "c.1976", "c.1978", "c.1979", "c.1981", "c.1983", "c.1986"],
        [
            ["1963", "0",      "0.0011", "0.2195", "0.1566", "0.0641", "0.0711", "0"],
            ["1965", "0.1382", "0.1854", "0",      "0",      "0",      "0",      "0"],
            ["1969", "0",      "0.0034", "0",      "0",      "0",      "0",      "0"],
            ["1974", "0.8618", "0",      "0",      "0",      "0",      "0",      "0"],
            ["1975", "—",      "0.8100", "0",      "0",      "0",      "0",      "0"],
            ["1977", "—",      "—",      "0.7805", "0",      "0",      "0",      "0"],
            ["1978", "—",      "—",      "—",      "0.8434", "0",      "0",      "0"],
            ["1980", "—",      "—",      "—",      "—",      "0.9359", "0",      "0"],
            ["1982", "—",      "—",      "—",      "—",      "—",      "0.9289", "0"],
            ["1985", "—",      "—",      "—",      "—",      "—",      "—",      "1.0000"],
        ],
        anchos=[1.6*cm, 2.3*cm, 2.3*cm, 2.3*cm, 2.3*cm, 2.3*cm, 2.3*cm, 2.3*cm],
        marcar_ult=True
    ))
    story.append(Paragraph(
        "Fila amarilla = ultimo periodo pre-tratamiento (peso dominante). "
        "'—' = periodo post-tratamiento (no aplica lambda).",
        S["nota"]
    ))
    story.append(esp(0.2))
    story.append(etiqueta("Tabla 8b: Concentracion lambda en el ultimo año pre-tratamiento", S))
    story.append(tabla(S,
        ["Cohorte", "Ultimo año pre (T0)", "lambda en T0", "% del total"],
        [
            ["1975", "1974", "0.8618", "86.2%"],
            ["1976", "1975", "0.8100", "81.0%"],
            ["1978", "1977", "0.7805", "78.1%"],
            ["1979", "1978", "0.8434", "84.3%"],
            ["1981", "1980", "0.9359", "93.6%"],
            ["1983", "1982", "0.9289", "92.9%"],
            ["1986", "1985", "1.0000", "100%  — caso extremo"],
        ],
        anchos=[2.5*cm, 4.0*cm, 3.5*cm, 6.5*cm]
    ))
    story.append(esp(0.4))

    # 3.2 lambda SC
    story += [Paragraph("3.2  Tabla 9 — lambda SC", S["h2"])]
    story.append(Paragraph(
        "El SC puro (Abadie et al., 2010) no usa informacion temporal del pre-periodo. "
        "Por diseno estructural del metodo, todos los pesos temporales son cero:",
        S["body"]
    ))
    story += [eq_lambda_sc(), esp(0.2)]
    story.append(etiqueta("Tabla 9: Pesos lambda SC — todos iguales a cero", S))
    story.append(tabla(S,
        ["Cohorte", "lambda_t", "Valor", "Motivo"],
        [["Todas (1975-1986)", "Para todo t = 1,...,T0", "0.0000",
          "Restriccion estructural del metodo SC"]],
        anchos=[4.0*cm, 4.5*cm, 2.5*cm, 5.5*cm]
    ))
    story.append(esp(0.4))

    # 3.3 lambda DiD
    story += [Paragraph("3.3  Tabla 10 — lambda DiD", S["h2"])]
    story.append(Paragraph(
        "El DiD usa pesos temporales uniformes — todos los años pre-tratamiento "
        "pesan igual. Esto implica el supuesto de tendencias paralelas incondicionales:",
        S["body"]
    ))
    story += [eq_lambda_did(), esp(0.2)]
    story.append(etiqueta("Tabla 10: Pesos lambda DiD — uniforme 1/T0 por cohorte", S))
    story.append(tabla(S,
        ["Cohorte", "Año tratamiento", "T0 (periodos pre)", "lambda_t = 1/T0", "Años incluidos"],
        [
            ["c.1975", "1975", "12", "0.0833", "1963 - 1974"],
            ["c.1976", "1976", "13", "0.0769", "1963 - 1975"],
            ["c.1978", "1978", "15", "0.0667", "1963 - 1977"],
            ["c.1979", "1979", "16", "0.0625", "1963 - 1978"],
            ["c.1981", "1981", "18", "0.0556", "1963 - 1980"],
            ["c.1983", "1983", "20", "0.0500", "1963 - 1982"],
            ["c.1986", "1986", "23", "0.0435", "1963 - 1985"],
        ],
        anchos=[2.2*cm, 3.3*cm, 3.5*cm, 3.5*cm, 4.0*cm]
    ))
    story.append(esp(0.2))
    story.append(caja(
        "<b>Riesgo del DiD:</b> supone que 1963 es igual de informativo que 1974 "
        "para predecir el contrafactual de 1975. Si el grupo tratado tenia tendencias "
        "diferentes, esto introduce sesgo en el ATT.",
        S, bg=ORANGE_LT, borde=ORANGE
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 4. TABLAS 11–13 (omega)
    # ══════════════════════════════════════════════════════════════════
    story += [Paragraph("4. Tablas 11-13 — Pesos de unidades omega por metodo", S["h1"]), linea()]

    # 4.1 omega SDID
    story += [Paragraph("4.1  Tabla 11 — omega SDID", S["h2"])]
    story.append(Paragraph(
        "El SDID optimiza omega con <b>penalizacion adaptativa fuerte</b>, lo que "
        "produce pesos difusos entre muchos estados:",
        S["body"]
    ))
    story += [eq_omega_sdid(), esp(0.1), eq_zeta_omega(), esp(0.2)]
    story.append(etiqueta("Tabla 11: Pesos omega SDID por estado y cohorte (10 de 38 estados)", S))
    story.append(tabla(S,
        ["Estado", "c.1975", "c.1976", "c.1978", "c.1979", "c.1981", "c.1983", "c.1986"],
        [
            ["1",   "0.0385", "0",      "0.0463", "0.0084", "0",      "0.0131", "0.0352"],
            ["5",   "0.0503", "0.1436", "0.0078", "0",      "0.0979", "0.0173", "0.0082"],
            ["8",   "0",      "0.0126", "0",      "0.0291", "0.2680", "0.0520", "0.0174"],
            ["14",  "0.0387", "0.1770", "0.0041", "0.0038", "0.1180", "0.0284", "0.0308"],
            ["18",  "0.0579", "0",      "0.1442", "0.0326", "0",      "0.0062", "0.0257"],
            ["22",  "0.0296", "0.0637", "0.0035", "0.0021", "0.2476", "0.0375", "0.0238"],
            ["31",  "0.0137", "0.2523", "0",      "0.0102", "0.1750", "0.0150", "0.0134"],
            ["36",  "0",      "0.1110", "0",      "0.0298", "0.0299", "0.0527", "0.0196"],
            ["39",  "0.0305", "0.1293", "0.0095", "0.0265", "0.0068", "0.0378", "0.0464"],
            ["46",  "0.0535", "0",      "0.0752", "0.0395", "0",      "0.0085", "0.0718"],
        ],
        anchos=[1.8*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm]
    ))
    story.append(Paragraph("Total: 38 estados de control. Se muestran 10 representativos.", S["nota"]))
    story.append(esp(0.4))

    # 4.2 omega SC
    story += [Paragraph("4.2  Tabla 12 — omega SC", S["h2"])]
    story.append(Paragraph(
        "El SC usa la misma formula que el SDID pero con zeta casi nulo, "
        "produciendo <b>pesos muy concentrados</b> en pocos estados:",
        S["body"]
    ))
    story += [eq_omega_sc(), esp(0.2)]
    story.append(etiqueta("Tabla 12: Pesos omega SC por estado y cohorte (estados con peso > 0)", S))
    story.append(tabla(S,
        ["Estado", "c.1975", "c.1976", "c.1978", "c.1979", "c.1981", "c.1983", "c.1986"],
        [
            ["4",   "0",      "0",      "0",      "0.4494", "0",      "0",      "0.0162"],
            ["5",   "0.1193", "0",      "0",      "0",      "0",      "0",      "0"],
            ["8",   "0",      "0.1676", "0.0030", "0",      "0.0435", "0.0285", "0"],
            ["14",  "0",      "0.3841", "0",      "0",      "0",      "0",      "0"],
            ["17",  "0.3106", "0",      "0",      "0.0129", "0",      "0",      "0"],
            ["18",  "0.0480", "0",      "0.3175", "0.0156", "0",      "0.0147", "0.0002"],
            ["22",  "0",      "0",      "0",      "0",      "0.9188", "0.0026", "0"],
            ["30",  "0.0005", "0.3057", "0.0335", "0.0448", "0",      "0.0562", "0.0036"],
            ["33",  "0.0882", "0",      "0.3645", "0",      "0",      "0",      "0.0875"],
            ["46",  "0.1933", "0",      "0.1025", "0.0474", "0",      "0",      "0.2015"],
            ["50",  "0",      "0",      "0",      "0.2647", "0",      "0.3445", "0"],
        ],
        anchos=[1.8*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm]
    ))
    story.append(Paragraph(
        "La mayoria de los 38 estados tiene omega = 0. Caso extremo: "
        "cohorte 1981 con omega_22 = 0.9188 (91.9% del contrafactual en 1 estado).",
        S["nota"]
    ))
    story.append(esp(0.4))

    # 4.3 omega DiD
    story += [Paragraph("4.3  Tabla 13 — omega DiD", S["h2"])]
    story.append(Paragraph(
        "El DiD no optimiza omega. Distribuye el peso uniformemente entre "
        "todos los N0 estados, lo que equivale al estimador TWFE clasico:",
        S["body"]
    ))
    story += [eq_omega_did(), esp(0.1), eq_att_did(), esp(0.2)]
    story.append(etiqueta("Tabla 13: Pesos omega DiD — uniforme para todos los estados", S))
    story.append(tabla(S,
        ["Cohorte", "N0 (controles)", "omega_i = 1/N0", "Aplicacion"],
        [["Todas las cohortes", "38", "0.0263", "Los 38 estados pesan exactamente igual"]],
        anchos=[4.0*cm, 3.0*cm, 3.5*cm, 6.0*cm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 5. COMPARACION FINAL
    # ══════════════════════════════════════════════════════════════════
    story += [Paragraph("5. Comparacion final — los tres metodos", S["h1"]), linea()]

    # 5.1 lambda
    story += [Paragraph("5.1  Resumen de pesos lambda", S["h2"])]
    story.append(tabla_comp(S,
        ["Caracteristica", "SDID", "SC", "DiD"],
        [
            ("Como se obtiene", "Optimizacion Frank-Wolfe\n(zeta = 1e-6*sigma)",
             "Fijo en 0\n(restriccion de diseno)", "Formula directa\n1/T0"),
            ("Años con peso > 0", "1-3 por cohorte", "Ninguno", "Todos los T0 años"),
            ("Concentracion", "Alta: 76-100%\nen el ultimo año",
             "No aplica\n(lambda = 0)", "Nula: todos\na 1/T0"),
            ("Supuesto", "Solo años recientes\nson relevantes",
             "Sin supuesto\ntemporal", "Todos los años\nigualmente relevantes"),
        ],
        anchos=[3.5*cm, 4.4*cm, 4.4*cm, 4.2*cm]
    ))
    story.append(esp(0.3))

    # 5.2 omega
    story += [Paragraph("5.2  Resumen de pesos omega", S["h2"])]
    story.append(tabla_comp(S,
        ["Caracteristica", "SDID", "SC", "DiD"],
        [
            ("Como se obtiene", "Optimizacion Frank-Wolfe\nzeta = (N1*T1)^(1/4)*sigma",
             "Optimizacion Frank-Wolfe\nzeta = 1e-6*sigma", "Formula directa\n1/N0"),
            ("# estados activos", "22-35 de 38\n(pesos difusos)",
             "3-8 de 38\n(pesos esparsos)", "38 de 38\n(todos iguales)"),
            ("Peso maximo tipico", "0.07 - 0.27", "0.31 - 0.92", "0.0263 = 1/38"),
            ("Riesgo", "Bajo\n(regularizacion fuerte)",
             "Alto\n(overfitting al pre-periodo)", "Sesgo por controles\nno representativos"),
        ],
        anchos=[3.5*cm, 4.4*cm, 4.4*cm, 4.2*cm]
    ))
    story.append(esp(0.3))

    # 5.3 ATT
    story += [Paragraph("5.3  Impacto en el ATT estimado", S["h2"])]
    story.append(Paragraph(
        "La formula del ATT que integra ambos tipos de pesos es:", S["body"]
    ))
    story += [eq_att(), esp(0.2)]
    story.append(etiqueta("Tabla 14: Resultados ATT — dataset Cigar, estado 42", S))
    story.append(tabla(S,
        ["Metodo", "ATT estimado", "Diferencia vs SDID", "Por que difiere"],
        [
            ["SDID", "-13.85 paquetes", "— (referencia)",    "Pesos optimos en unidades Y tiempo"],
            ["SC",   "-13.37 paquetes", "+0.48 paquetes",    "No usa informacion temporal (lambda=0)"],
            ["DiD",  "-19.48 paquetes", "-5.63 paquetes",    "Controles no optimos (omega uniforme)"],
        ],
        anchos=[2.2*cm, 3.8*cm, 3.8*cm, 6.7*cm], col_verde=0
    ))
    story.append(esp(0.2))
    story.append(caja(
        "<b>Por que la diferencia DiD vs SDID es 5.6 paquetes?</b>  "
        "Los estados tratados tenian, antes de la ley, una tendencia diferente al promedio nacional. "
        "El DiD no corrige este desbalance (usa todos los estados por igual), mientras que el SDID "
        "asigna mas peso a los estados con trayectoria similar al tratado. "
        "Esa diferencia de 5.6 paquetes es el sesgo del DiD por tendencias no paralelas.",
        S, bg=GREEN_LT, borde=GREEN,
        titulo="Por que el SDID es preferible al DiD en este caso"
    ))
    story.append(esp(0.2))
    story.append(etiqueta("Tabla 15: Equivalencia Python vs Stata — resumen final", S))
    story.append(tabla(S,
        ["Metodo", "Dif. omega", "Dif. lambda", "Dif. ATT", "Conclusion"],
        [
            ["SDID", "4.8 x 10^-8", "4.0 x 10^-8", "< 1 x 10^-6", "Equivalentes"],
            ["SC",   "5.0 x 10^-8", "0 (exacto)",  "< 1 x 10^-6", "Equivalentes"],
            ["DiD",  "1.1 x 10^-8", "4.4 x 10^-8", "< 1 x 10^-6", "Equivalentes"],
        ],
        anchos=[2.0*cm, 3.0*cm, 3.0*cm, 3.0*cm, 5.5*cm], col_verde=4
    ))

    story += [esp(0.6),
              HRFlowable(width="100%", thickness=0.5,
                         color=colors.HexColor("#e2e8f0"), spaceAfter=8),
              Paragraph("Referencias", S["h2"])]
    for r in [
        "[1] Arkhangelsky, Athey, Hirshberg, Imbens & Wager (2021). "
        "<i>Synthetic Difference-in-Differences</i>. American Economic Review, 111(12), 4088-4118.",
        "[2] Abadie, Diamond & Hainmueller (2010). "
        "<i>Synthetic Control Methods</i>. JASA, 105(490), 493-505.",
        "[3] Pailañir & Clarke (2022). <i>SDID: Stata module</i>. Boston College.",
        "[4] Baltagi (2002). <i>Econometrics</i>, 3a ed. Springer.",
    ]:
        story.append(Paragraph(r, ParagraphStyle("ref",
            fontName="Helvetica", fontSize=8.5, leading=13, textColor=GRAY,
            leftIndent=18, firstLineIndent=-18, spaceAfter=5)))

    doc.build(story, onFirstPage=portada, onLaterPages=header_footer)
    print(f"PDF generado: {output}")


if __name__ == "__main__":
    build("Explicacion_pesos.pdf")
