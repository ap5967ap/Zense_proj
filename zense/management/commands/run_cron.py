# myapp/management/commands/run_cron.py
from django.core.management.base import BaseCommand
from django_cron.management.commands.runcrons import Command as RunCronsCommand

class Command(BaseCommand):
    help = 'Run scheduled cron jobs'

    def handle(self, *args, **options):
        RunCronsCommand().handle()
