from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from pa.models import Plan, Action, Profile


class StatsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
            j=5,
            date_creation=date.today(),
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
            j=5,
            date_creation=date.today(),
        )
        Action.objects.create(
            act_id="ACT-0003",
            titre="A3",
            statut="Cloturee",
            priorite="High",
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=2,
            j=-1,
            date_creation=date.today() - relativedelta(months=1),
            date_realisation=date.today(),
        )

    def test_counters_filters_and_roles(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.get("/api/dashboard/counters")
        self.assertEqual(resp.data["total"], 3)
        resp = self.client.get("/api/dashboard/counters", {"plan": self.plan1.id})
        self.assertEqual(resp.data["total"], 2)
        self.client.force_authenticate(self.pilot)
        resp = self.client.get("/api/dashboard/counters")
        self.assertEqual(resp.data["total"], 2)
        self.assertEqual(resp.data["en_retard"], 1)

    def test_progress_last_12_months(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.get("/api/charts/progress")
        self.assertEqual(len(resp.data["labels"]), 12)
        self.assertEqual(sum(resp.data["created_per_month"]), 3)
        self.assertEqual(sum(resp.data["closed_per_month"]), 1)

    def test_compare_plans_on_authorized_scope(self):
        plan3 = Plan.objects.create(nom="Plan3", excel_path="p3.xlsx", excel_sheet="plan d’action", header_row_index=11, actif=False)
        Action.objects.create(
            act_id="ACT-0004",
            titre="A4",
            statut="En cours",
            priorite="High",
            plan=plan3,
            excel_fichier="p3.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=5,
            date_creation=date.today(),
        )
        self.client.force_authenticate(self.sa)
        resp = self.client.get("/api/charts/compare-plans")
        plans = {p["plan"] for p in resp.data}
        self.assertNotIn("Plan3", plans)
        resp = self.client.get("/api/charts/compare-plans", {"only_active": "false"})
        plans = {p["plan"] for p in resp.data}
        self.assertIn("Plan3", plans)
        self.client.force_authenticate(self.pilot)
        resp = self.client.get("/api/charts/compare-plans")
        plans = {p["plan"] for p in resp.data}
        self.assertEqual(plans, {"Plan1"})
