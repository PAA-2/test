from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .permissions import RolePermission
from .models import DataQualityIssue, DataQualityRule, Profile
from .serializers import DataQualityIssueSerializer, DataQualityRuleSerializer
from .services.quality import run_quality_checks, resolve_issue, ignore_issue


class QualityRunView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        filters = request.data.get("filters", {})
        only_rules = request.data.get("only_rules")
        dry_run = request.data.get("dry_run", False)
        stats = run_quality_checks(request.user, filters, only_rules, dry_run=dry_run)
        return Response(stats)


class QualityIssuesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, RolePermission]
    serializer_class = DataQualityIssueSerializer

    def get_queryset(self):
        qs = DataQualityIssue.objects.all().order_by("-detected_at")
        params = self.request.query_params
        status = params.get("status")
        severity = params.get("severity")
        rule_key = params.get("rule_key")
        plan = params.get("plan")
        act_id = params.get("act_id")
        if status:
            qs = qs.filter(status=status)
        if severity:
            qs = qs.filter(severity=severity)
        if rule_key:
            qs = qs.filter(rule_key=rule_key)
        if plan:
            qs = qs.filter(plan_id=plan)
        if act_id:
            qs = qs.filter(act_id=act_id)
        user = self.request.user
        role = user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            allowed = user.profile.plans_autorises.all()
            qs = qs.filter(plan_id__in=allowed)
        return qs


class QualityIssueResolveView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request, pk):
        issue = get_object_or_404(DataQualityIssue, pk=pk)
        self.check_object_permissions(request, issue)
        resolve_issue(issue, request.user)
        return Response({"status": "resolved"})


class QualityIssueIgnoreView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request, pk):
        issue = get_object_or_404(DataQualityIssue, pk=pk)
        self.check_object_permissions(request, issue)
        ignore_issue(issue, request.user)
        return Response({"status": "ignored"})


class QualityRulesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, RolePermission]
    serializer_class = DataQualityRuleSerializer

    def get_queryset(self):
        return DataQualityRule.objects.all()

    def perform_create(self, serializer):
        role = self.request.user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            raise PermissionDenied()
        serializer.save()


class QualityRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, RolePermission]
    serializer_class = DataQualityRuleSerializer
    queryset = DataQualityRule.objects.all()

    def perform_update(self, serializer):
        role = self.request.user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            raise PermissionDenied()
        serializer.save()

    def perform_destroy(self, instance):
        role = self.request.user.profile.role
        if role not in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            raise PermissionDenied()
        instance.delete()
