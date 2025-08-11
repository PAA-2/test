from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import Action, Plan, Profile


def _actions_for_user(user):
    role = user.profile.role
    qs = Action.objects.all()
    if role in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
        return qs
    allowed = user.profile.plans_autorises.all()
    return qs.filter(plan__in=allowed)


def _filter_actions(qs, params):
    plan = params.get("plan")
    responsable = params.get("responsable")
    priorite = params.get("priorite")
    q = params.get("q")
    if plan:
        qs = qs.filter(plan_id=plan)
    if responsable:
        qs = qs.filter(responsables__username=responsable)
    if priorite:
        qs = qs.filter(priorite=priorite)
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(commentaire__icontains=q))
    return qs


def get_counters(user, params=None):
    params = params or {}
    qs = _actions_for_user(user)
    qs = _filter_actions(qs, params)
    return {
        "total": qs.count(),
        "en_cours": qs.filter(statut="En cours").count(),
        "en_traitement": qs.filter(statut="En traitement").count(),
        "cloturees": qs.filter(statut="Cloturee").count(),
        "archivees": qs.filter(statut="Archivee").count(),
        "en_retard": qs.filter(j__lt=0).count(),
    }


def get_progress(user, start=None, end=None, params=None):
    params = params or {}
    qs = _actions_for_user(user)
    qs = _filter_actions(qs, params)
    today = timezone.now().date()
    if not start or not end:
        end_date = date(today.year, today.month, 1)
        start_date = end_date - relativedelta(months=11)
    else:
        start_date = datetime.strptime(start, "%Y-%m").date()
        end_date = datetime.strptime(end, "%Y-%m").date()
    months = []
    current = start_date
    while current <= end_date:
        months.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)
    created = (
        qs.filter(date_creation__gte=start_date, date_creation__lt=end_date + relativedelta(months=1))
        .annotate(month=TruncMonth("date_creation"))
        .values("month")
        .annotate(count=Count("id"))
    )
    closed = (
        qs.filter(
            statut="Cloturee",
            date_realisation__isnull=False,
            date_realisation__gte=start_date,
            date_realisation__lt=end_date + relativedelta(months=1),
        )
        .annotate(month=TruncMonth("date_realisation"))
        .values("month")
        .annotate(count=Count("id"))
    )
    created_map = {c["month"].strftime("%Y-%m"): c["count"] for c in created}
    closed_map = {c["month"].strftime("%Y-%m"): c["count"] for c in closed}
    return {
        "labels": months,
        "created_per_month": [created_map.get(m, 0) for m in months],
        "closed_per_month": [closed_map.get(m, 0) for m in months],
    }


def compare_plans(user, only_active=True, params=None):
    params = params or {}
    role = user.profile.role
    if role in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
        plans = Plan.objects.all()
    else:
        plans = user.profile.plans_autorises.all()
    if only_active:
        plans = plans.filter(actif=True)
    qs = Action.objects.filter(plan__in=plans)
    qs = _filter_actions(qs, params)
    data = (
        qs.values("plan__nom")
        .annotate(
            total=Count("id"),
            en_retard=Count("id", filter=Q(j__lt=0)),
            cloturees=Count("id", filter=Q(statut="Cloturee")),
        )
        .order_by("plan__nom")
    )
    return [
        {"plan": d["plan__nom"], "total": d["total"], "en_retard": d["en_retard"], "cloturees": d["cloturees"]}
        for d in data
    ]
