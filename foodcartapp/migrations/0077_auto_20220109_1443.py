# Generated by Django 3.2.8 on 2022-01-09 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0076_location'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DeliveryLocation',
        ),
        migrations.DeleteModel(
            name='RestaurantLocation',
        ),
    ]
