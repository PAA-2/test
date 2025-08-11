from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from pa.models import Plan, Action, Profile


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user("user", password="pass")
        self.profile = Profile.objects.create(user=self.user, role=Profile.Role.SUPER_ADMIN)
        self.plan = Plan.objects.create(
            nom="Plan1", excel_path="/tmp/p.xlsx", excel_sheet="Sheet1", header_row_index=1
        )
        self.action = Action.objects.create(
            act_id="ACT-0001",
            titre="Action1",
            statut="open",
            priorite="high",
            plan=self.plan,
            excel_fichier="p.xlsx",
            excel_feuille="Sheet1",
            excel_row_index=2,
        )

    def test_plan_list(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get("/api/plans/")
        self.assertEqual(resp.status_code, 200)

    def test_action_list(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get("/api/actions/", {"plan": self.plan.id})
        self.assertEqual(resp.status_code, 200)

    def test_action_validate(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(f"/api/actions/{self.action.act_id}/validate/")
        self.assertEqual(resp.status_code, 200)
