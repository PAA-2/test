from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from rest_framework.test import APIClient

from pa.models import Plan, Action, Profile, SyncConfig, SyncJob


class SyncAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        self.sa_profile = Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.pilot = User.objects.create_user("pilot", password="pass")
        self.pilot_profile = Profile.objects.create(user=self.pilot, role=Profile.Role.PILOTE)
        self.plan1 = Plan.objects.create(nom="Plan1", excel_path="p1.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.plan2 = Plan.objects.create(nom="Plan2", excel_path="p2.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.pilot_profile.plans_autorises.add(self.plan1)
        self.client = APIClient()
        self.config = SyncConfig.objects.create()

    def test_put_config_requires_role(self):
        self.client.force_authenticate(self.pilot)
        resp = self.client.put("/api/sync/config", {"enabled": False})
        self.assertEqual(resp.status_code, 403)
        self.client.force_authenticate(self.sa)
        resp = self.client.put("/api/sync/config", {"enabled": False})
        self.assertEqual(resp.status_code, 200)

    @patch("pa.services.sync.excel_io.read_plan")
    def test_run_dry_run_returns_stats_without_writes(self, mock_read):
        Action.objects.create(
            act_id="ACT-0001",
            titre="Old",
            statut="En cours",
            priorite="High",
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
        )
        mock_read.return_value = [
            {
                "act_id": "ACT-0001",
                "titre": "New",
                "statut": "En cours",
                "priorite": "High",
                "excel_fichier": "p1.xlsx",
                "excel_feuille": "plan d’action",
                "excel_row_index": 1,
            }
        ]
        self.client.force_authenticate(self.sa)
        resp = self.client.post("/api/sync/run", {"dry_run": True, "plan": self.plan1.id}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Action.objects.get(act_id="ACT-0001").titre, "Old")
        self.assertEqual(resp.json()["stats"]["written"], 1)
        job = SyncJob.objects.first()
        self.assertTrue(job.dry_run)

    @patch("pa.services.sync.excel_io.read_plan")
    def test_run_real_updates_in_batches_and_logs_job(self, mock_read):
        mock_read.return_value = [
            {
                "act_id": "ACT-0002",
                "titre": "A2",
                "statut": "En cours",
                "priorite": "Low",
                "excel_fichier": "p2.xlsx",
                "excel_feuille": "plan d’action",
                "excel_row_index": 1,
            }
        ]
        self.client.force_authenticate(self.sa)
        resp = self.client.post("/api/sync/run", {"plan": self.plan2.id}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Action.objects.filter(act_id="ACT-0002").exists())
        job = SyncJob.objects.first()
        self.assertFalse(job.dry_run)

    @patch("pa.scheduler.scheduler.add_job")
    @patch("pa.scheduler.scheduler.remove_all_jobs")
    def test_scheduler_respects_cron_and_enabled(self, mock_remove, mock_add):
        from pa.scheduler import schedule_from_config

        self.config.enabled = True
        self.config.cron = "*/5 * * * *"
        self.config.save()
        schedule_from_config()
        mock_remove.assert_called()
        mock_add.assert_called()
        mock_remove.reset_mock(); mock_add.reset_mock()
        self.config.enabled = False
        self.config.save()
        schedule_from_config()
        mock_remove.assert_called()
        mock_add.assert_not_called()

    def test_jobs_list_filters_and_roles(self):
        SyncJob.objects.create(plan=self.plan1, status=SyncJob.Status.OK, stats={})
        SyncJob.objects.create(plan=self.plan2, status=SyncJob.Status.FAIL, stats={})
        self.client.force_authenticate(self.sa)
        resp = self.client.get("/api/sync/jobs", {"status": "OK"})
        self.assertEqual(len(resp.json()), 1)
        self.client.force_authenticate(self.pilot)
        resp = self.client.get("/api/sync/jobs")
        self.assertEqual(len(resp.json()), 1)
