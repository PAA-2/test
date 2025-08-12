import os
from datetime import date
from django.db.models import Count
from django.utils import timezone

from ..models import (
    Action,
    Plan,
    Profile,
    DataQualityRule,
    DataQualityIssue,
)
from ..exporters import build_actions_queryset


def _plans_for_user(user):
    role = user.profile.role if user else Profile.Role.SUPER_ADMIN
    qs = Plan.objects.all()
    if role in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
        return qs
    allowed = user.profile.plans_autorises.all()
    return qs.filter(id__in=allowed)


def check_actid_duplicate(actions, plans):
    issues = []
    dupes = actions.values("act_id").annotate(c=Count("id")).filter(c__gt=1)
    for d in dupes:
        acts = actions.filter(act_id=d["act_id"])
        for act in acts:
            issues.append(
                {
                    "entity_type": "action",
                    "act_id": act.act_id,
                    "entity_id": act.id,
                    "plan_id": act.plan_id,
                    "message": "ACT-ID dupliqué",
                    "details": {"count": d["c"]},
                }
            )
    return issues


def check_deadline_mismatch_j(actions, plans):
    issues = []
    today = date.today()
    for act in actions.filter(delais__isnull=False):
        expected = (act.delais - today).days
        if act.j is None or abs(expected - act.j) > 1:
            issues.append(
                {
                    "entity_type": "action",
                    "act_id": act.act_id,
                    "entity_id": act.id,
                    "plan_id": act.plan_id,
                    "message": "J incohérent avec délai",
                    "details": {"expected": expected, "j": act.j},
                }
            )
    return issues


def check_orphan_row_index(actions, plans):
    issues = []
    for act in actions:
        if not act.excel_row_index or not os.path.exists(act.excel_fichier):
            issues.append(
                {
                    "entity_type": "action",
                    "act_id": act.act_id,
                    "entity_id": act.id,
                    "plan_id": act.plan_id,
                    "message": "Ligne Excel introuvable",
                }
            )
    return issues


def check_excel_path_unreachable(actions, plans):
    issues = []
    for plan in plans:
        if not os.path.exists(plan.excel_path):
            issues.append(
                {
                    "entity_type": "plan",
                    "entity_id": plan.id,
                    "plan_id": plan.id,
                    "message": "Chemin Excel introuvable",
                }
            )
    return issues


RULE_FUNCTIONS = {
    "actid_duplicate": check_actid_duplicate,
    "deadline_mismatch_J": check_deadline_mismatch_j,
    "orphan_row_index": check_orphan_row_index,
    "excel_path_unreachable": check_excel_path_unreachable,
}


def run_quality_checks(user, filters=None, only_rules=None, dry_run=False):
    filters = filters or {}
    user_for_qs = user
    if user_for_qs is None:
        class Dummy:
            profile = type(
                "p",
                (),
                {
                    "role": Profile.Role.SUPER_ADMIN,
                    "plans_autorises": Plan.objects.none(),
                },
            )()
        user_for_qs = Dummy()
    actions = build_actions_queryset(user_for_qs, filters)
    plans = _plans_for_user(user_for_qs)
    if filters.get("plan"):
        plans = plans.filter(id=filters.get("plan"))
    active_rules = DataQualityRule.objects.filter(enabled=True)
    if only_rules:
        active_rules = active_rules.filter(key__in=only_rules)
    stats = {
        "total": 0,
        "by_severity": {k: 0 for k in DataQualityIssue.Severity.values},
        "by_rule": {},
    }
    collected = []
    for rule in active_rules:
        func = RULE_FUNCTIONS.get(rule.key)
        if not func:
            continue
        issues = func(actions, plans)
        stats["by_rule"][rule.key] = len(issues)
        stats["total"] += len(issues)
        stats["by_severity"][rule.severity] += len(issues)
        for issue in issues:
            issue["rule_key"] = rule.key
            issue["severity"] = rule.severity
            collected.append(issue)
    if not dry_run:
        now = timezone.now()
        for issue in collected:
            DataQualityIssue.objects.update_or_create(
                rule_key=issue["rule_key"],
                entity_type=issue["entity_type"],
                act_id=issue.get("act_id"),
                entity_id=issue.get("entity_id"),
                message=issue["message"],
                defaults={
                    "severity": issue["severity"],
                    "plan_id": issue.get("plan_id"),
                    "details": issue.get("details", {}),
                    "detected_at": now,
                    "status": DataQualityIssue.Status.OPEN,
                    "resolved_by": None,
                    "resolved_at": None,
                },
            )
    return stats


def resolve_issue(issue, user):
    issue.status = DataQualityIssue.Status.RESOLVED
    issue.resolved_by = user
    issue.resolved_at = timezone.now()
    issue.save(update_fields=["status", "resolved_by", "resolved_at"])


def ignore_issue(issue, user):
    issue.status = DataQualityIssue.Status.IGNORED
    issue.resolved_by = user
    issue.resolved_at = timezone.now()
    issue.save(update_fields=["status", "resolved_by", "resolved_at"])
