from django.apps import AppConfig


class InvestmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Investments"
    def ready(self):
        from . import jobs
        jobs.start_scheduler()