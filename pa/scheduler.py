from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone

import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from .models import SyncConfig, SyncJob
from .services.sync import plan_sync
from .services.quality import run_quality_checks

logger = logging.getLogger(__name__)


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


def schedule_from_config():
    scheduler.remove_all_jobs()
    config = SyncConfig.objects.first()
    if not config or not config.enabled:
        return
    trigger = CronTrigger.from_crontab(config.cron)
    scheduler.add_job(_run_sync, trigger, args=[config.id], id="plan-sync")
    scheduler.start()


def _quality_job():
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        return
    stats = run_quality_checks(user, persist=True)
    thresh = settings.QUALITY_ALERT_THRESHOLD
    if (
        stats["by_severity"].get("CRITICAL", 0) >= thresh.get("CRITICAL", 999)
        or stats["by_severity"].get("HIGH", 0) >= thresh.get("HIGH", 999)
    ):
        logger.warning("QUALITY_ALERT", extra={"payload": stats})


def schedule_quality_job():
    trigger = CronTrigger.from_crontab(settings.QUALITY_DEFAULT_CRON)
    scheduler.add_job(_quality_job, trigger, id="quality-check")
