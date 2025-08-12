from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from pa.models import Plan, Action, Profile, CustomField, CustomFieldOption


class CustomFieldsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        self.sa_profile = Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.pilote = User.objects.create_user("pilote", password="pass")
        self.pilote_profile = Profile.objects.create(user=self.pilote, role=Profile.Role.PILOTE)
        self.plan = Plan.objects.create(
            nom="Plan1", excel_path="/tmp/p.xlsx", excel_sheet="plan d’action", header_row_index=11
        )
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "plan d’action"
        ws.append(["act_id"])
        wb.save(self.plan.excel_path)
        self.pilote_profile.plans_autorises.add(self.plan)
        self.action = Action.objects.create(
            act_id="ACT-0001",
            titre="Action",
            statut="open",
            priorite="high",
            plan=self.plan,
            excel_fichier="/tmp/p.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
        )

    def test_custom_field_crud_permissions(self):
        url = "/api/admin/custom-fields/"
        self.client.force_authenticate(self.pilote)
        resp = self.client.post(url, {"name": "X", "key": "x", "type": "text"}, format="json")
        self.assertEqual(resp.status_code, 403)
        self.client.force_authenticate(self.sa)
        resp = self.client.post(url, {"name": "X", "key": "x", "type": "text"}, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_action_custom_field_validation(self):
        self.client.force_authenticate(self.sa)
        field = CustomField.objects.create(name="Criticite", key="criticite", type="select", required=True)
        CustomFieldOption.objects.create(field=field, value="H", label="High")
        field2 = CustomField.objects.create(
            name="Cause", key="cause", type="text", regex=r"^[A-Z]+$"
        )
        url = "/api/actions/"
        payload = {
            "titre": "T1",
            "statut": "open",
            "priorite": "high",
            "plan": self.plan.id,
            "excel_fichier": "/tmp/p.xlsx",
            "excel_feuille": "plan d’action",
            "excel_row_index": 1,
            "responsables": [],
            "custom": {"cause": "abc"},
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 400)
        payload["custom"] = {"criticite": "X", "cause": "ABC"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 400)
        payload["custom"] = {"criticite": "H", "cause": "ABC"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_custom_field_visibility_by_role(self):
        cf = CustomField.objects.create(
            name="Secret", key="secret", type="text", role_visibility="SA_PP"
        )
        self.action.custom = {"secret": "VAL"}
        self.action.save()
        self.client.force_authenticate(self.pilote)
        url = f"/api/actions/{self.action.act_id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("secret", resp.data.get("custom", {}))
