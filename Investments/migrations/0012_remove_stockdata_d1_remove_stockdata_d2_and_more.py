# Generated by Django 4.2.4 on 2023-08-20 22:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Investments", "0011_stockdata"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stockdata",
            name="d1",
        ),
        migrations.RemoveField(
            model_name="stockdata",
            name="d2",
        ),
        migrations.RemoveField(
            model_name="stockdata",
            name="d3",
        ),
        migrations.RemoveField(
            model_name="stockdata",
            name="d4",
        ),
        migrations.RemoveField(
            model_name="stockdata",
            name="d5",
        ),
        migrations.RemoveField(
            model_name="stockdata",
            name="dmax",
        ),
        migrations.RemoveField(
            model_name="stockdata",
            name="dmin",
        ),
    ]
