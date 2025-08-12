from django.db import transaction
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .assistant import compute_score, get_weights, update_weights
from .models import Action, Profile, Automation
from .permissions import RolePermission
from .views_assistant import get_authorized_actions, annotate_with_j
from .services.excel_io import apply_update


class AssistantScoresView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        return Response({"weights": get_weights()})

    def put(self, request):
        role = request.user.profile.role
        if role not in [Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS]:
            return Response(status=403)
        data = request.data.get("weights", {})
        for v in data.values():
            if not isinstance(v, int) or v < 0 or v > 5:
                return Response({"error": "invalid"}, status=400)
        if sum(data.values()) <= 0:
            return Response({"error": "invalid"}, status=400)
        return Response({"weights": update_weights(data)})


class ExplainView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        act_ids = request.data.get("act_ids", [])
        filters = request.data.get("filters", {})
        qs = annotate_with_j(get_authorized_actions(request.user, filters))
        qs = qs.filter(act_id__in=act_ids)
        weights = get_weights()
        results = []
        for act in qs:
            score, parts = compute_score(act, weights)
            reasons = []
            if parts["delay"]:
                reasons.append("delay")
            if parts["priority"]:
                reasons.append("priority")
            if parts["status"]:
                reasons.append("status")
            if parts["pdca"]:
                reasons.append("pdca")
            results.append(
                {
                    "act_id": act.act_id,
                    "score": score,
                    "breakdown": parts,
                    "reasons": reasons,
                }
            )
        return Response(results)


class _BatchBase(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    action_type = ""

    def handle_action(self, action_obj, pdca, comment):
        if self.action_type == "validate":
            if pdca.get("C", True):
                action_obj.c = True
        elif self.action_type == "close":
            if pdca.get("A", True):
                action_obj.a = True
                action_obj.statut = "Cloturee"
        elif self.action_type == "reject":
            action_obj.statut = "rejected"
        if comment:
            action_obj.commentaire = (action_obj.commentaire or "") + f"\n{comment}"
        action_obj.save()
        apply_update(action_obj.act_id)

    def post(self, request):
        data = request.data
        act_ids = data.get("act_ids", [])
        filters = data.get("filters", {})
        pdca = data.get("pdca", {})
        comment = data.get("comment", "")
        dry_run = data.get("dry_run", False)
        qs = get_authorized_actions(request.user, filters)
        qs = qs.filter(act_id__in=act_ids)
        success = 0
        errors = []
        for act in qs:
            try:
                if not dry_run:
                    self.handle_action(act, pdca, comment)
                success += 1
            except Exception as exc:  # pragma: no cover
                errors.append({"act_id": act.act_id, "message": str(exc)})
        return Response({"total": len(act_ids), "success": success, "failed": len(errors), "errors": errors})


class BatchValidateView(_BatchBase):
    action_type = "validate"


class BatchCloseView(_BatchBase):
    action_type = "close"


class BatchRejectView(_BatchBase):
    action_type = "reject"


class SuggestFieldsView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        act_id = request.data.get("act_id")
        try:
            act = Action.objects.get(act_id=act_id)
        except Action.DoesNotExist:
            return Response(status=404)
        j = act.j
        if j is None and act.delais:
            j = (act.delais - act.date_creation).days if act.date_creation else None
        suggest = {
            "pdca": {"C": not act.c, "A": not act.a},
        }
        reasons = []
        if j is not None and j < 0:
            reasons.append("overdue")
        return Response({"act_id": act.act_id, "suggest": suggest, "reasons": reasons})


class ScheduleRemindersView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        role = request.user.profile.role
        if role not in [Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS]:
            return Response(status=403)
        payload = request.data
        name = f"reminder_{payload.get('plan') or 'all'}"
        automation, _ = Automation.objects.update_or_create(
            name=name,
            defaults={
                "trigger": Automation.Trigger.CRON,
                "cron": payload.get("cron", "0 7 * * 1-5"),
                "action": Automation.Action.NOTIFY_EMAIL,
                "filters": {"plan": payload.get("plan"), "only_overdue": True, "severity": payload.get("severity", "all")},
                "action_params": {"to": payload.get("to", []), "template_id": payload.get("template_id")},
            },
        )
        return Response({"id": automation.id, "name": automation.name})
