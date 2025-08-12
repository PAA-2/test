from datetime import datetime, timedelta
from django.utils import timezone

from ..models import Automation, SyncJob
from .quality import run_quality_checks
from .sync import plan_sync
from .outlook_mail import send_mail, build_mail
from ..report_builder import build_pdf
from .template_render import render_template


def evaluate_trigger(automation: Automation):
    if automation.trigger == Automation.Trigger.SYNC_FAIL:
        return SyncJob.objects.filter(status=SyncJob.Status.FAIL).order_by("-created").first()
    if automation.trigger == Automation.Trigger.QUALITY_THRESHOLD:
        stats = run_quality_checks(None, automation.filters or {}, dry_run=True)
        sev = automation.condition.get("severity>=")
        count = automation.condition.get("count>=", 0)
        total = sum(v for k, v in stats.get("by_severity", {}).items() if k >= sev)
        if total >= count:
            return {"stats": stats}
    if automation.trigger == Automation.Trigger.ACTION_OVERDUE:
        # simple evaluation of overdue actions count
        from ..models import Action

        qs = Action.objects.filter(j__lt=0)
        if automation.filters.get("plan"):
            qs = qs.filter(plan_id=automation.filters["plan"])
        count = qs.count()
        threshold = automation.condition.get("count>=", 1)
        if count >= threshold:
            return {"count": count}
    return None


def execute_action(automation: Automation, payload):
    try:
        if automation.action == Automation.Action.NOTIFY_EMAIL:
            from ..models import Template

            template_id = automation.action_params.get("template_id")
            template = Template.objects.get(id=template_id)
            context = payload or {}
            rendered = render_template(template, context)
            mail = build_mail(
                to=automation.action_params.get("to", []),
                cc=automation.action_params.get("cc"),
                bcc=None,
                subject=rendered["subject"],
                body_html=rendered["body_html"],
                body_text=rendered["body_text"],
                attachments=None,
            )
            send_mail(mail, send=not automation.action_params.get("dry_run", False))
            return {"status": "OK", "message": "email sent"}
        if automation.action == Automation.Action.RUN_QUALITY:
            stats = run_quality_checks(None, automation.filters or {}, dry_run=False)
            return {"status": "OK", "message": str(stats)}
        if automation.action == Automation.Action.RUN_SYNC:
            from ..models import SyncConfig

            config = SyncConfig.objects.first()
            if config:
                plan_sync(config, dry_run=False)
            return {"status": "OK", "message": "sync triggered"}
        if automation.action == Automation.Action.EXPORT_REPORT:
            buf = build_pdf(title="Report", layout={}, data={})
            return {"status": "OK", "meta": {"size": buf.getbuffer().nbytes}}
    except Exception as exc:  # pragma: no cover
        return {"status": "FAIL", "message": str(exc)}
    return {"status": "SKIP", "message": "no action"}
