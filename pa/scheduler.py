from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from django.conf import settings

from django.utils import timezone
from .services.quality import run_quality_checks
from .services.outlook_mail import build_mail, send_mail

from .models import SyncConfig, SyncJob
from .services.sync import plan_sync


scheduler = BackgroundScheduler()


def _run_sync(config_id: int):
    config = SyncConfig.objects.get(id=config_id)
    stats = {}
    status = SyncJob.Status.OK
    try:
        stats = plan_sync(config)
    except Exception as exc:  # pragma: no cover - unexpected errors
        status = SyncJob.Status.FAIL
        SyncJob.objects.create(status=status, stats=stats, error=str(exc))
    else:
        SyncJob.objects.create(status=status, stats=stats)
    config.last_run = timezone.now()
    config.last_status = status
    config.save(update_fields=["last_run", "last_status"])




def _run_quality():
    stats = run_quality_checks(None, {})
    thresholds = getattr(settings, "QUALITY_ALERT_THRESHOLD", {})
    crit = stats["by_severity"].get("CRITICAL", 0)
    high = stats["by_severity"].get("HIGH", 0)
    if crit >= thresholds.get("CRITICAL", 0) or high >= thresholds.get("HIGH", 0):
        logging.getLogger(__name__).warning("QUALITY_ALERT", extra={"payload": stats})
        if settings.OUTLOOK_ENABLED:
            try:
                mail = build_mail([], None, None, "Data quality alert", str(stats), None, None)
                send_mail(mail)
            except Exception:
                pass

def schedule_from_config():
    scheduler.remove_all_jobs()
    config = SyncConfig.objects.first()
    if not config or not config.enabled:
        return
    trigger = CronTrigger.from_crontab(config.cron)
    scheduler.add_job(_run_sync, trigger, args=[config.id], id="plan-sync")
    q_trigger = CronTrigger.from_crontab(settings.QUALITY_DEFAULT_CRON)
    scheduler.add_job(_run_quality, q_trigger, id="quality-checks")
    scheduler.start()
