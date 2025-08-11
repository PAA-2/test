from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from pa.models import Plan, Action, Profile


class AssistantAPITests(TestCase):
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

        a1 = Action.objects.create(
            act_id="ACT-0001",
            titre="A1",
            statut="En cours",
            priorite="High",
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=-5,
            p=True,
            d=True,
            date_creation=date.today(),
        )
        a1.responsables.add(self.sa)
        a2 = Action.objects.create(
            act_id="ACT-0002",
            titre="A2",
            statut="En traitement",
            priorite="Med",
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=2,
            j=2,
            p=True,
            d=True,
            date_creation=date.today(),
        )
        a2.responsables.add(self.pilot)
        a3 = Action.objects.create(
            act_id="ACT-0003",
            titre="A3",
            statut="En cours",
            priorite="Low",
            plan=self.plan2,
            excel_fichier="p2.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=1,
            p=True,
            d=True,
            date_creation=date.today(),
        )
        a3.responsables.add(self.pilot)
        a4 = Action.objects.create(
            act_id="ACT-0004",
            titre="A4",
            statut="En cours",
            priorite="Low",
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=3,
            j=10,
            date_creation=date.today(),
        )
        a5 = Action.objects.create(
            act_id="ACT-0005",
            titre="A5",
            statut="En cours",
            priorite="High",
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=4,
            j=1,
            p=True,
            d=True,
            date_realisation=date.today(),
            date_creation=date.today(),
        )
        a5.responsables.add(self.sa)

    def test_suggest_closures_respects_roles_and_limits(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.post("/api/assistant/suggest-closures", {"limit": 2})
        self.assertEqual(len(resp.data), 2)
        ids = {a["act_id"] for a in resp.data}
        self.assertIn("ACT-0005", ids)
        self.client.force_authenticate(self.pilot)
        resp = self.client.post("/api/assistant/suggest-closures", {"limit": 1})
        self.assertEqual(len(resp.data), 1)
        self.assertIn(resp.data[0]["act_id"], {"ACT-0002", "ACT-0005"})

    def test_prioritize_returns_scored_actions(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.post("/api/assistant/prioritize", {})
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 5)
        first = resp.data[0]
        self.assertEqual(first["act_id"], "ACT-0001")
        self.assertIn("delay", first)
        self.assertIn("priority", first)
        self.assertIn("status", first)
        self.assertIn("pdca", first)

    def test_summarize_counts_and_top_responsables(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.post("/api/assistant/summarize", {})
        self.assertEqual(resp.data["total"], 5)
        self.assertEqual(resp.data["en_retard"], 1)
        self.assertEqual(resp.data["a_cloturer"], 3)
        top = {r["name"]: r for r in resp.data["top_responsables"]}
        self.assertEqual(top["sa"]["count"], 2)
        self.assertEqual(top["sa"]["retard"], 1)
        self.assertEqual(top["pilot"]["count"], 2)
        self.assertEqual(top["pilot"]["retard"], 0)

