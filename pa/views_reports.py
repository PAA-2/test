import logging
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import RolePermission
from .services.exports import query_actions_for_export, DEFAULT_COLUMNS, _rows_from_queryset
from .services.report_builder import build_custom_report
from .charts import get_counters, get_progress, compare_plans

logger = logging.getLogger(__name__)


class CustomReportView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        payload = request.data
        filters = payload.get("filters", {})
        dry_run = payload.get("dry_run", False)
        sections = payload.get("sections", [])
        qs = query_actions_for_export(request.user, filters)
        if dry_run:
            preview = {"pages_estimate": 1}
            if any(s.get("type") == "kpi" for s in sections):
                preview["kpis"] = get_counters(request.user, filters)
            if any(s.get("type") == "table" for s in sections):
                columns = sections[0].get("columns", DEFAULT_COLUMNS)
                preview["table_preview"] = _rows_from_queryset(qs[:1], columns)
            if any(s.get("type") == "charts" for s in sections):
                preview["charts_info"] = {
                    "progress": bool(get_progress(request.user, filters)),
                    "compare_plans": bool(compare_plans(request.user, filters)),
                }
            return Response(preview)
        buffer = build_custom_report(request.user, payload)
        filename = f"rapport_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
