from io import BytesIO
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from PyPDF2 import PdfReader

from pa.models import Plan, Action, Profile


class CustomReportTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        self.sa_profile = Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.pilot = User.objects.create_user("pilot", password="pass")
        self.pilot_profile = Profile.objects.create(user=self.pilot, role=Profile.Role.PILOTE)
        self.plan1 = Plan.objects.create(nom="Plan1", excel_path="p1.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.plan2 = Plan.objects.create(nom="Plan2", excel_path="p2.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.pilot_profile.plans_autorises.add(self.plan1)
        Action.objects.create(
            act_id="ACT-0001",
            titre="A1",
            statut="En cours",
            priorite="High",
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=-5,
        )
        Action.objects.create(
            act_id="ACT-0002",
            titre="A2",
            statut="En cours",
            priorite="Low",
            plan=self.plan2,
            excel_fichier="p2.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=3,
        )

    def test_dry_run_returns_preview_metadata_with_roles(self):
        client = APIClient()
        client.force_authenticate(self.pilot)
        payload = {
            "title": "R",
            "filters": {},
            "layout": {},
            "sections": [{"type": "grouped_table", "group_by": "plan", "columns": ["ACT-ID", "Titre"]}],
            "dry_run": True,
        }
        resp = client.post("/api/reports/custom", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("pages_estimate", data)
        self.assertIn("Plan1", data["groups_preview"])
        self.assertNotIn("Plan2", data["groups_preview"])

    def test_pdf_generation_content_type_and_disposition(self):
        client = APIClient()
        client.force_authenticate(self.sa)
        payload = {
            "title": "R",
            "filters": {},
            "layout": {},
            "sections": [{"type": "summary_kpis"}],
            "dry_run": False,
        }
        resp = client.post("/api/reports/custom", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertIn("report_", resp["Content-Disposition"])
        reader = PdfReader(BytesIO(resp.content))
        self.assertGreater(len(reader.pages), 0)

    def test_grouped_table_respects_filters_and_roles(self):
        client = APIClient()
        client.force_authenticate(self.sa)
        payload = {
            "title": "R",
            "filters": {"plan": self.plan1.id},
            "layout": {},
            "sections": [{"type": "grouped_table", "group_by": "plan", "columns": ["ACT-ID"]}],
            "dry_run": True,
        }
        resp = client.post("/api/reports/custom", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(set(data["groups_preview"].keys()), {"Plan1"})

    def test_charts_sections_build_without_errors(self):
        client = APIClient()
        client.force_authenticate(self.sa)
        payload = {
            "title": "R",
            "filters": {},
            "layout": {},
            "sections": [{"type": "charts", "include": ["progress", "compare_plans"]}],
            "dry_run": False,
        }
        resp = client.post("/api/reports/custom", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
