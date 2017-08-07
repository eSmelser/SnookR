# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-25 23:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20170725_2240'),
        ('sublist', '0002_sublist_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='sublist',
            name='session',
            field=models.OneToOneField(default=123, on_delete=django.db.models.deletion.CASCADE, to='main.Session'),
            preserve_default=False,
        ),
    ]