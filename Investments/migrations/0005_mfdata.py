# Generated by Django 4.2.4 on 2023-08-18 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "Investments",
            "0004_investment_fd_i_investment_mf_i_investment_sgb_i_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="MFData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("returns", models.DecimalField(decimal_places=2, max_digits=20)),
                ("rank", models.IntegerField()),
                (
                    "choice",
                    models.CharField(
                        choices=[("l", "l"), ("m", "m"), ("s", "s")], max_length=1
                    ),
                ),
            ],
        ),
    ]
