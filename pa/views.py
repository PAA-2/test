from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Plan, Action
from .serializers import PlanSerializer, ActionSerializer
from .permissions import RolePermission
from .filters import ActionFilter


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

    @action(detail=True, methods=["post"])
    def validate(self, request, act_id=None):
        action_obj = self.get_object()
        action_obj.c = True
        action_obj.save()
        return Response({"status": "validated"})

    @action(detail=True, methods=["post"])
    def close(self, request, act_id=None):
        action_obj = self.get_object()
        action_obj.a = True
        action_obj.save()
        return Response({"status": "closed"})

    @action(detail=True, methods=["post"])
    def reject(self, request, act_id=None):
        return Response({"status": "rejected"})

    @action(detail=True, methods=["post"])
    def assign(self, request, act_id=None):
        action_obj = self.get_object()
        responsables = request.data.get("responsables", [])
        action_obj.responsables.set(responsables)
        return Response({"status": "assigned"})
