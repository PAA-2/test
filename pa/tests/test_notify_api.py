from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient

from pa.models import Plan, Action, Profile, NotificationTemplate


class NotifyAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        self.sa_profile = Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.pilot = User.objects.create_user("pilot", password="pass")
        self.pilot_profile = Profile.objects.create(user=self.pilot, role=Profile.Role.PILOTE)
        self.plan1 = Plan.objects.create(nom="Plan1", excel_path="p1.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.plan2 = Plan.objects.create(nom="Plan2", excel_path="p2.xlsx", excel_sheet="plan d’action", header_row_index=11)
        self.pilot_profile.plans_autorises.add(self.plan1)
        NotificationTemplate.objects.create(name="def", subject="{{ count }} actions", body_text="body", is_default=True)
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
            plan=self.plan1,
            excel_fichier="p1.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=2,
            j=5,
        )
        Action.objects.create(
            act_id="ACT-0003",
            titre="A3",
            statut="Cloturee",
            priorite="Low",
            plan=self.plan2,
            excel_fichier="p2.xlsx",
            excel_feuille="plan d’action",
            excel_row_index=1,
            j=1,
        )

    @patch("pa.views_notify.win32com", new=object())
    @patch("pa.services.outlook_mail.send_mail")
    @patch("pa.services.outlook_mail.build_mail")
    def test_notify_late_dry_run(self, mock_build, mock_send):
        client = APIClient()
        client.force_authenticate(self.sa)
        resp = client.post(
            "/api/notify/late",
            {"filters": {}, "to": ["x@example.com"], "dry_run": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("preview", resp.data)
        self.assertEqual(resp.data["count"], 1)
        mock_send.assert_not_called()

    @patch("pa.views_notify.win32com", new=object())
    @patch("pa.services.outlook_mail.send_mail")
    @patch("pa.services.outlook_mail.build_mail")
    def test_notify_summary_roles(self, mock_build, mock_send):
        client = APIClient()
        client.force_authenticate(self.sa)
        resp = client.post(
            "/api/notify/summary",
            {"to": ["x@example.com"], "dry_run": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 3)
        client.force_authenticate(self.pilot)
        resp = client.post(
            "/api/notify/summary",
            {"to": ["x@example.com"], "dry_run": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    @patch("pa.views_notify.win32com", new=object())
    @patch("pa.services.outlook_mail.send_mail")
    @patch("pa.services.outlook_mail.build_mail")
    def test_notify_custom_minimal(self, mock_build, mock_send):
        client = APIClient()
        client.force_authenticate(self.sa)
        resp = client.post(
            "/api/notify/custom",
            {
                "to": ["x@example.com"],
                "subject": "Hello",
                "body_text": "Hi",
                "dry_run": True,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("preview", resp.data)
        self.assertEqual(resp.data["preview"]["subject"], "Hello")
