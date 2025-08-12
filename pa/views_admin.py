from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Template, Automation, MenuItem
from .serializers import TemplateSerializer, AutomationSerializer, MenuItemSerializer
from .services.template_render import render_template
from .services.automation_engine import evaluate_trigger, execute_action


class IsSAorPP(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(user.profile, "role", None)
        return role in ["SuperAdmin", "PiloteProcessus"]


class TemplatesListCreateView(generics.ListCreateAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsSAorPP]


class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsSAorPP]


class TemplatePreviewView(generics.GenericAPIView):
    serializer_class = TemplateSerializer
    permission_classes = [IsSAorPP]

    def post(self, request, pk):
        template = Template.objects.get(pk=pk)
        rendered = render_template(template, request.data.get("context", {}))
        return Response(rendered)


class AutomationsListCreateView(generics.ListCreateAPIView):
    queryset = Automation.objects.all()
    serializer_class = AutomationSerializer
    permission_classes = [IsSAorPP]


class AutomationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Automation.objects.all()
    serializer_class = AutomationSerializer
    permission_classes = [IsSAorPP]


class AutomationRunNowView(generics.GenericAPIView):
    permission_classes = [IsSAorPP]

    def post(self, request, pk):
        automation = Automation.objects.get(pk=pk)
        payload = evaluate_trigger(automation)
        result = execute_action(automation, payload)
        return Response(result)


class MenuItemsListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsSAorPP]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsSAorPP]


class EffectiveMenuView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = getattr(request.user.profile, "role", None)
        items = MenuItem.objects.filter(active=True).order_by("order")
        if role:
            items = [
                {
                    "label": i.label,
                    "path": i.path,
                    "icon": i.icon,
                    "key": i.key,
                }
                for i in items
                if role in (i.visible_for_roles or [])
            ]
        return Response({"items": items})
