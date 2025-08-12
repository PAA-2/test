from __future__ import annotations

from collections import defaultdict
from typing import Optional

from django.db import transaction

from ..models import Action, Plan, SyncConfig
from . import excel_io


class SyncError(Exception):
    """Base sync error."""


def plan_sync(config: SyncConfig, dry_run: bool = False, plan_id: Optional[int] = None):
    """Synchronise les actions depuis Excel vers la base."""

    stats = defaultdict(int)
    plans = Plan.objects.all()
    if plan_id:
        plans = plans.filter(id=plan_id)
    elif config.strategy == SyncConfig.Strategy.ACTIVE:
        plans = plans.filter(actif=True)

    for plan in plans:
        rows = excel_io.read_plan(plan)
        stats["read"] += len(rows)
        for row in rows:
            act_id = row.get("act_id")
            if not act_id:
                stats["ignored"] += 1
                continue
            defaults = {k: v for k, v in row.items() if k != "act_id"}
            if dry_run:
                action = Action.objects.filter(act_id=act_id).first()
                if action is None:
                    stats["written"] += 1
                else:
                    changed = any(getattr(action, k) != v for k, v in defaults.items())
                    stats["written"] += int(changed)
                continue

            with transaction.atomic():
                Action.objects.update_or_create(
                    act_id=act_id,
                    defaults={**defaults, "plan": plan},
                )
                stats["written"] += 1

    return dict(stats)
