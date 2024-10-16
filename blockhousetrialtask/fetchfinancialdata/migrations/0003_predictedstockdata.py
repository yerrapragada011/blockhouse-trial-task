# Generated by Django 4.2.16 on 2024-10-17 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fetchfinancialdata', '0002_stockdata_cash'),
    ]

    operations = [
        migrations.CreateModel(
            name='PredictedStockData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10)),
                ('date', models.DateField()),
                ('predicted_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
