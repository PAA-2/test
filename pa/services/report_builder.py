from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
    PageBreak,
)

from ..charts import get_counters
from .exports import query_actions_for_export, DEFAULT_COLUMNS, _rows_from_queryset


def build_custom_report(user, payload):
    title = payload.get("title", "Rapport PAA")
    layout = payload.get("layout", {})
    sections = payload.get("sections", [])
    filters = payload.get("filters", {})

    paper = (layout.get("paper", "A4") or "A4").upper()
    orientation = layout.get("orientation", "portrait")
    page_size = {"A4": A4, "A3": A3}.get(paper, A4)
    page_size = landscape(page_size) if orientation == "landscape" else portrait(page_size)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=page_size)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles["Normal"]), PageBreak()]

    qs = query_actions_for_export(user, filters)

    if any(s.get("type") == "kpi" for s in sections):
        kpis = get_counters(user, filters)
        rows = [[k, v] for k, v in kpis.items()]
        table = Table(rows)
        table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
        story.append(Paragraph("KPIs", styles["Heading2"]))
        story.append(table)
        story.append(PageBreak())

    for section in sections:
        if section.get("type") == "table":
            columns = section.get("columns", DEFAULT_COLUMNS)
            data = _rows_from_queryset(qs, columns)
            table = Table([columns] + data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ]
                )
            )
            story.append(Paragraph(section.get("title", "Table"), styles["Heading2"]))
            story.append(table)
            story.append(PageBreak())
        elif section.get("type") == "text":
            story.append(Paragraph(section.get("title", "Texte"), styles["Heading2"]))
            story.append(Paragraph(section.get("text", ""), styles["Normal"]))
            story.append(PageBreak())

    footer = layout.get("footer")

    def _footer(canvas, doc):
        canvas.saveState()
        if footer:
            canvas.setFont("Helvetica", 9)
            canvas.drawString(doc.leftMargin, 20, footer)
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 20, str(canvas.getPageNumber()))
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer
