from datetime import date
from django.db.models import Q, Count, Value, F, IntegerField, ExpressionWrapper
from django.db.models.functions import Coalesce
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Action, Profile
from .permissions import RolePermission
from .assistant import compute_score, DEFAULT_WEIGHTS


def get_authorized_actions(user, filters):
    qs = Action.objects.all()
    role = user.profile.role
    if role == Profile.Role.PILOTE:
        qs = qs.filter(plan__in=user.profile.plans_autorises.all())
    plan = filters.get("plan")
    responsable = filters.get("responsable")
    priorite = filters.get("priorite")
    q = filters.get("q")
    f_from = filters.get("from")
    f_to = filters.get("to")
    if plan:
        qs = qs.filter(plan_id=plan)
    if responsable:
        qs = qs.filter(responsables__username=responsable)
    if priorite:
        qs = qs.filter(priorite=priorite)
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(commentaire__icontains=q))
    if f_from and f_to:
        qs = qs.filter(date_creation__range=[f_from, f_to])
    return qs.distinct()


def annotate_with_j(qs):
    today = date.today()
    return qs.annotate(
        j_calc=Coalesce("j", ExpressionWrapper(F("delais") - Value(today), output_field=IntegerField()))
    )


class BaseAssistantView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]


class SuggestClosuresView(BaseAssistantView):
    def post(self, request):
        data = request.data
        filters = data.get("filters", {})
        limit = int(data.get("limit", 20))
        qs = annotate_with_j(get_authorized_actions(request.user, filters))
        qs = qs.filter(
            Q(statut__in=["En cours", "En traitement"]) &
            (Q(date_realisation__isnull=False) | (Q(j_calc__gte=0) & Q(p=True, d=True)))
        )
        results = []
        for act in qs:
            score, parts = compute_score(act)
            reasons = []
            if parts["delay"]:
                reasons.append("retard" if (getattr(act, "j", None) or getattr(act, "j_calc", 0)) < 0 else "deadline proche")
            if parts["priority"]:
                reasons.append(f"priorite {act.priorite}")
            if parts["status"]:
                reasons.append(f"statut {act.statut}")
            if parts["pdca"]:
                reasons.append("PDCA incomplet")
            results.append(
                {
                    "act_id": act.act_id,
                    "titre": act.titre,
                    "responsables": ", ".join(act.responsables.values_list("username", flat=True)),
                    "delais": act.delais.isoformat() if act.delais else "",
                    "j": act.j if act.j is not None else act.j_calc,
                    "score": score,
                    "reasons": reasons,
                    "plan": act.plan.nom,
                }
            )
        results.sort(key=lambda x: x["score"], reverse=True)
        return Response(results[:limit])


class PrioritizeView(BaseAssistantView):
    def post(self, request):
        data = request.data
        filters = data.get("filters", {})
        limit = int(data.get("limit", 50))
        qs = annotate_with_j(get_authorized_actions(request.user, filters))
        results = []
        for act in qs:
            score, parts = compute_score(act)
            results.append(
                {
                    "act_id": act.act_id,
                    "titre": act.titre,
                    "responsables": ", ".join(act.responsables.values_list("username", flat=True)),
                    "delais": act.delais.isoformat() if act.delais else "",
                    "j": act.j if act.j is not None else act.j_calc,
                    "score": score,
                    **parts,
                }
            )
        results.sort(key=lambda x: x["score"], reverse=True)
        return Response(results[:limit])


class SummarizeView(BaseAssistantView):
    def post(self, request):
        data = request.data
        filters = data.get("filters", {})
        qs = annotate_with_j(get_authorized_actions(request.user, filters))
        total = qs.count()
        en_retard = qs.filter(j_calc__lt=0).count()
        a_cloturer = qs.filter(
            Q(statut__in=["En cours", "En traitement"]) &
            (Q(date_realisation__isnull=False) | (Q(j_calc__gte=0) & Q(p=True, d=True)))
        ).count()
        par_priorite = {p["priorite"] or "": p["c"] for p in qs.values("priorite").annotate(c=Count("id"))}
        par_statut = {s["statut"] or "": s["c"] for s in qs.values("statut").annotate(c=Count("id"))}
        top_resp_qs = (
            qs.values("responsables__username")
            .annotate(count=Count("id"), retard=Count("id", filter=Q(j_calc__lt=0)))
            .order_by("-count")[:5]
        )
        top_responsables = [
            {"name": r["responsables__username"], "count": r["count"], "retard": r["retard"]}
            for r in top_resp_qs
            if r["responsables__username"]
        ]
        points_cles = [
            f"{en_retard} actions en retard",
            f"{a_cloturer} actions à clôturer",
        ]
        return Response(
            {
                "total": total,
                "en_retard": en_retard,
                "a_cloturer": a_cloturer,
                "par_priorite": par_priorite,
                "par_statut": par_statut,
                "top_responsables": top_responsables,
                "points_cles": points_cles,
            }
        )


class AssistantScoresView(BaseAssistantView):
    def get(self, request):
        return Response({"weights": DEFAULT_WEIGHTS})
