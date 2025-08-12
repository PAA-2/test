from django.apps import AppConfig


class PaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pa"

    def ready(self):
        from .scheduler import schedule_from_config, schedule_quality_job

        try:
            schedule_from_config()
            schedule_quality_job()
        except Exception:
            pass
