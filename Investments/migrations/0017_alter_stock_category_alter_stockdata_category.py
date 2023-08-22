# Generated by Django 4.2.4 on 2023-08-21 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Investments", "0016_stock_sell_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="category",
            field=models.CharField(
                choices=[("l", "Large Cap"), ("m", "Mid Cap"), ("s", "Small Cap")],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="stockdata",
            name="category",
            field=models.CharField(
                choices=[("l", "l"), ("m", "m"), ("s", "s"), ("n", "n")], max_length=100
            ),
        ),
    ]
