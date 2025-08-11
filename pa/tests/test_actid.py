from django.test import TestCase

from pa.models import Action, Plan
from pa.services.actid import generate_act_id


class ActIdServiceTests(TestCase):
    def test_generate_first_id(self):
        self.assertEqual(generate_act_id(), "ACT-0001")

    def test_generate_next_id(self):
        plan = Plan.objects.create(
            nom="Plan1",
            excel_path="file.xlsx",
            excel_sheet="Sheet1",
            header_row_index=1,
        )
        Action.objects.create(
            act_id="ACT-0001",
            titre="Test",
            statut="open",
            priorite="high",
            plan=plan,
            excel_fichier="file.xlsx",
            excel_feuille="Sheet1",
            excel_row_index=2,
        )
        self.assertEqual(generate_act_id(), "ACT-0002")
