from django.apps import AppConfig


class PaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pa"

    def ready(self):
        from .scheduler import schedule_from_config

        try:
            schedule_from_config()
        except Exception:
            pass
