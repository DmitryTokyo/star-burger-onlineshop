# Generated by Django 3.2.8 on 2022-01-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0078_location_foodcartapp_restaur_ed2898_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='delivery_address',
            field=models.CharField(max_length=200, unique=True, verbose_name='адрес доставки'),
        ),
        migrations.AlterField(
            model_name='location',
            name='restaurant_address',
            field=models.CharField(max_length=200, unique=True, verbose_name='адрес ресторана'),
        ),
    ]
