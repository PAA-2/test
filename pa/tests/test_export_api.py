from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from openpyxl import load_workbook
from unittest.mock import patch

from pa.models import Plan, Action, Profile


class ExportAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user("user", password="pass")
        self.profile = Profile.objects.create(user=self.user, role=Profile.Role.PILOTE)
        self.plan1 = Plan.objects.create(
            nom="Plan1",
            excel_path="/tmp/plan1.xlsx",
            excel_sheet="plan d’action",
            header_row_index=11,
        )
        self.plan2 = Plan.objects.create(
            nom="Plan2",
            excel_path="/tmp/plan2.xlsx",
            excel_sheet="plan d’action",
            header_row_index=11,
        )
        self.profile.plans_autorises.add(self.plan1)
        self.action1 = Action.objects.create(
            act_id="ACT-0001",
            titre="Action1",
            statut="open",
            priorite="high",
            plan=self.plan1,
            excel_fichier=self.plan1.excel_path,
            excel_feuille="plan d’action",
            excel_row_index=12,
        )
        self.action2 = Action.objects.create(
            act_id="ACT-0002",
            titre="Action2",
            statut="open",
            priorite="low",
            plan=self.plan2,
            excel_fichier=self.plan2.excel_path,
            excel_feuille="plan d’action",
            excel_row_index=12,
        )
        self.client.force_authenticate(self.user)

    def test_excel_export_respects_roles_and_filters(self):
        resp = self.client.get(f"/api/export/excel?plan={self.plan1.id}&priorite=high")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        wb = load_workbook(BytesIO(resp.content))
        ws = wb.active
        # header
        self.assertEqual(ws.cell(1, 1).value, "ACT-ID")
        # only action1 present
        self.assertEqual(ws.cell(2, 1).value, "ACT-0001")
        self.assertIsNone(ws.cell(3, 1).value)

        # unauthorized plan should yield no rows
        resp2 = self.client.get(f"/api/export/excel?plan={self.plan2.id}")
        wb2 = load_workbook(BytesIO(resp2.content))
        ws2 = wb2.active
        self.assertIsNone(ws2.cell(2, 1).value)

    def test_pdf_export_respects_roles_and_filters(self):
        resp = self.client.get(f"/api/export/pdf?q=Action1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        # first bytes of PDF start with %PDF
        self.assertTrue(resp.content.startswith(b"%PDF"))

    def test_excel_export_large_queryset_chunks(self):
        qs = Action.objects.filter(id=self.action1.id)
        with patch.object(qs, "count", return_value=50001):
            from pa.exporters import export_actions_excel

            buf = export_actions_excel(qs, {})
            wb = load_workbook(buf)
            ws = wb.active
            self.assertEqual(ws.cell(2, 1).value, "ACT-0001")

