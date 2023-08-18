# Generated by Django 4.2.4 on 2023-08-18 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Investments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investment",
            name="FD",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="MF",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="SGB",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="SmallCase",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="large",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="mid",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="risky",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="safe",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="small",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="investment",
            name="trade",
            field=models.IntegerField(default=0),
        ),
    ]
