# Generated by Django 3.2.8 on 2022-01-15 03:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0082_location_unique_couple_addresses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
    ]
