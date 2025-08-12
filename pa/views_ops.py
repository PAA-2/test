import subprocess
from django.db import connection
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .services import excel_io


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        db_ok = True
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        except Exception:
            db_ok = False

        excel_ok = hasattr(excel_io, "read_plan")
        try:
            version = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
        except Exception:
            version = "unknown"

        return JsonResponse({
            "status": "ok" if db_ok else "error",
            "db": db_ok,
            "excel_io": excel_ok,
            "version": version,
        })
