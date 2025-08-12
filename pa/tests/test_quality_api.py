from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from pa.models import (
    Plan,
    Action,
    Profile,
    DataQualityRule,
    DataQualityIssue,
)


class QualityAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.pilot = User.objects.create_user("pilot", password="pass")
        pprof = Profile.objects.create(user=self.pilot, role=Profile.Role.PILOTE)
        self.plan1 = Plan.objects.create(nom="Plan1", excel_path="missing1.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.plan2 = Plan.objects.create(nom="Plan2", excel_path="missing2.xlsx", excel_sheet="plan d’action", header_row_index=11)
        pprof.plans_autorises.add(self.plan1)
        # actions
        today = date.today()
        a1 = Action.objects.create(
            act_id="ACT-0001",
            titre="A1",
            statut="En cours",
            priorite="High",
            plan=self.plan1,
            excel_fichier="a1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=5,
            delais=today + timedelta(days=10),
            date_creation=today,
        )
        a2 = Action.objects.create(
            act_id="ACT-0002",
            titre="A2",
            statut="En cours",
            priorite="High",
            plan=self.plan1,
            excel_fichier="a2.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=0,
            j=1,
            delais=today + timedelta(days=1),
            date_creation=today,
        )
        a3 = Action.objects.create(
            act_id="ACT-0003",
            titre="A3",
            statut="En cours",
            priorite="Low",
            plan=self.plan2,
            excel_fichier="a3.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=2,
            j=0,
            delais=today + timedelta(days=5),
            date_creation=today,
        )
        a1.responsables.add(self.sa)
        a2.responsables.add(self.sa)
        a3.responsables.add(self.pilot)
        # rules
        DataQualityRule.objects.create(
            key="actid_duplicate",
            name="Dup",
            severity=DataQualityRule.Severity.HIGH,
            scope=DataQualityRule.Scope.ACTION,
        )
        DataQualityRule.objects.create(
            key="orphan_row_index",
            name="Orphan",
            severity=DataQualityRule.Severity.HIGH,
            scope=DataQualityRule.Scope.ACTION,
        )
        DataQualityRule.objects.create(
            key="deadline_mismatch_J",
            name="J mismatch",
            severity=DataQualityRule.Severity.MED,
            scope=DataQualityRule.Scope.ACTION,
        )
        DataQualityRule.objects.create(
            key="excel_path_unreachable",
            name="Excel path",
            severity=DataQualityRule.Severity.HIGH,
            scope=DataQualityRule.Scope.PLAN,
        )

    def auth(self, user):
        self.client.force_authenticate(user)

    def test_run_quality_creates_issues_and_stats(self):
        self.auth(self.sa)
        resp = self.client.post("/api/quality/run", {}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.data["total"], 0)
        self.assertEqual(DataQualityIssue.objects.count(), resp.data["total"])

    def test_filters_and_roles_limit_scope(self):
        self.auth(self.sa)
        self.client.post("/api/quality/run", {}, format="json")
        self.client.force_authenticate(self.pilot)
        resp = self.client.get("/api/quality/issues")
        self.assertEqual(resp.status_code, 200)
        for issue in (resp.data if isinstance(resp.data, list) else resp.data["results"]):
            if issue.get("plan"):
                self.assertEqual(issue["plan"], self.plan1.id)

    def test_resolve_and_ignore_issue_transitions(self):
        issue = DataQualityIssue.objects.create(
            rule_key="test",
            severity=DataQualityIssue.Severity.LOW,
            entity_type="action",
            act_id="ACT-9999",
            entity_id=1,
            plan=self.plan1,
            message="msg",
        )
        self.auth(self.sa)
        r1 = self.client.post(f"/api/quality/issues/{issue.id}/resolve")
        self.assertEqual(r1.status_code, 200)
        issue.refresh_from_db()
        self.assertEqual(issue.status, DataQualityIssue.Status.RESOLVED)
        r2 = self.client.post(f"/api/quality/issues/{issue.id}/ignore")
        self.assertEqual(r2.status_code, 200)
        issue.refresh_from_db()
        self.assertEqual(issue.status, DataQualityIssue.Status.IGNORED)

    def test_rules_crud_requires_sa_pp(self):
        self.auth(self.pilot)
        resp = self.client.post(
            "/api/quality/rules",
            {"key": "k1", "name": "n1", "severity": "LOW", "scope": "action"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)
        self.auth(self.sa)
        resp = self.client.post(
            "/api/quality/rules",
            {"key": "k1", "name": "n1", "severity": "LOW", "scope": "action"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
