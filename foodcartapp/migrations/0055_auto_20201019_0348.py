# Generated by Django 3.0.7 on 2020-10-19 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_auto_20201019_0330'),
    ]

    operations = [
        migrations.RenameField(
            model_name='banner',
            old_name='banner_name',
            new_name='title',
        ),
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(upload_to='banners/', verbose_name='баннер'),
        ),
    ]
