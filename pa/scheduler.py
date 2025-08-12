from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone

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


def schedule_from_config():
    scheduler.remove_all_jobs()
    config = SyncConfig.objects.first()
    if not config or not config.enabled:
        return
    trigger = CronTrigger.from_crontab(config.cron)
    scheduler.add_job(_run_sync, trigger, args=[config.id], id="plan-sync")
    scheduler.start()
