import logging
from io import BytesIO
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse

from .exporters import build_actions_queryset
from .charts import get_counters, get_progress, compare_plans
from .permissions import RolePermission
from .report_builder import build_pdf

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ACT-ID": lambda a: a.act_id,
    "Titre": lambda a: a.titre,
    "Statut": lambda a: a.statut,
    "Priorité": lambda a: a.priorite,
    "Responsables": lambda a: ", ".join(a.responsables.values_list("username", flat=True)),
    "Délais": lambda a: a.delais.isoformat() if a.delais else "",
    "J": lambda a: a.j,
}


def _row_from_action(action, columns):
    return [COLUMN_MAP.get(col, lambda a: "")(action) for col in columns]


class CustomReportView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        data = request.data
        filters = data.get("filters", {})
        sections = data.get("sections", [])
        dry_run = data.get("dry_run", False)
        qs = build_actions_queryset(request.user, filters)
        pdf_data = {"sections": sections}
        if any(s.get("type") == "summary_kpis" for s in sections):
            pdf_data["kpis"] = get_counters(request.user, filters)
        if any(s.get("type") == "grouped_table" for s in sections):
            section = next(s for s in sections if s.get("type") == "grouped_table")
            group_by = section.get("group_by")
            columns = section.get(
                "columns",
                [
                    "ACT-ID",
                    "Titre",
                    "Statut",
                    "Priorité",
                    "Responsables",
                    "Délais",
                    "J",
                ],
            )
            actions = list(qs.select_related("plan").prefetch_related("responsables")[:10000])
            groups = {}
            for a in actions:
                if group_by == "plan":
                    key = a.plan.nom if a.plan else ""
                elif group_by == "statut":
                    key = a.statut
                elif group_by == "priorite":
                    key = a.priorite
                elif group_by == "responsable":
                    key = ", ".join(a.responsables.values_list("username", flat=True))
                else:
                    key = ""
                groups.setdefault(key, []).append(_row_from_action(a, columns))
            pdf_data["group_columns"] = columns
            pdf_data["groups"] = list(groups.items())
        if any(s.get("type") == "top_late" for s in sections):
            section = next(s for s in sections if s.get("type") == "top_late")
            limit = section.get("limit", 20)
            columns = section.get(
                "columns",
                [
                    "ACT-ID",
                    "Titre",
                    "Statut",
                    "Priorité",
                    "Responsables",
                    "Délais",
                    "J",
                ],
            )
            late_qs = qs.filter(j__lt=0).order_by("j")[:limit]
            pdf_data["late_columns"] = columns
            pdf_data["top_late"] = [_row_from_action(a, columns) for a in late_qs]
        if any(s.get("type") == "charts" for s in sections):
            section = next(s for s in sections if s.get("type") == "charts")
            include = section.get("include", [])
            if "progress" in include:
                pdf_data["progress"] = get_progress(request.user, params=filters)
            if "compare_plans" in include:
                pdf_data["compare_plans"] = compare_plans(request.user, params=filters)
        if dry_run:
            preview = {
                "pages_estimate": 1,
                "kpis": pdf_data.get("kpis", {}),
                "groups_preview": {k: v[:1] for k, v in pdf_data.get("groups", [])},
                "charts_info": {
                    "progress": bool(pdf_data.get("progress")),
                    "compare_plans": bool(pdf_data.get("compare_plans")),
                },
            }
            logger.info(
                "REPORT_CUSTOM %s",
                {"payload": data, "sent": False, "count": qs.count()},
            )
            return Response(preview)
        buffer = BytesIO()
        build_pdf(buffer, data.get("title", "Rapport"), data.get("layout", {}), pdf_data)
        logger.info(
            "REPORT_CUSTOM %s",
            {"payload": data, "sent": True, "count": qs.count()},
        )
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        filename = f"report_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
