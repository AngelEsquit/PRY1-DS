# -*- coding: utf-8 -*-
"""
Genera Libro_de_Codigos.pdf a partir de Libro_de_Codigos.md.

Reglas de formato aplicadas:
- Fuente Times New Roman, 12 pt para el cuerpo.
- Sin guiones largos (se normalizan a guion corto).
- Sin lineas horizontales de separacion entre secciones.
- Tablas con formato academico "Tabla n. Descripcion" (solo reglas horizontales).
- Caratula con los integrantes.

Uso:  python generar_pdf_code_book.py
"""

import html
import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

BASE = Path(__file__).resolve().parent
MD = BASE / "Libro_de_Codigos.md"
PDF = BASE / "Libro_de_Codigos.pdf"

FONTS = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont("Times", f"{FONTS}/times.ttf"))
pdfmetrics.registerFont(TTFont("Times-Bold", f"{FONTS}/timesbd.ttf"))
pdfmetrics.registerFont(TTFont("Times-Italic", f"{FONTS}/timesi.ttf"))
pdfmetrics.registerFont(TTFont("Times-BoldItalic", f"{FONTS}/timesbi.ttf"))
pdfmetrics.registerFontFamily(
    "Times", normal="Times", bold="Times-Bold",
    italic="Times-Italic", boldItalic="Times-BoldItalic",
)

INTEGRANTES = [
    ("Javier Espana", "23361"),
    ("Angel Esquit", "23221"),
    ("Roberto Barreda", "23354"),
]
# Nombres con tildes reales (se mantienen; solo se prohiben guiones largos).
INTEGRANTES = [
    ("Javier España", "23361"),
    ("Ángel Esquit", "23221"),
    ("Roberto Barreda", "23354"),
]

# ---------------------------------------------------------------- estilos
body = ParagraphStyle(
    "body", fontName="Times", fontSize=12, leading=16,
    alignment=TA_JUSTIFY, spaceAfter=6,
)
h2 = ParagraphStyle(
    "h2", fontName="Times-Bold", fontSize=15, leading=19,
    spaceBefore=16, spaceAfter=8, keepWithNext=True,
)
h3 = ParagraphStyle(
    "h3", fontName="Times-Bold", fontSize=12.5, leading=16,
    spaceBefore=12, spaceAfter=3, keepWithNext=True,
)
bullet = ParagraphStyle(
    "bullet", parent=body, leftIndent=18, firstLineIndent=-10,
    spaceAfter=3,
)
subbullet = ParagraphStyle(
    "subbullet", parent=body, leftIndent=38, firstLineIndent=-10,
    spaceAfter=2,
)
caption = ParagraphStyle(
    "caption", fontName="Times-Bold", fontSize=12, leading=15,
    spaceBefore=6, spaceAfter=6,
)
cell = ParagraphStyle(
    "cell", fontName="Times", fontSize=10, leading=12.5, alignment=TA_LEFT,
)
cell_c = ParagraphStyle("cell_c", parent=cell, alignment=TA_CENTER)
cover_title = ParagraphStyle(
    "cover_title", fontName="Times-Bold", fontSize=30, leading=34,
    alignment=TA_CENTER,
)
cover_sub = ParagraphStyle(
    "cover_sub", fontName="Times", fontSize=14, leading=19, alignment=TA_CENTER,
)
cover_small = ParagraphStyle(
    "cover_small", fontName="Times", fontSize=12, leading=16, alignment=TA_CENTER,
)


def inline(text):
    """Convierte markdown en linea a marcado de reportlab."""
    text = text.replace("—", "-").replace("–", "-")  # em/en dash -> guion corto
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    return text


def build_table(rows):
    """Construye la tabla de calidad con estilo academico (reglas horizontales)."""
    ncols = len(rows[0])
    widths = [1.05, 0.60, 0.65, 2.65]  # proporciones relativas
    total = 16.0 * cm
    scale = total / sum(widths)
    col_widths = [w * scale for w in widths]

    data = []
    for r, row in enumerate(rows):
        out = []
        for c, val in enumerate(row):
            val = val.strip()
            if r == 0:
                out.append(Paragraph(inline(val), ParagraphStyle(
                    "hdr", parent=cell_c, fontName="Times-Bold")))
            elif c == 0:
                out.append(Paragraph(inline(val), ParagraphStyle(
                    "m", parent=cell, fontName="Times-Bold")))
            elif c == ncols - 1:
                out.append(Paragraph(inline(val), cell))
            else:
                out.append(Paragraph(inline(val), cell_c))
        data.append(out)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        # estilo academico: solo reglas horizontales superior, bajo encabezado e inferior
        ("LINEABOVE", (0, 0), (-1, 0), 1.1, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 1.1, colors.black),
    ]))
    return t


