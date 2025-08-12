import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from pa.models import Plan, Action, Profile
from pa.services.excel_io import resolve_excel_path


class Command(BaseCommand):
    help = "Seed demo users, plans and actions"

    def handle(self, *args, **options):
        User = get_user_model()

        users = {
            "sa": (Profile.Role.SUPER_ADMIN, []),
            "pp": (Profile.Role.PILOTE_PROCESSUS, []),
            "pilote": (Profile.Role.PILOTE, []),
            "user": (Profile.Role.UTILISATEUR, []),
        }
        created_users = {}
        for username, (role, _) in users.items():
            u, _ = User.objects.get_or_create(username=username)
            u.set_password("Pa$$w0rd!")
            u.save()
            profile, _ = Profile.objects.get_or_create(user=u, defaults={"role": role})
            profile.role = role
            profile.save()
            created_users[username] = u

        plan_paths = [
            ("CODIR", "F-ELK-494 Plan HSE.xlsx"),
            ("HSE", "F-ELK-494 Plan Maintenance.xlsx"),
        ]
        plans = []
        for name, path in plan_paths:
            resolved = resolve_excel_path(path)
            plan, _ = Plan.objects.get_or_create(
                nom=name,
                defaults={
                    "excel_path": resolved,
                    "excel_sheet": "plan d’action",
                    "header_row_index": 11,
                },
            )
            plan.excel_path = resolved
            plan.save()
            plans.append(plan)

        # Assign pilote access to first plan
        Profile.objects.filter(user=created_users["pilote"]).first().plans_autorises.set([plans[0]])

        today = datetime.date.today()
        act_counter = 1
        statuses = ["En_cours", "En_traitement", "Cloturee"]
        priorities = ["High", "Med", "Low"]
        resp_sets = [
            [created_users["sa"], created_users["pp"]],
            [created_users["sa"], created_users["pilote"]],
            [created_users["pp"], created_users["pilote"]],
        ]

        for plan in plans:
            for i in range(25):
                act_id = f"ACT-{act_counter:04d}"
                delais = today + datetime.timedelta(days=i - 10)
                j_val = (delais - today).days
                statut = statuses[i % len(statuses)]
                date_realisation = None
                if statut == "Cloturee":
                    date_realisation = today - datetime.timedelta(days=1)
                action = Action.objects.create(
                    act_id=act_id,
                    titre=f"Action {act_counter}",
                    statut=statut,
                    priorite=priorities[i % len(priorities)],
                    budget_dzd=1000 + i,
                    delais=delais,
                    j=j_val,
                    date_creation=today,
                    date_realisation=date_realisation,
                    plan=plan,
                    excel_fichier=plan.excel_path,
                    excel_feuille=plan.excel_sheet,
                    excel_row_index=plan.header_row_index + i + 1,
                    p=True,
                    d=True,
                    c=(i % 2 == 0),
                    a=(i % 3 == 0),
                )
                action.responsables.set(resp_sets[i % len(resp_sets)])
                act_counter += 1

        total_actions = Action.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(users)} users, {len(plans)} plans and {total_actions} actions"
            )
        )
