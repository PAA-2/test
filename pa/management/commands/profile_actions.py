from django.core.management.base import BaseCommand
from django.db import connection
from pa.models import Action
import time


class Command(BaseCommand):
    help = "Profile Action queries"

    def add_arguments(self, parser):
        parser.add_argument("--plan", type=int, required=True)
        parser.add_argument("--limit", type=int, default=200)

    def handle(self, *args, **options):
        plan = options["plan"]
        limit = options["limit"]
        start = time.perf_counter()
        list(
            Action.objects.filter(plan_id=plan)
            .select_related("plan")
            .prefetch_related("responsables")[:limit]
        )
        duration = time.perf_counter() - start
        queries = len(connection.queries)
        self.stdout.write(
            f"Fetched {limit} actions in {duration:.2f}s using {queries} queries"
        )
