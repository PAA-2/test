from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from pa.models import Profile, MenuItem, Template, Automation


class AdminParamsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.sa = User.objects.create_user("sa", password="pass")
        Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.user = User.objects.create_user("u", password="pass")
        Profile.objects.create(user=self.user, role=Profile.Role.UTILISATEUR)

    def test_template_crud_and_preview(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.post(
            "/api/admin/templates",
            {
                "name": "t1",
                "kind": "email",
                "subject": "Hello {{ name }}",
                "body_html": "<p>Hi {{ name }}</p>",
            },
        )
        assert resp.status_code == 201
        tid = resp.data["id"]
        resp = self.client.post(
            f"/api/admin/templates/{tid}/preview",
            {"context": {"name": "X"}},
            format="json",
        )
        assert resp.status_code == 200
        assert "Hi X" in resp.data["body_html"]
        # permission check
        self.client.force_authenticate(self.user)
        resp = self.client.get("/api/admin/templates")
        assert resp.status_code == 403

    def test_automation_run(self):
        self.client.force_authenticate(self.sa)
        tmpl = Template.objects.create(name="t", kind="email", subject="s", body_html="b")
        auto = Automation.objects.create(
            name="a1",
            trigger="manual",
            action="notify_email",
            action_params={"template_id": tmpl.id, "to": ["x@y"]},
        )
        resp = self.client.post(f"/api/admin/automations/{auto.id}/run")
        assert resp.status_code == 200
        assert resp.data["status"] in {"OK", "FAIL", "SKIP"}

    def test_menu_effective(self):
        self.client.force_authenticate(self.sa)
        MenuItem.objects.create(key="dash", label="Dash", path="/", visible_for_roles=["SuperAdmin"]) 
        resp = self.client.get("/api/menu")
        assert resp.status_code == 200
        assert resp.data["items"]
        self.client.force_authenticate(self.user)
        resp = self.client.get("/api/menu")
        assert resp.status_code == 200

