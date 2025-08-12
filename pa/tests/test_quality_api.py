from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta

from pa.models import Plan, Action, Profile, DataQualityRule, DataQualityIssue


class QualityAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        self.sa = User.objects.create_user("sa", password="pass")
        Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.pilot_user = User.objects.create_user("pilot", password="pass")
        pilot_profile = Profile.objects.create(user=self.pilot_user, role=Profile.Role.PILOTE)
        self.plan1 = Plan.objects.create(nom="Plan1", excel_path="/tmp/missing.xlsx", excel_sheet="plan", header_row_index=11)
        self.plan2 = Plan.objects.create(nom="Plan2", excel_path="/tmp/plan2.xlsx", excel_sheet="plan", header_row_index=11)
        pilot_profile.plans_autorises.add(self.plan1)
        Action.objects.create(
            act_id="ACT-0001",
            titre="A1",
            statut="En cours",
            priorite="High",
            plan=self.plan1,
            excel_fichier=self.plan1.excel_path,
            excel_feuille="plan",
            excel_row_index=0,
            delais=date.today() + timedelta(days=5),
            j=3,
        )
        Action.objects.create(
            act_id="ACT-0002",
            titre="A2",
            statut="En cours",
            priorite="High",
            plan=self.plan2,
            excel_fichier=self.plan2.excel_path,
            excel_feuille="plan",
            excel_row_index=5,
            delais=date.today() + timedelta(days=1),
            j=10,
        )
        DataQualityRule.objects.create(key="orphan_row_index", name="orphan", severity="MED", scope="action")
        DataQualityRule.objects.create(key="deadline_mismatch_J", name="J", severity="MED", scope="action")
        DataQualityRule.objects.create(key="excel_path_unreachable", name="path", severity="HIGH", scope="plan")

    def test_run_quality_creates_issues_and_stats(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.post("/api/quality/run", {"filters": {}}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data["stats"]["total"], 3)
        self.assertEqual(DataQualityIssue.objects.count(), resp.data["stats"]["total"])

    def test_filters_and_roles_limit_scope(self):
        self.client.force_authenticate(self.sa)
        self.client.post("/api/quality/run", {"filters": {}}, format="json")
        self.client.force_authenticate(self.pilot_user)
        resp = self.client.get("/api/quality/issues")
        for issue in resp.data:
            if issue["plan"]:
                self.assertEqual(issue["plan"], self.plan1.id)

    def test_resolve_and_ignore_issue_transitions(self):
        self.client.force_authenticate(self.sa)
        self.client.post("/api/quality/run", {"filters": {}}, format="json")
        issue = DataQualityIssue.objects.first()
        resp = self.client.post(f"/api/quality/issues/{issue.id}/resolve")
        self.assertEqual(resp.status_code, 200)
        issue.refresh_from_db()
        self.assertEqual(issue.status, DataQualityIssue.Status.RESOLVED)
        resp = self.client.post(f"/api/quality/issues/{issue.id}/ignore")
        self.assertEqual(resp.status_code, 200)
        issue.refresh_from_db()
        self.assertEqual(issue.status, DataQualityIssue.Status.IGNORED)

    def test_rules_crud_requires_sa_pp(self):
        self.client.force_authenticate(self.pilot_user)
        resp = self.client.post(
            "/api/quality/rules",
            {"key": "r1", "name": "R1", "severity": "LOW", "scope": "action"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)
        self.client.force_authenticate(self.sa)
        resp = self.client.post(
            "/api/quality/rules",
            {"key": "r1", "name": "R1", "severity": "LOW", "scope": "action"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
