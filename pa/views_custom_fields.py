from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomField, Profile
from .serializers import CustomFieldSerializer


class CustomFieldAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        role = getattr(request.user.profile, "role", None)
        return role in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS)


class CustomFieldViewSet(viewsets.ModelViewSet):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    permission_classes = [CustomFieldAdminPermission]


class CustomFieldSchemaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fields = []
        for cf in CustomField.objects.filter(active=True).prefetch_related("options"):
            item = {
                "key": cf.key,
                "label": cf.name,
                "type": cf.type,
                "required": cf.required,
                "help": cf.help_text,
                "visibleFor": [cf.role_visibility],
            }
            if cf.type in (CustomField.Type.SELECT, CustomField.Type.TAGS):
                item["options"] = [
                    {"value": o.value, "label": o.label} for o in cf.options.all()
                ]
            fields.append(item)
        return Response({"fields": fields})
