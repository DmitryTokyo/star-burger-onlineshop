# Generated by Django 3.0.7 on 2021-01-25 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0057_auto_20210125_0341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(upload_to='banners/', verbose_name='баннер'),
        ),
    ]