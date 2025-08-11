import logging
from io import BytesIO
from datetime import datetime

import pandas as pd
from django.db.models import Q
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfgen import canvas
import os

from .models import Action, Profile
from .charts import _actions_for_user

logger = logging.getLogger(__name__)

COLUMNS = [
    "ACT-ID",
    "Titre",
    "Statut",
    "Priorité",
    "Budget (DZD)",
    "Responsables",
    "Délais",
    "Date réalisation",
    "J",
    "P",
    "D",
    "C",
    "A",
    "Plan",
    "Fichier",
    "Feuille",
    "RowIndex",
]


def build_actions_queryset(user, params):
    qs = _actions_for_user(user)
    plan = params.get("plan")
    statut = params.get("statut")
    priorite = params.get("priorite")
    responsable = params.get("responsable")
    q = params.get("q")
    date_from = params.get("from")
    date_to = params.get("to")
    if plan:
        qs = qs.filter(plan_id=plan)
    if statut:
        qs = qs.filter(statut=statut)
    if priorite:
        qs = qs.filter(priorite=priorite)
    if responsable:
        qs = qs.filter(responsables__username=responsable)
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(commentaire__icontains=q))
    if date_from:
        qs = qs.filter(date_creation__gte=date_from)
    if date_to:
        qs = qs.filter(date_creation__lte=date_to)
    return qs.select_related("plan").prefetch_related("responsables")


def _action_to_row(action):
    responsables = ", ".join(action.responsables.values_list("username", flat=True))
    return [
        action.act_id,
        action.titre,
        action.statut,
        action.priorite,
        float(action.budget_dzd) if action.budget_dzd is not None else None,
        responsables,
        action.delais.isoformat() if action.delais else None,
        action.date_realisation.isoformat() if action.date_realisation else None,
        action.j,
        int(action.p),
        int(action.d),
        int(action.c),
        int(action.a),
        action.plan.nom,
        action.excel_fichier,
        action.excel_feuille,
        action.excel_row_index,
    ]


def export_actions_excel(qs, filters=None):
    filters = filters or {}
    total = qs.count()
    logger.info("EXPORT", extra={"payload": {"filters": dict(filters), "format": "excel", "count": total}})
    if total > 50_000:
        wb = Workbook(write_only=True)
        ws = wb.create_sheet(title="Actions")
        ws.append(COLUMNS)
        for action in qs.iterator(chunk_size=5000):
            ws.append(_action_to_row(action))
        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream
    data = [_action_to_row(a) for a in qs]
    df = pd.DataFrame(data, columns=COLUMNS)
    stream = BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Actions")
        ws = writer.sheets["Actions"]
        ws.freeze_panes = "A2"
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="DDDDDD")
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length + 2
    stream.seek(0)
    return stream


def _header_footer(canvas_obj, doc, filters_summary):
    width, height = landscape(A4)
    logo_path = os.path.join(os.path.dirname(__file__), "static", "logo.png")
    if os.path.exists(logo_path):
        canvas_obj.drawImage(logo_path, 40, height - 40, width=40, height=40, preserveAspectRatio=True, mask='auto')
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawString(80, height - 20, "Export Actions")
    canvas_obj.drawString(40, 20, f"Généré le {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    canvas_obj.drawRightString(width - 40, 20, filters_summary)


def export_actions_pdf(qs, filters=None):
    filters = filters or {}
    total = qs.count()
    logger.info("EXPORT", extra={"payload": {"filters": dict(filters), "format": "pdf", "count": total}})
    data = [_action_to_row(a) for a in qs]
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    story = [Paragraph("Export Actions", styles["Title"])]
    table = Table([COLUMNS] + data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    filters_summary = ", ".join(f"{k}={v}" for k, v in filters.items())
    doc.build(story, onFirstPage=lambda c, d: _header_footer(c, d, filters_summary), onLaterPages=lambda c, d: _header_footer(c, d, filters_summary))
    buffer.seek(0)
    return buffer
