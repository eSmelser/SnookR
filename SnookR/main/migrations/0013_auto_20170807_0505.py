# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 05:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20170807_0451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sub',
            name='date',
            field=models.DateTimeField(auto_now=True, verbose_name='sub date'),
        ),
    ]
