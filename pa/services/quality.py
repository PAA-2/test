import os
from datetime import date
from collections import defaultdict

from django.db.models import Count, Q
from django.utils import timezone

from ..models import Action, Plan, DataQualityRule, DataQualityIssue, Profile
from ..exporters import build_actions_queryset


def _allowed_plans(user):
    role = user.profile.role
    if role in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
        return Plan.objects.all()
    return Plan.objects.filter(id__in=user.profile.plans_autorises.all())


# Rule implementations returning list of issue dictionaries

def _rule_missing_required(qs, rule):
    issues = []
    for action in qs.filter(Q(titre="") | Q(priorite="") | Q(delais__isnull=True)):
        issues.append(
            {
                "rule_key": rule.key,
                "severity": rule.severity,
                "entity_type": "action",
                "action": action,
                "plan": action.plan,
                "message": "Missing required fields",
                "details": {},
            }
        )
    return issues


def _rule_invalid_dates(qs, rule):
    issues = []
    for action in qs.filter(
        (Q(delais__lt=Q(date_creation)) & Q(delais__isnull=False) & Q(date_creation__isnull=False))
        | (
            Q(date_realisation__lt=Q(date_creation))
            & Q(date_realisation__isnull=False)
            & Q(date_creation__isnull=False)
        )
    ):
        issues.append(
            {
                "rule_key": rule.key,
                "severity": rule.severity,
                "entity_type": "action",
                "action": action,
                "plan": action.plan,
                "message": "Invalid dates",
                "details": {},
            }
        )
    return issues


def _rule_deadline_mismatch(qs, rule):
    issues = []
    today = date.today()
    for action in qs.filter(delais__isnull=False, j__isnull=False):
        diff = (action.delais - today).days
        if abs(diff - action.j) > 1:
            issues.append(
                {
                    "rule_key": rule.key,
                    "severity": rule.severity,
                    "entity_type": "action",
                    "action": action,
                    "plan": action.plan,
                    "message": "Deadline mismatch with J",
                    "details": {"expected": diff, "found": action.j},
                }
            )
    return issues


def _rule_actid_duplicate(qs, rule):
    issues = []
    dup_ids = (
        qs.values("act_id").annotate(c=Count("id")).filter(c__gt=1).values_list("act_id", flat=True)
    )
    for action in qs.filter(act_id__in=list(dup_ids)):
        issues.append(
            {
                "rule_key": rule.key,
                "severity": rule.severity,
                "entity_type": "action",
                "action": action,
                "plan": action.plan,
                "message": "Duplicate ACT-ID",
                "details": {},
            }
        )
    return issues


def _rule_orphan_row_index(qs, rule):
    issues = []
    for action in qs.filter(Q(excel_row_index__isnull=True) | Q(excel_row_index=0)):
        issues.append(
            {
                "rule_key": rule.key,
                "severity": rule.severity,
                "entity_type": "action",
                "action": action,
                "plan": action.plan,
                "message": "Orphan row index",
                "details": {},
            }
        )
    return issues


def _rule_pdca_inconsistent(qs, rule):
    issues = []
    for action in qs:
        if action.statut == "Cloturee" and (not action.c or not action.a):
            issues.append(
                {
                    "rule_key": rule.key,
                    "severity": rule.severity,
                    "entity_type": "action",
                    "action": action,
                    "plan": action.plan,
                    "message": "Cloturee sans C/A",
                    "details": {},
                }
            )
        elif action.statut != "Cloturee" and (action.c or action.a):
            issues.append(
                {
                    "rule_key": rule.key,
                    "severity": rule.severity,
                    "entity_type": "action",
                    "action": action,
                    "plan": action.plan,
                    "message": "C/A cochés mais statut non clôturé",
                    "details": {},
                }
            )
    return issues


def _rule_responsables_malformed(qs, rule):
    issues = []
    for action in qs.annotate(cnt=Count("responsables")).filter(cnt=0):
        issues.append(
            {
                "rule_key": rule.key,
                "severity": rule.severity,
                "entity_type": "action",
                "action": action,
                "plan": action.plan,
                "message": "Responsables manquants",
                "details": {},
            }
        )
    return issues


def _rule_excel_path_unreachable(plans, rule):
    issues = []
    for plan in plans:
        if not os.path.exists(plan.excel_path):
            issues.append(
                {
                    "rule_key": rule.key,
                    "severity": rule.severity,
                    "entity_type": "plan",
                    "plan": plan,
                    "message": "Excel path unreachable",
                    "details": {"path": plan.excel_path},
                }
            )
    return issues


RULE_FUNCS = {
    "missing_required": _rule_missing_required,
    "invalid_dates": _rule_invalid_dates,
    "deadline_mismatch_J": _rule_deadline_mismatch,
    "actid_duplicate": _rule_actid_duplicate,
    "orphan_row_index": _rule_orphan_row_index,
    "pdca_inconsistent": _rule_pdca_inconsistent,
    "responsables_malformed": _rule_responsables_malformed,
    "excel_path_unreachable": _rule_excel_path_unreachable,
}


def run_quality_checks(user, filters=None, only_rules=None, persist=True):
    filters = filters or {}
    rules_qs = DataQualityRule.objects.filter(enabled=True)
    if only_rules:
        rules_qs = rules_qs.filter(key__in=only_rules)
    rules = list(rules_qs)
    actions_qs = build_actions_queryset(user, filters)
    plans_qs = _allowed_plans(user)

    issues = []
    stats_by_sev = defaultdict(int)
    stats_by_rule = defaultdict(int)

    for rule in rules:
        func = RULE_FUNCS.get(rule.key)
        if not func:
            continue
        if rule.scope == DataQualityRule.Scope.PLAN:
            new_issues = func(plans_qs, rule)
        else:
            new_issues = func(actions_qs, rule)
        for issue in new_issues:
            stats_by_sev[issue["severity"]] += 1
            stats_by_rule[rule.key] += 1
        issues.extend(new_issues)

    if persist:
        for issue in issues:
            DataQualityIssue.objects.update_or_create(
                rule_key=issue["rule_key"],
                entity_type=issue["entity_type"],
                action=issue.get("action"),
                plan=issue.get("plan"),
                message=issue["message"],
                defaults={
                    "severity": issue["severity"],
                    "details": issue.get("details", {}),
                },
            )

    return {
        "total": len(issues),
        "by_severity": stats_by_sev,
        "by_rule": stats_by_rule,
    }


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
