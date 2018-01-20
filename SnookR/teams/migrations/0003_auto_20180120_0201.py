# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-20 02:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_auto_20180120_0159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='captain',
            name='division',
        ),
        migrations.RemoveField(
            model_name='captain',
            name='user',
        ),
        migrations.AlterField(
            model_name='team',
            name='captain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_teams', to='accounts.CustomUser'),
        ),
        migrations.DeleteModel(
            name='Captain',
        ),
    ]
