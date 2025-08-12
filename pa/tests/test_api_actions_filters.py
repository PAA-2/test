from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta

from pa.models import Plan, Action, Profile


class ActionFilterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user('sa', password='pass')
        Profile.objects.create(user=self.user, role=Profile.Role.SUPER_ADMIN)
        self.plan1 = Plan.objects.create(
            nom='Plan1', excel_path='/tmp/p1.xlsx', excel_sheet='plan d’action', header_row_index=11
        )
        self.plan2 = Plan.objects.create(
            nom='Plan2', excel_path='/tmp/p2.xlsx', excel_sheet='plan d’action', header_row_index=11
        )
        today = date.today()
        Action.objects.create(
            act_id='ACT-0001', titre='foo', statut='open', priorite='High',
            delais=today + timedelta(days=5), j=5, plan=self.plan1,
            excel_fichier=self.plan1.excel_path, excel_feuille='plan d’action', excel_row_index=12
        )
        Action.objects.create(
            act_id='ACT-0002', titre='bar', statut='open', priorite='Low',
            delais=today - timedelta(days=5), j=-5, plan=self.plan2,
            excel_fichier=self.plan2.excel_path, excel_feuille='plan d’action', excel_row_index=12
        )
        self.client.force_authenticate(self.user)

    def test_actions_filter_by_plan_priority_q(self):
        resp = self.client.get('/api/actions/', {'plan': self.plan1.id, 'priorite': 'High', 'q': 'foo'})
        assert resp.status_code == 200
        assert resp.data['count'] == 1

    def test_actions_ordering_delais(self):
        resp = self.client.get('/api/actions/', {'ordering': '-delais'})
        assert resp.status_code == 200
        dates = [item['delais'] for item in resp.data['results']]
        assert dates == sorted(dates, reverse=True)

    def test_permissions_role_pilote_scope(self):
        User = get_user_model()
        pilote = User.objects.create_user('pilote', password='pass')
        profile = Profile.objects.create(user=pilote, role=Profile.Role.PILOTE)
        profile.plans_autorises.set([self.plan1])
        client = APIClient()
        client.force_authenticate(pilote)
        resp = client.get('/api/actions/')
        assert resp.data['count'] == 2
