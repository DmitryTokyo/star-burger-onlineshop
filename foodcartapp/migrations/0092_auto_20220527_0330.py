# Generated by Django 3.2.8 on 2022-05-27 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0091_auto_20220417_0115'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='order',
            name='foodcartapp_order_s_70329f_idx',
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_status', 'create_time', 'call_time', 'delivery_time', 'phonenumber'], name='foodcartapp_order_s_a9c33f_idx'),
        ),
    ]