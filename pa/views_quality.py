from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import DataQualityIssue, DataQualityRule, Profile
from .serializers import DataQualityRuleSerializer, DataQualityIssueSerializer
from .services.quality import run_quality_checks, resolve_issue, ignore_issue
from .permissions import RolePermission
from .exporters import build_actions_queryset


class QualityRunView(APIView):
    permission_classes = [RolePermission]

    def post(self, request):
        role = request.user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            return Response(status=status.HTTP_403_FORBIDDEN)
        filters = request.data.get("filters", {})
        only_rules = request.data.get("only_rules")
        dry_run = request.data.get("dry_run", False)
        stats = run_quality_checks(request.user, filters, only_rules, persist=not dry_run)
        sample = DataQualityIssue.objects.all()[:5]
        return Response(
            {"stats": stats, "sample": DataQualityIssueSerializer(sample, many=True).data}
        )


class QualityIssuesListView(generics.ListAPIView):
    serializer_class = DataQualityIssueSerializer
    permission_classes = [RolePermission]

    def get_queryset(self):
        qs = DataQualityIssue.objects.all().select_related("action", "plan")
        user = self.request.user
        role = user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            allowed = user.profile.plans_autorises.all()
            qs = qs.filter(plan__in=allowed)
        status_param = self.request.query_params.get("status")
        severity = self.request.query_params.get("severity")
        rule_key = self.request.query_params.get("rule_key")
        plan = self.request.query_params.get("plan")
        act_id = self.request.query_params.get("act_id")
        date_from = self.request.query_params.get("from")
        date_to = self.request.query_params.get("to")
        if status_param:
            qs = qs.filter(status=status_param)
        if severity:
            qs = qs.filter(severity=severity)
        if rule_key:
            qs = qs.filter(rule_key=rule_key)
        if plan:
            qs = qs.filter(plan_id=plan)
        if act_id:
            qs = qs.filter(action__act_id=act_id)
        if date_from:
            qs = qs.filter(detected_at__gte=date_from)
        if date_to:
            qs = qs.filter(detected_at__lte=date_to)
        return qs.order_by("-detected_at")


class QualityIssueResolveView(APIView):
    permission_classes = [RolePermission]

    def post(self, request, pk):
        issue = DataQualityIssue.objects.get(pk=pk)
        self.check_object_permissions(request, issue)
        resolve_issue(issue, request.user)
        return Response({"status": "resolved"})


class QualityIssueIgnoreView(APIView):
    permission_classes = [RolePermission]

    def post(self, request, pk):
        issue = DataQualityIssue.objects.get(pk=pk)
        self.check_object_permissions(request, issue)
        ignore_issue(issue, request.user)
        return Response({"status": "ignored"})


class QualityRulesView(generics.ListCreateAPIView):
    serializer_class = DataQualityRuleSerializer
    permission_classes = [RolePermission]

    def get_queryset(self):
        return DataQualityRule.objects.all()

    def create(self, request, *args, **kwargs):
        role = request.user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class QualityRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DataQualityRuleSerializer
    permission_classes = [RolePermission]
    queryset = DataQualityRule.objects.all()

    def put(self, request, *args, **kwargs):
        role = request.user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        role = request.user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
