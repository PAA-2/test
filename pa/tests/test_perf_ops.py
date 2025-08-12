from datetime import date
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from rest_framework.throttling import AnonRateThrottle

from pa.models import Plan, Action, Profile


class PerfOpsTests(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.client = APIClient()
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.plan = Plan.objects.create(
            nom="Plan1",
            excel_path="p1.xlsx",
            excel_sheet="plan d’action",
            header_row_index=11,
        )
        for i in range(1, 130):
            a = Action.objects.create(
                act_id=f"ACT-{i:04d}",
                titre=f"A{i}",
                statut="En cours",
                priorite="High",
                plan=self.plan,
                excel_fichier="p1.xlsx",
                excel_feuille="plan d’action",
                excel_row_index=i,
                date_creation=date.today(),
            )
            a.responsables.add(self.sa)

    def auth(self):
        self.client.force_authenticate(self.sa)

    def test_no_n_plus_one(self):
        self.auth()
        with CaptureQueriesContext(connection) as ctx:
            self.client.get("/api/actions/")
        self.assertLessEqual(len(ctx), 20)
        act_id = Action.objects.first().act_id
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(f"/api/actions/{act_id}/")
        self.assertLessEqual(len(ctx), 5)

    def test_pagination_and_ordering(self):
        self.auth()
        resp = self.client.get("/api/actions/", {"ordering": "bad"})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get("/api/actions/", {"page_size": 500})
        self.assertEqual(len(resp.data["results"]), 100)

    def test_cache(self):
        self.auth()
        self.client.get("/api/dashboard/counters")
        with CaptureQueriesContext(connection) as ctx:
            self.client.get("/api/dashboard/counters")
        self.assertEqual(len(ctx), 0)

    def test_throttle(self):
        from pa.views_ops import HealthView

        class OnePerMinThrottle(AnonRateThrottle):
            rate = "1/min"

        HealthView.throttle_classes = [OnePerMinThrottle]
        self.client.get("/api/health")
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 429)
        HealthView.throttle_classes = []

    def test_health_and_logging(self):
        with self.assertLogs(level="INFO") as logs:
            resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("request_id", logs.output[0])
