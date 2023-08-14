from django.apps import AppConfig
class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zense'

    def ready(self):
        from . import cron  # Import your cron file
        cron.MyCronJob().schedule()