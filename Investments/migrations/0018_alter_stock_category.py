# Generated by Django 4.2.4 on 2023-08-21 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Investments", "0017_alter_stock_category_alter_stockdata_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="category",
            field=models.CharField(
                choices=[("l", "l"), ("m", "m"), ("s", "s")], max_length=100
            ),
        ),
    ]
