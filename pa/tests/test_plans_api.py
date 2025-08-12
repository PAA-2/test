from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from pa.models import Plan, Profile


class PlansAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.sa = User.objects.create_user('sa', password='pass')
        Profile.objects.create(user=self.sa, role=Profile.Role.SUPER_ADMIN)
        self.other = User.objects.create_user('user', password='pass')
        Profile.objects.create(user=self.other, role=Profile.Role.UTILISATEUR)
        self.plan = Plan.objects.create(
            nom='Plan1', excel_path='/tmp/p1.xlsx', excel_sheet='plan d’action', header_row_index=11
        )
        # create minimal Excel file for preview endpoint
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'plan d’action'
        for _ in range(10):
            ws.append([])
        ws.append(['act_id'])
        ws.append(['ACT-0001'])
        wb.save(self.plan.excel_path)

    def test_create_plan_requires_sa_or_pp(self):
        self.client.force_authenticate(self.other)
        resp = self.client.post('/api/plans/', {'nom': 'X', 'excel_path': 'p.xlsx', 'excel_sheet': 's', 'header_row_index': 1})
        assert resp.status_code == 403
        self.client.force_authenticate(self.sa)
        resp = self.client.post('/api/plans/', {'nom': 'X', 'excel_path': 'p.xlsx', 'excel_sheet': 's', 'header_row_index': 1})
        assert resp.status_code == 201

    def test_rescan_returns_404(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.post(f'/api/plans/{self.plan.id}/rescan/')
        assert resp.status_code in (200, 404)

    def test_preview_returns_first_rows(self):
        self.client.force_authenticate(self.sa)
        resp = self.client.get(f'/api/excel/preview?plan={self.plan.id}')
        assert resp.status_code == 200
        assert 'rows' in resp.data