def parse_markdown(md):
    lines = md.split("\n")
    story = []
    table_count = 0
    pending_caption = ""  # descripcion para la proxima tabla
    i = 0
    n = len(lines)

    # saltar titulo H1 y subtitulo (van en la caratula)
    while i < n and not lines[i].startswith("## "):
        i += 1

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("---"):  # regla horizontal: se omite
            i += 1
            continue

        if line.startswith("## "):
            title = line[3:].strip()
            story.append(Paragraph(inline(title), h2))
            if "Calidad" in title:
                pending_caption = "Informe de calidad de datos (antes vs. despues del proceso de limpieza)"
            i += 1
            continue

        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:].strip()), h3))
            i += 1
            continue

        # fila de tabla
        if stripped.startswith("|"):
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = []
            for r in block:
                cells = [c.strip() for c in r.strip("|").split("|")]
                if all(set(c) <= set(":- ") for c in cells):  # fila separadora ---
                    continue
                rows.append(cells)
            if rows:
                table_count += 1
                desc = pending_caption or "Datos"
                story.append(Paragraph(
                    f"<b>Tabla {table_count}.</b> <i>{inline(desc)}</i>", caption))
                story.append(build_table(rows))
                story.append(Spacer(1, 6))
                pending_caption = ""
            continue

        # nota final -> parrafo formal (sin la etiqueta "Nota")
        if stripped.startswith("*Nota:"):
            txt = stripped.strip("*")
            txt = re.sub(r"^Nota:\s*", "", txt)
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                "<b>Reproducibilidad y trazabilidad.</b> " + inline(txt), body))
            i += 1
            continue

        # sub-bullet (>= 4 espacios de indentacion)
        m_sub = re.match(r"^\s{4,}[*-]\s+(.*)$", line)
        if m_sub:
            story.append(Paragraph("• " + inline(m_sub.group(1)), subbullet))
            i += 1
            continue

        # bullet de primer nivel
        m_b = re.match(r"^[*-]\s+(.*)$", line)
        if m_b:
            story.append(Paragraph("• " + inline(m_b.group(1)), bullet))
            i += 1
            continue

        # parrafo normal
        story.append(Paragraph(inline(stripped), body))
        i += 1

    return story


def cover_flowables(subtitle):
    els = [Spacer(1, 3.2 * cm)]
    els.append(Paragraph("Code Book", cover_title))
    els.append(Spacer(1, 0.5 * cm))
    els.append(Paragraph(subtitle, cover_sub))
    els.append(Spacer(1, 3.5 * cm))
    els.append(Paragraph("Integrantes", ParagraphStyle(
        "ci", parent=cover_small, fontName="Times-Bold", fontSize=13)))
    els.append(Spacer(1, 0.35 * cm))

    data = [[Paragraph(nombre, ParagraphStyle("cn", parent=cover_small,
                                              alignment=TA_CENTER)),
             Paragraph(carne, ParagraphStyle("cc", parent=cover_small,
                                             alignment=TA_CENTER))]
            for nombre, carne in INTEGRANTES]
    header = [Paragraph("<b>Nombre</b>", ParagraphStyle(
                  "chn", parent=cover_small, alignment=TA_CENTER)),
              Paragraph("<b>Carne</b>", ParagraphStyle(
                  "chc", parent=cover_small, alignment=TA_CENTER))]
    tab = Table([header] + data, colWidths=[7.5 * cm, 3.5 * cm], hAlign="CENTER")
    tab.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    els.append(tab)
    els.append(Spacer(1, 4.5 * cm))
    els.append(Paragraph("Julio 2026", cover_small))
    return els


def main():
    md = MD.read_text(encoding="utf-8")

    # subtitulo desde la segunda linea del markdown (**...**)
    subtitle = "Proyecto 1 - Obtencion y Limpieza de Datos - Data Science"
    for ln in md.split("\n"):
        m = re.match(r"^\*\*(.+)\*\*\s*$", ln.strip())
        if m:
            subtitle = m.group(1).replace("—", "-").replace("–", "-")
            break

    doc = BaseDocTemplate(
        str(PDF), pagesize=letter,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2.5 * cm, bottomMargin=2.2 * cm,
        title="Code Book", author="Javier Espana; Angel Esquit; Roberto Barreda",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")

    def footer(canvas, d):
        canvas.saveState()
        canvas.setFont("Times", 9)
        canvas.drawCentredString(letter[0] / 2, 1.3 * cm, str(canvas.getPageNumber()))
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame]),
        PageTemplate(id="body", frames=[frame], onPage=footer),
    ])

    story = cover_flowables(subtitle)
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())
    story.extend(parse_markdown(md))

    doc.build(story)
    print(f"OK -> {PDF}")


if __name__ == "__main__":
    main()
