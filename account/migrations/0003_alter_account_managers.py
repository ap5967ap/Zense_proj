# Generated by Django 4.2.4 on 2023-08-09 20:44

import account.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_alter_account_managers"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="account",
            managers=[
                ("objects", account.models.MyAccountManager()),
            ],
        ),
    ]
