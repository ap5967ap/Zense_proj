from django.apps import AppConfig


class InvestmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Investments"
    def ready(self):
        from . import jobs
        from . import stocks
        stocks.start_scheduler()
        from . import mutual_fund_data
        jobs.start_scheduler()
        mutual_fund_data.start_scheduler()