from django.http import HttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import RolePermission
from .services.exports import (
    DEFAULT_COLUMNS,
    query_actions_for_export,
    to_excel,
    to_pdf_table,
)

MAX_ROWS_EXPORT = 20_000


class ExportExcelView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        qs = query_actions_for_export(request.user, request.query_params)
        if qs.count() > MAX_ROWS_EXPORT:
            return Response({"detail": "Too many rows"}, status=400)
        cols_param = request.query_params.get("columns")
        columns = None
        if cols_param:
            columns = [c for c in cols_param.split(",") if c in DEFAULT_COLUMNS]
        stream = to_excel(qs, columns)
        filename = timezone.now().strftime("actions_%Y%m%d_%H%M.xlsx")
        response = HttpResponse(
            stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class ExportPdfView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        qs = query_actions_for_export(request.user, request.query_params)
        if qs.count() > MAX_ROWS_EXPORT:
            return Response({"detail": "Too many rows"}, status=400)
        cols_param = request.query_params.get("columns")
        columns = None
        if cols_param:
            columns = [c for c in cols_param.split(",") if c in DEFAULT_COLUMNS]
        stream = to_pdf_table(qs, columns)
        filename = timezone.now().strftime("actions_%Y%m%d_%H%M.pdf")
        response = HttpResponse(stream.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
