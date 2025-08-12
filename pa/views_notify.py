import logging
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Action, NotificationTemplate, Profile
from .permissions import RolePermission
from .services.outlook_mail import render_template, build_mail, send_mail, win32com

logger = logging.getLogger(__name__)


def get_authorized_actions(user, filters):
    qs = Action.objects.all()
    role = user.profile.role
    if role == Profile.Role.PILOTE:
        qs = qs.filter(plan__in=user.profile.plans_autorises.all())
    plan = filters.get("plan")
    responsable = filters.get("responsable")
    priorite = filters.get("priorite")
    q = filters.get("q")
    if plan:
        qs = qs.filter(plan_id=plan)
    if responsable:
        qs = qs.filter(responsables__username=responsable)
    if priorite:
        qs = qs.filter(priorite=priorite)
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(commentaire__icontains=q))
    return qs.distinct()


def serialize_actions_min(qs):
    data = []
    for act in qs:
        responsables = ", ".join(act.responsables.values_list("username", flat=True))
        data.append(
            {
                "act_id": act.act_id,
                "titre": act.titre,
                "responsables": responsables,
                "delais": act.delais.isoformat() if act.delais else "",
                "j": act.j,
            }
        )
    return data


def build_summary(qs, date_range=None):
    if date_range:
        start = date_range.get("from")
        end = date_range.get("to")
        if start and end:
            qs = qs.filter(date_creation__range=[start, end])
    return {
        "total": qs.count(),
        "cloturees": qs.filter(statut="Cloturee").count(),
        "en_retard": qs.filter(j__lt=0).count(),
        "en_cours": qs.filter(statut="En cours").count(),
    }


class BaseNotifyView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]

    def _check(self, request):
        if not settings.OUTLOOK_ENABLED or win32com is None:
            return Response({"detail": "Outlook indisponible sur cet hôte"}, status=503)
        if request.user.profile.role == Profile.Role.UTILISATEUR:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return None


class LateNotifyView(BaseNotifyView):
    def post(self, request):
        if (resp := self._check(request)) is not None:
            return resp
        data = request.data
        filters = data.get("filters", {})
        qs = get_authorized_actions(request.user, filters).filter(j__lt=0)
        actions = list(qs)
        serialized = serialize_actions_min(actions)
        count = len(actions)
        template_id = data.get("template_id")
        template = None
        if template_id:
            template = NotificationTemplate.objects.filter(id=template_id).first()
        else:
            template = NotificationTemplate.objects.filter(is_default=True).first()
        context = {"actions": serialized, "count": count, "user": request.user, "now": timezone.now()}
        subject = ""
        body_html = body_text = None
        if template:
            subject, body_html, body_text = render_template(template, context)
        dry_run = data.get("dry_run", False)
        log_payload = {"filters": filters, "to": data.get("to", []), "cc": data.get("cc", []), "bcc": data.get("bcc", []), "template_id": template_id, "dry_run": dry_run}
        if dry_run:
            logger.info("NOTIFY_LATE %s", {"payload": log_payload, "sent": False, "count": count})
            return Response({"preview": {"subject": subject, "body_html": body_html, "body_text": body_text}, "count": count})
        mail = build_mail(data.get("to", []), data.get("cc"), data.get("bcc"), subject, body_html, body_text, None)
        send_mail(mail, send=True)
        logger.info("NOTIFY_LATE %s", {"payload": log_payload, "sent": True, "count": count})
        return Response({"sent": True, "count": count})


class SummaryNotifyView(BaseNotifyView):
    def post(self, request):
        if (resp := self._check(request)) is not None:
            return resp
        data = request.data
        plan_id = data.get("plan")
        filters = {"plan": plan_id} if plan_id else {}
        qs = get_authorized_actions(request.user, filters)
        summary = build_summary(qs, data.get("range"))
        template_id = data.get("template_id")
        template = None
        if template_id:
            template = NotificationTemplate.objects.filter(id=template_id).first()
        else:
            template = NotificationTemplate.objects.filter(is_default=True).first()
        context = {"summary": summary, "user": request.user, "now": timezone.now()}
        subject = ""
        body_html = body_text = None
        if template:
            subject, body_html, body_text = render_template(template, context)
        dry_run = data.get("dry_run", False)
        log_payload = {"plan": plan_id, "to": data.get("to", []), "cc": data.get("cc", []), "template_id": template_id, "range": data.get("range"), "dry_run": dry_run}
        if dry_run:
            logger.info("NOTIFY_SUMMARY %s", {"payload": log_payload, "sent": False, "count": summary["total"]})
            return Response({"preview": {"subject": subject, "body_html": body_html, "body_text": body_text}, "count": summary["total"]})
        mail = build_mail(data.get("to", []), data.get("cc"), None, subject, body_html, body_text, None)
        send_mail(mail, send=True)
        logger.info("NOTIFY_SUMMARY %s", {"payload": log_payload, "sent": True, "count": summary["total"]})
        return Response({"sent": True, "count": summary["total"]})


class CustomNotifyView(BaseNotifyView):
    def post(self, request):
        if (resp := self._check(request)) is not None:
            return resp
        data = request.data
        to = data.get("to", [])
        subject = data.get("subject", "")
        body_html = data.get("body_html")
        body_text = data.get("body_text")
        attachments = data.get("attachments") or []
        dry_run = data.get("dry_run", False)
        log_payload = {"to": to, "cc": data.get("cc", []), "bcc": data.get("bcc", []), "subject": subject, "dry_run": dry_run}
        if dry_run:
            logger.info("NOTIFY_CUSTOM %s", {"payload": log_payload, "sent": False, "count": 0})
            return Response({"preview": {"subject": subject, "body_html": body_html, "body_text": body_text}, "count": 0})
        if not to:
            logger.info("NOTIFY_CUSTOM %s", {"payload": log_payload, "sent": False, "count": 0})
            return Response({"sent": False, "count": 0})
        mail = build_mail(to, data.get("cc"), data.get("bcc"), subject, body_html, body_text, attachments)
        send_mail(mail, send=True)
        logger.info("NOTIFY_CUSTOM %s", {"payload": log_payload, "sent": True, "count": 0})
        return Response({"sent": True, "count": 0})
