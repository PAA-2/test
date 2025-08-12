from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date

from pa.models import Plan, Action, Profile, AssistantWeights, Automation


class AssistantV2APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        self.sa_profile = Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.client.force_authenticate(self.sa)
        self.plan = Plan.objects.create(nom="P1", excel_path="p1.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.action = Action.objects.create(
            act_id="ACT-1000",
            titre="A",
            statut="En cours",
            priorite="High",
            plan=self.plan,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=-1,
            p=True,
            d=True,
            date_creation=date.today(),
        )

    def test_put_scores_limits(self):
        r = self.client.put("/api/assistant/scores", {"weights": {"delay": 3, "priority": 1, "status": 1, "pdca": 1}}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(AssistantWeights.objects.get(id=1).delay, 3)

    def test_explain_returns_breakdown(self):
        r = self.client.post("/api/assistant/explain", {"act_ids": ["ACT-1000"]}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data[0]["act_id"], "ACT-1000")
        self.assertIn("breakdown", r.data[0])

    def test_batch_validate_dry_run(self):
        r = self.client.post("/api/assistant/batch-validate", {"act_ids": ["ACT-1000"], "dry_run": True}, format="json")
        self.assertEqual(r.status_code, 200)
        self.action.refresh_from_db()
        self.assertFalse(self.action.c)

    def test_schedule_reminders_creates_automation(self):
        r = self.client.post("/api/assistant/schedule-reminders", {"plan": self.plan.id, "to": ["x@y"]}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Automation.objects.filter(id=r.data["id"]).exists())
