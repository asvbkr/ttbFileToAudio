# Generated by Django 3.0.7 on 2020-06-17 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djh_app', '0008_auto_20200616_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ttbdjchatavailable',
            name='permissions',
            field=models.TextField(verbose_name='permissions'),
        ),
    ]
