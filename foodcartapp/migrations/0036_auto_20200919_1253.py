# Generated by Django 3.0.7 on 2020-09-19 12:53

from django.db import migrations


def fill_order_payment(apps, schema_editor):
    OrderProduct = apps.get_model('foodcartapp', 'OrderProduct')

    for product in OrderProduct.objects.all():
        payment = product.payment
        if not payment or payment <=0:
            price = product.product.price
            quantity = product.quantity
            product.payment = price * quantity
            product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0035_auto_20200919_0213'),
    ]

    operations = [
        migrations.RunPython(fill_order_payment),
    ]
