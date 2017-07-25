# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-25 22:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='email',
        ),
        migrations.RemoveField(
            model_name='player',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='player',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='player',
            name='username',
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.OneToOneField(default=123, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
