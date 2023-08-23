from django.apps import AppConfig


class ExpenseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "expense"
    def ready(self):
        from . import jobs  
        jobs.start_scheduler()