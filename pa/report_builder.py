import os
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.graphics.shapes import Drawing, String


def build_pdf(buffer: BytesIO, title: str, layout: dict, data: dict) -> BytesIO:
    paper = (layout.get("paper", "A4") or "A4").upper()
    orientation = layout.get("orientation", "portrait")
    page_size = {"A4": A4, "A3": A3}.get(paper, A4)
    page_size = landscape(page_size) if orientation == "landscape" else portrait(page_size)
    doc = SimpleDocTemplate(buffer, pagesize=page_size)
    styles = getSampleStyleSheet()
    story = []

    logo_path = layout.get("logo")
    if logo_path and os.path.exists(logo_path):
        from reportlab.platypus import Image

        story.append(Image(logo_path, width=120, height=40))
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles["Normal"]))
    story.append(PageBreak())

    sections = data.get("sections", [])
    for section in sections:
        t = section.get("type")
        if t == "summary_kpis":
            kpis = data.get("kpis", {})
            rows = [[k, v] for k, v in kpis.items()]
            table = Table(rows)
            table.setStyle(
                TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black)])
            )
            story.append(Paragraph("KPIs", styles["Heading2"]))
            story.append(table)
        elif t == "grouped_table":
            columns = data.get("group_columns", [])
            groups = data.get("groups", [])
            story.append(Paragraph("Données groupées", styles["Heading2"]))
            for name, rows in groups:
                story.append(Paragraph(str(name), styles["Heading3"]))
                table = Table([columns] + rows, repeatRows=1)
                table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ]
                    )
                )
                story.append(table)
        elif t == "top_late":
            columns = data.get("late_columns", [])
            rows = data.get("top_late", [])
            story.append(Paragraph("Actions en retard", styles["Heading2"]))
            table = Table([columns] + rows, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ]
                )
            )
            story.append(table)
        elif t == "charts":
            include = section.get("include", [])
            if "progress" in include:
                d = Drawing(400, 200)
                d.add(String(100, 100, "Progress", fontSize=12))
                story.append(d)
            if "compare_plans" in include:
                d = Drawing(400, 200)
                d.add(String(100, 100, "Compare Plans", fontSize=12))
                story.append(d)
        story.append(PageBreak())

    footer = layout.get("footer")

    def _footer(canvas, doc):
        canvas.saveState()
        if footer:
            canvas.setFont("Helvetica", 9)
            canvas.drawString(doc.leftMargin, 20, footer)
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin, 20, str(canvas.getPageNumber())
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer
