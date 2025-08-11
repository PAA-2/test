from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plan, Action
from .serializers import PlanSerializer, ActionSerializer
from .permissions import RolePermission
from .filters import ActionFilter
from .services.excel_io import read_plan, apply_update


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated, RolePermission]


class ActionViewSet(viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    lookup_field = "act_id"
    filterset_class = ActionFilter

    def perform_update(self, serializer):
        action_obj = serializer.save()
        apply_update(action_obj.act_id)

    @action(detail=True, methods=["post"])
    def validate(self, request, act_id=None):
        action_obj = self.get_object()
        action_obj.c = True
        action_obj.save()
        apply_update(action_obj.act_id)
        return Response({"status": "validated"})

    @action(detail=True, methods=["post"])
    def close(self, request, act_id=None):
        action_obj = self.get_object()
        action_obj.a = True
        action_obj.save()
        apply_update(action_obj.act_id)
        return Response({"status": "closed"})

    @action(detail=True, methods=["post"])
    def reject(self, request, act_id=None):
        action_obj = self.get_object()
        action_obj.statut = "rejected"
        action_obj.save()
        apply_update(action_obj.act_id)
        return Response({"status": "rejected"})

    @action(detail=True, methods=["post"])
    def assign(self, request, act_id=None):
        action_obj = self.get_object()
        responsables = request.data.get("responsables", [])
        action_obj.responsables.set(responsables)
        apply_update(action_obj.act_id)
        return Response({"status": "assigned"})


class ExcelPreview(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        plan_id = request.query_params.get("plan")
        plan = get_object_or_404(Plan, id=plan_id)
        data = read_plan(plan)
        return Response({"rows": data})


class ExcelRefresh(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        plan_id = request.data.get("plan")
        plan = get_object_or_404(Plan, id=plan_id)
        data = read_plan(plan)
        return Response({"rows": data})
