# Generated by Django 4.2.4 on 2023-08-28 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0006_expense_done_alter_expense_date_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="expense",
            name="done",
        ),
    ]
