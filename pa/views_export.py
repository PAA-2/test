from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .permissions import RolePermission
from .exporters import (
    build_actions_queryset,
    export_actions_excel,
    export_actions_pdf,
)
from django.utils import timezone


class ExportExcelView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        qs = build_actions_queryset(request.user, request.query_params)
        buf = export_actions_excel(qs, request.query_params)
        filename = f"actions_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        response = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response


class ExportPdfView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        qs = build_actions_queryset(request.user, request.query_params)
        buf = export_actions_pdf(qs, request.query_params)
        filename = f"actions_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        response = HttpResponse(buf.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response

