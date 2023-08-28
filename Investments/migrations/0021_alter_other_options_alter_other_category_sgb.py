# Generated by Django 4.2.4 on 2023-08-27 22:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Investments", "0020_remove_investment_smallcase_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="other",
            options={"verbose_name": "FD", "verbose_name_plural": "FD"},
        ),
        migrations.AlterField(
            model_name="other",
            name="category",
            field=models.CharField(choices=[("FD", "FD")], max_length=100),
        ),
        migrations.CreateModel(
            name="SGB",
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
                ("price", models.DecimalField(decimal_places=2, max_digits=20)),
                ("buy_date", models.DateField()),
                ("duration", models.IntegerField(choices=[(5, 5), (8, 8), (11, 11)])),
                ("sell_date", models.DateField(blank=True, null=True)),
                (
                    "sell_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        default=0,
                        max_digits=20,
                        null=True,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
