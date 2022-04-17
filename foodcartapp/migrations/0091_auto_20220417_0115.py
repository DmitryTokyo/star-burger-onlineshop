# Generated by Django 3.2.8 on 2022-04-17 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0090_alter_orderitem_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='delivery_address',
            field=models.CharField(max_length=200, verbose_name='адрес'),
        ),
        migrations.AlterField(
            model_name='location',
            name='delivery_lat',
            field=models.FloatField(blank=True, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='location',
            name='delivery_lon',
            field=models.FloatField(blank=True, null=True, verbose_name='долгота'),
        ),
        migrations.AlterField(
            model_name='location',
            name='restaurant_address',
            field=models.CharField(max_length=200, verbose_name='адрес'),
        ),
        migrations.AlterField(
            model_name='location',
            name='restaurant_lat',
            field=models.FloatField(blank=True, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='location',
            name='restaurant_lon',
            field=models.FloatField(blank=True, null=True, verbose_name='долгота'),
        ),
    ]
