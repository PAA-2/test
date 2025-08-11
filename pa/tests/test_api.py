from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from openpyxl import Workbook

from pa.models import Plan, Action, Profile


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user("user", password="pass")
        self.profile = Profile.objects.create(user=self.user, role=Profile.Role.SUPER_ADMIN)
        self.plan = Plan.objects.create(
            nom="Plan1",
            excel_path="/tmp/plan.xlsx",
            excel_sheet="plan d’action",
            header_row_index=11,
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "plan d’action"
        for _ in range(10):
            ws.append([])
        ws.append(["act_id", "titre", "statut", "priorite"])
        ws.append(["ACT-0001", "Action1", "open", "high"])
        wb.save(self.plan.excel_path)

        self.action = Action.objects.create(
            act_id="ACT-0001",
            titre="Action1",
            statut="open",
            priorite="high",
            plan=self.plan,
            excel_fichier=self.plan.excel_path,
            excel_feuille="plan d’action",
            excel_row_index=12,
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

    def test_excel_preview(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get(f"/api/excel/preview?plan={self.plan.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("rows", resp.data)

    def test_excel_refresh(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post("/api/excel/refresh", {"plan": self.plan.id}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("rows", resp.data)
