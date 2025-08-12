from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import urlencode

from .permissions import RolePermission
from . import charts


def make_cache_key(user_id, path, params):
    serialized = urlencode(sorted(params.items()))
    return f"user:{user_id}:{path}?{serialized}"


class DashboardCounters(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        params = request.query_params.dict()
        key = make_cache_key(request.user.id, request.path, params)
        data = cache.get(key)
        if data is None:
            data = charts.get_counters(request.user, request.query_params)
            cache.set(key, data, 60)
        return Response(data)


class ProgressChart(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        params = request.query_params.dict()
        key = make_cache_key(request.user.id, request.path, params)
        data = cache.get(key)
        if data is None:
            start = request.query_params.get("from")
            end = request.query_params.get("to")
            data = charts.get_progress(request.user, start, end, request.query_params)
            cache.set(key, data, 60)
        return Response(data)


class ComparePlansChart(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        params = request.query_params.dict()
        key = make_cache_key(request.user.id, request.path, params)
        data = cache.get(key)
        if data is None:
            only_active = request.query_params.get("only_active", "true").lower() != "false"
            data = charts.compare_plans(request.user, only_active, request.query_params)
            cache.set(key, data, 60)
        return Response(data)
